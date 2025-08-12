from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Dict, Optional, Set
from uuid import uuid4

from jsonschema import validate as jsonschema_validate, ValidationError

from natbus.client import NatsBus
from natbus.message import BusMessage, ReceivedMessage

from .config import LlmAgentConfig
from .registry import CommandRegistry, CommandMapping
from .schemas import LlmPlan, FinalReply
from .abilities import AbilityCatalog
from .canonicalizer import LlmCanonicalizer  # NEW

log = logging.getLogger(__name__)

@dataclass
class PendingRequest:
    reply_subject: str
    original_command: str
    mapping: CommandMapping
    iterative: bool  # re-plan after observations when True

class LlmNatbusAgent:
    """
    NatBus ↔ LLM planner/actor.

    • Accepts human commands on cfg.human_command_subject
    • Calls injected llm_call(prompt, system) to obtain a plan (JSON)
    • Publishes service requests per plan; tracks correlation for responses
    • Iterative mode: after each observation, calls LLM again to decide next step or finalize
    • Validates plan payloads against mapping/ability JSON Schemas when provided
    • If a human cmd is unknown, optionally uses LLM canonicalizer to map free-form → known command.
    """

    def __init__(
        self,
        bus: NatsBus,
        llm_call,
        registry: CommandRegistry,
        cfg: Optional[LlmAgentConfig] = None,
        abilities: Optional[AbilityCatalog] = None,
    ):
        self.bus = bus
        self.llm_call = llm_call  # async: (prompt: str, system: Optional[str]) -> str
        self.registry = registry
        self.cfg = cfg or LlmAgentConfig()
        self.abilities = abilities or AbilityCatalog()

        self._pending: Dict[str, PendingRequest] = {}
        self._pending_ts: Dict[str, float] = {}
        self._started = False
        self._gc_task: Optional[asyncio.Task] = None

        self._resp_subscribed: Set[str] = set()

        # NEW: canonicalizer
        self._canonicalizer: Optional[LlmCanonicalizer] = None
        if self.cfg.enable_canonicalization:
            self._canonicalizer = LlmCanonicalizer(
                llm_call=self.llm_call,
                min_confidence=self.cfg.canonicalization_min_confidence,
            )

    # -------------------------------------------------------------------------
    async def start(self) -> None:
        if self._started: return
        self._started = True

        await self.bus.push_subscribe(
            self.cfg.human_command_subject,
            handler=self._on_human_command,
            durable="ai-gateway-human",
            queue="ai-gateway",
        )

        subjects = set(self.registry.all_response_subjects())
        subjects.update(self.cfg.extra_response_subjects or ())
        for ability in self.abilities.as_contract().values():
            resp = ability.get("response_subject")
            if resp: subjects.add(resp)

        for subj in subjects:
            await self._ensure_response_subscribed(subj)

        self._gc_task = asyncio.create_task(self._gc_pending_loop())

    async def close(self) -> None:
        if self._gc_task:
            self._gc_task.cancel()
            try:
                await self._gc_task
            except asyncio.CancelledError:
                pass
        self._started = False

    async def _gc_pending_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(5)
                self._expire_pending()
        except asyncio.CancelledError:
            return

    def _expire_pending(self) -> None:
        if not self._pending:
            return
        now = asyncio.get_event_loop().time()
        ttl = self.cfg.pending_timeout_seconds
        expired = [cid for cid, ts in self._pending_ts.items() if now - ts > ttl]
        for cid in expired:
            ctx = self._pending.pop(cid, None)
            self._pending_ts.pop(cid, None)
            if ctx:
                log.warning("Expired pending request correlation_id=%s command=%s", cid, ctx.original_command)

    @staticmethod
    def _sanitize(s: str) -> str:
        return s.replace(".", "-").replace("*", "star").replace(">", "gt")

    async def _ensure_response_subscribed(self, subject: Optional[str]) -> None:
        if not subject or subject in self._resp_subscribed:
            return
        await self.bus.push_subscribe(
            subject,
            handler=self._on_service_response,
            durable=f"ai-gateway-resp-{self._sanitize(subject)}",
            queue="ai-gateway",
        )
        self._resp_subscribed.add(subject)

    # -------------------------------------------------------------------------
    async def _on_human_command(self, rm: ReceivedMessage) -> None:
        try:
            payload = rm.as_json()
        except Exception as e:
            log.error("Invalid human command JSON: %s", e)
            await rm.ack()
            return

        cmd = str(payload.get("cmd", "")).strip().lower()
        args = payload.get("args", {}) or {}
        reply_subject = str(payload.get("reply_subject") or self.cfg.default_reply_subject)
        correlation_id = rm.correlation_id or rm.trace_id or str(uuid4())

        mapping = self.registry.get(cmd)
        effective_cmd = cmd
        effective_args = dict(args)

        # -------- Canonicalization gate (STRICT) --------
        if not mapping and self.cfg.enable_canonicalization:
            try:
                canon = await self._canonicalizer.canonicalize(cmd, self.abilities, self.registry)
            except Exception as e:
                log.warning("canonicalize error: %s", e)
                canon = None

            if canon is not None:
                conf = float(getattr(canon, "confidence", 0.0) or 0.0)
                if conf >= float(self.cfg.canonicalization_min_confidence):
                    m2 = self.registry.get(canon.command)
                    if m2 is None:
                        # Canonicalized to an unknown command → treat as unknown
                        await self._reply_json(
                            reply_subject, {"error": "unknown_command", "cmd": cmd}, rm, corr_id=correlation_id
                        )
                        await rm.ack()
                        return
                    mapping = m2
                    effective_cmd = canon.command.strip().lower()
                    for k, v in (getattr(canon, "args", {}) or {}).items():
                        effective_args.setdefault(k, v)
                else:
                    # BELOW THRESHOLD → do NOT call planner
                    await self._reply_json(
                        reply_subject, {"error": "unknown_command", "cmd": cmd}, rm, corr_id=correlation_id
                    )
                    await rm.ack()
                    return
            else:
                # No canonicalization candidate → unknown
                await self._reply_json(
                    reply_subject, {"error": "unknown_command", "cmd": cmd}, rm, corr_id=correlation_id
                )
                await rm.ack()
                return
        # -------- /gate --------

        if not mapping:
            await self._reply_json(
                reply_subject, {"error": "unknown_command", "cmd": cmd}, rm, corr_id=correlation_id
            )
            await rm.ack()
            return

        # Plan using effective command/args
        try:
            plan = await self._llm_plan(effective_cmd, effective_args, mapping)
        except Exception as e:
            await self._reply_json(
                reply_subject, {"error": "invalid_llm_output", "detail": str(e)}, rm, corr_id=correlation_id
            )
            await rm.ack()
            return

        if plan.action != "send_request":
            await self._reply_json(
                reply_subject, {"error": "unsupported_action", "action": plan.action}, rm, corr_id=correlation_id
            )
            await rm.ack()
            return

        await self._publish_service_request(plan, correlation_id, effective_cmd)

        if plan.await_response:
            resp_subject = plan.response_subject or mapping.response_subject
            if not resp_subject:
                await self._reply_json(
                    reply_subject, {"error": "no_response_subject_configured"}, rm, corr_id=correlation_id
                )
            else:
                await self._ensure_response_subscribed(resp_subject)
                iterative = mapping.llm_iterative if mapping.llm_iterative is not None else self.cfg.llm_iterative_default
                self._pending[correlation_id] = PendingRequest(
                    reply_subject=reply_subject,
                    original_command=effective_cmd,
                    mapping=mapping,
                    iterative=iterative,
                )
                self._pending_ts[correlation_id] = asyncio.get_event_loop().time()
        else:
            await self._reply_json(
                reply_subject,
                {"status": "sent", "subject": plan.subject, "correlation_id": correlation_id},
                rm,
                corr_id=correlation_id,
            )

        await rm.ack()

    async def _on_service_response(self, rm: ReceivedMessage) -> None:
        correlation_id = rm.correlation_id or ""
        ctx = self._pending.get(correlation_id)
        if not ctx:
            await rm.ack()
            return

        try:
            observation = rm.as_json()
        except Exception:
            observation = {"raw": rm.as_text()}

        if ctx.iterative:
            try:
                decision = await self._llm_iterate(ctx.original_command, observation)
            except Exception as e:
                await self._reply_json(
                    ctx.reply_subject,
                    {
                        "correlation_id": correlation_id,
                        "command": ctx.original_command,
                        "data": observation,
                        "note": f"iteration_error: {e}",
                    },
                    rm,
                    corr_id=correlation_id,
                )
                self._pending.pop(correlation_id, None)
                self._pending_ts.pop(correlation_id, None)
                await rm.ack()
                return

            if isinstance(decision, LlmPlan) and decision.action == "send_request":
                await self._publish_service_request(decision, correlation_id, ctx.original_command)
                if decision.await_response:
                    next_resp = decision.response_subject or ctx.mapping.response_subject
                    await self._ensure_response_subscribed(next_resp)
                    self._pending_ts[correlation_id] = asyncio.get_event_loop().time()
                    await rm.ack()
                    return
                await self._reply_json(
                    ctx.reply_subject,
                    {"status": "sent", "subject": decision.subject, "correlation_id": correlation_id},
                    rm,
                    corr_id=correlation_id,
                )
                self._pending.pop(correlation_id, None)
                self._pending_ts.pop(correlation_id, None)
                await rm.ack()
                return

            if isinstance(decision, FinalReply):
                await self._reply_json(
                    ctx.reply_subject,
                    {"correlation_id": correlation_id, "command": ctx.original_command, "data": decision.result},
                    rm,
                    corr_id=correlation_id,
                )
                self._pending.pop(correlation_id, None)
                self._pending_ts.pop(correlation_id, None)
                await rm.ack()
                return

            await self._reply_json(
                ctx.reply_subject,
                {"correlation_id": correlation_id, "command": ctx.original_command, "data": observation},
                rm,
                corr_id=correlation_id,
            )
            self._pending.pop(correlation_id, None)
            self._pending_ts.pop(correlation_id, None)
            await rm.ack()
            return

        await self._reply_json(
            ctx.reply_subject,
            {"correlation_id": correlation_id, "command": ctx.original_command, "data": observation},
            rm,
            corr_id=correlation_id,
        )
        self._pending.pop(correlation_id, None)
        self._pending_ts.pop(correlation_id, None)
        await rm.ack()

    # -------------------------------------------------------------------------
    async def _publish_service_request(self, plan: LlmPlan, correlation_id: str, origin_cmd: str) -> None:
        ability = self.abilities.get_by_subject(plan.subject)
        if ability and ability.payload_schema:
            self._validate_payload(plan.payload, ability.payload_schema)

        msg = BusMessage.from_json(
            plan.subject,
            plan.payload,
            sender="ai-gateway",
            correlation_id=correlation_id,
            headers={"x-origin-cmd": origin_cmd},
            ensure_trace=True,
            compress=self.cfg.compress_outbound,
        )
        await self.bus.publish(msg)

    def _validate_payload(self, payload: dict, schema: dict) -> None:
        try:
            jsonschema_validate(payload, schema)
        except ValidationError as e:
            path = "/".join(map(str, e.path)) or "<root>"
            raise ValueError(f"payload schema validation failed: {e.message} at {path}")

    async def _reply_json(
        self,
        subject: str,
        obj: dict,
        rm: Optional[ReceivedMessage],
        corr_id: Optional[str] = None,
    ) -> None:
        corr = corr_id or (rm.correlation_id if rm else None)
        msg = BusMessage.from_json(
            subject,
            obj,
            sender="ai-gateway",
            correlation_id=corr,
            ensure_trace=True,
            compress=self.cfg.compress_outbound,
        )
        await self.bus.publish(msg)

    # -------------------------------------------------------------------------
    # LLM orchestration + prompts
    # -------------------------------------------------------------------------
    async def _llm_plan(self, cmd: str, args: dict, mapping: CommandMapping) -> LlmPlan:
        prompt = self._build_plan_prompt(cmd, args, mapping)
        obj = await self._llm_json(
            system=self.cfg.llm_system_prompt,
            prompt=prompt,
            required_keys={"action"},
            max_retries=self.cfg.llm_max_retries,
        )
        if str(obj.get("action")) == "final_reply":
            raise ValueError("Planner returned final_reply on first step; expected send_request")

        if mapping.request_schema and obj.get("subject") == mapping.request_subject:
            self._validate_payload(obj.get("payload", {}), mapping.request_schema)

        ability = self.abilities.get_by_subject(str(obj.get("subject", "")))
        if ability and ability.payload_schema:
            self._validate_payload(obj.get("payload", {}), ability.payload_schema)

        return LlmPlan.from_json(obj)

    async def _llm_iterate(self, original_command: str, observation: dict):
        prompt = self._build_iterative_prompt(original_command, observation)
        obj = await self._llm_json(
            system=self.cfg.llm_iterative_system_prompt,
            prompt=prompt,
            required_keys={"action"},
            max_retries=self.cfg.llm_max_retries,
        )
        action = str(obj.get("action"))
        if action == "send_request":
            ability = self.abilities.get_by_subject(str(obj.get("subject", "")))
            if ability and ability.payload_schema:
                self._validate_payload(obj.get("payload", {}), ability.payload_schema)
            return LlmPlan.from_json(obj)
        if action == "final_reply":
            return FinalReply.from_json(obj)
        raise ValueError(f"Unknown action in iterative decision: {action}")

    async def _llm_json(
        self,
        *,
        system: str,
        prompt: str,
        required_keys: Optional[Set[str]] = None,
        max_retries: int = 2,
    ) -> dict:
        if len(prompt) > self.cfg.max_prompt_chars:
            prompt = prompt[: self.cfg.max_prompt_chars]

        last_error: Optional[str] = None
        for _ in range(max_retries + 1):
            text = await self.llm_call(prompt, system)
            try:
                obj = json.loads(self._extract_first_json(text))
                if required_keys and not required_keys.issubset(set(obj.keys())):
                    missing = sorted(list(required_keys - set(obj.keys())))
                    raise ValueError(f"missing keys: {', '.join(missing)}")
                return obj
            except Exception as e:
                last_error = str(e)
                prompt += "\nReminder: Output only a single valid JSON object per the schema. No commentary."

        raise RuntimeError(f"LLM did not return valid JSON after retries: {last_error}")

    def _build_plan_prompt(self, cmd: str, args: dict, mapping: CommandMapping) -> str:
        contract = {
            "request_subject": mapping.request_subject,
            "response_subject": mapping.response_subject,
            "payload_schema": mapping.request_schema or {},
            "example_payload": mapping.example_payload or {},
        }
        abilities = self.abilities.as_contract()
        instructions = mapping.llm_instructions or ""
        context = {
            "command": cmd,
            "args": args,
            "default_request_subject": mapping.request_subject,
            "default_response_subject": mapping.response_subject,
        }
        return (
            "You are planning the FIRST action for a task. Output only one JSON object.\n"
            "Allowed keys: action, subject, payload, await_response, response_subject (optional).\n"
            f"Abilities: {json.dumps(abilities, ensure_ascii=False)}\n"
            f"Contract: {json.dumps(contract, ensure_ascii=False)}\n"
            "Rules:\n"
            "- subject MUST be one of the abilities' request_subjects or the contract request_subject.\n"
            "- payload MUST satisfy the payload_schema when provided.\n"
            "- Set await_response true for calls with response_subject.\n"
            f"Additional instructions: {instructions}\n"
            f"Context: {json.dumps(context, ensure_ascii=False)}"
        )

    def _build_iterative_prompt(self, original_command: str, observation: dict) -> str:
        abilities = self.abilities.as_contract()
        return (
            "Plan next step based on the latest observation. If you have enough information to conclude for the human, "
            'return {"action":"final_reply","result":{...}}; otherwise return a {"action":"send_request",...}.\n'
            f"Abilities: {json.dumps(abilities, ensure_ascii=False)}\n"
            f"Original command: {original_command}\n"
            f"Observation: {json.dumps(observation, ensure_ascii=False)}"
        )

    @staticmethod
    def _extract_first_json(text: str) -> str:
        start = text.find("{")
        if start == -1:
            raise ValueError("No JSON object found in LLM output")
        depth = 0
        for i in range(start, len(text)):
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
        raise ValueError("Unterminated JSON object in LLM output")
