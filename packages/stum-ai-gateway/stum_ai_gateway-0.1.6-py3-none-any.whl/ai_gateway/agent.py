from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set
from uuid import uuid4

from jsonschema import validate as jsonschema_validate, ValidationError

from natbus.client import NatsBus
from natbus.message import BusMessage, ReceivedMessage

from .config import LlmAgentConfig
from .registry import CommandRegistry, CommandMapping
from .schemas import LlmPlan, FinalReply
from .abilities import AbilityCatalog
from .canonicalizer import LlmCanonicalizer  # intent canonicalizer

log = logging.getLogger(__name__)


class CanonicalizationError(Exception):
    pass


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
    • Canonicalization: free text → known command; schema-guided arg completion before planning
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

        # Intent canonicalizer (command mapping)
        self._canonicalizer: Optional[LlmCanonicalizer] = None
        if getattr(self.cfg, "enable_canonicalization", True):
            self._canonicalizer = LlmCanonicalizer(
                llm_call=self.llm_call,
                min_confidence=getattr(self.cfg, "canonicalization_min_confidence", 0.6),
            )

    # -------------------------------------------------------------------------
    async def start(self) -> None:
        if self._started:
            return
        self._started = True

        await self.bus.push_subscribe(
            self.cfg.human_command_subject,
            handler=self._on_human_command,
            durable="ai-gateway-human",
            queue="ai-gateway",
        )

        subjects = set(self.registry.all_response_subjects())
        subjects.update(getattr(self.cfg, "extra_response_subjects", ()) or ())
        for ability in self.abilities.as_contract().values():
            resp = ability.get("response_subject")
            if resp:
                subjects.add(resp)

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
        ttl = getattr(self.cfg, "pending_timeout_seconds", 60.0)
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

        raw_cmd_text = str(payload.get("cmd", "")).strip()
        cmd_lc = raw_cmd_text.lower()
        args = payload.get("args", {}) or {}
        reply_subject = str(payload.get("reply_subject") or self.cfg.default_reply_subject)
        correlation_id = rm.correlation_id or rm.trace_id or str(uuid4())

        mapping = self.registry.get(cmd_lc)
        effective_cmd = cmd_lc
        effective_args = dict(args)

        # -------- Intent canonicalization (maps to a registered command) --------
        if not mapping and self._canonicalizer is not None:
            try:
                canon = await self._canonicalizer.canonicalize(cmd_lc, self.abilities, self.registry)
            except Exception as e:
                log.warning("canonicalize error: %s", e)
                canon = None

            if canon is not None and float(getattr(canon, "confidence", 0.0) or 0.0) >= float(
                getattr(self.cfg, "canonicalization_min_confidence", 0.6)
            ):
                m2 = self.registry.get(canon.command)
                if m2 is None:
                    await self._reply_json(
                        reply_subject, {"error": "unknown_command", "cmd": raw_cmd_text}, rm, corr_id=correlation_id
                    )
                    await rm.ack()
                    return
                mapping = m2
                effective_cmd = canon.command.strip().lower()
                for k, v in (getattr(canon, "args", {}) or {}).items():
                    effective_args.setdefault(k, v)
            else:
                await self._reply_json(
                    reply_subject, {"error": "unknown_command", "cmd": raw_cmd_text}, rm, corr_id=correlation_id
                )
                await rm.ack()
                return

        if not mapping:
            await self._reply_json(
                reply_subject, {"error": "unknown_command", "cmd": raw_cmd_text}, rm, corr_id=correlation_id
            )
            await rm.ack()
            return

        # -------- Schema-guided argument completion BEFORE planning --------
        try:
            effective_args = await self._canonicalize_args(raw_cmd_text, effective_args, mapping)
        except CanonicalizationError as e:
            await self._reply_json(
                reply_subject, {"error": "canonicalization_failed", "detail": str(e)}, rm, corr_id=correlation_id
            )
            # default: ack on canon failure to avoid CPU loops
            if not getattr(self.cfg, "ack_on_canon_failure", True):
                log.debug("ack_on_canon_failure=False, but requeue is not implemented; acknowledging")
            await rm.ack()
            return

        # -------- Plan --------
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
                iterative = mapping.llm_iterative if mapping.llm_iterative is not None else getattr(
                    self.cfg, "llm_iterative_default", True
                )
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
    # Schema-guided argument canonicalization (fills required fields before planning)
    # -------------------------------------------------------------------------
    async def _canonicalize_args(self, cmd_text: str, raw_args: Dict[str, Any], mapping: CommandMapping) -> Dict[str, Any]:
        schema = mapping.request_schema
        if not getattr(self.cfg, "enable_canonicalization", True) or not schema:
            # still normalize obvious fields
            args = dict(raw_args or {})
            self._normalize_fx_fields(cmd_text, args)
            return args

        args = dict(raw_args or {})
        # 1) deterministic normalization
        self._normalize_fx_fields(cmd_text, args)

        # 2) satisfied?
        if self._satisfies_schema(args, schema):
            return args

        # 3) single bounded LLM extraction pass (configurable)
        attempts = max(1, int(getattr(self.cfg, "canon_max_attempts", 1)))
        for _ in range(attempts):
            extracted = await self._schema_guided_extract(cmd_text, args, schema)
            if isinstance(extracted, dict):
                args.update(extracted)
                # normalize once more (e.g., "AUD/USD" → "AUDUSD")
                self._normalize_fx_fields(cmd_text, args)
            if self._satisfies_schema(args, schema):
                return args

        # 4) fail fast (prevents iterative loops)
        required = list(schema.get("required") or [])
        missing = [k for k in required if k not in args or args[k] in (None, "", [])]
        raise CanonicalizationError(f"missing required fields: {missing} for command '{mapping.command}'")

    def _normalize_fx_fields(self, cmd_text: Optional[str], args: Dict[str, Any]) -> None:
        # Normalize FX symbol:
        #  - prefer provided args.symbol
        #  - accept args.pair and coerce to 6-letter
        #  - fallback: mine from free-text (AUDUSD, AUD/USD, AUD USD)
        sym = str(args.get("symbol") or "").upper().replace("/", "").strip()
        if len(sym) == 6 and sym.isalpha():
            args["symbol"] = sym
            return

        pair = str(args.get("pair") or "").upper().replace("/", "").strip()
        if len(pair) == 6 and pair.isalpha():
            args["symbol"] = pair
            return

        t = (cmd_text or "").upper()
        m = re.search(r'\b([A-Z]{3})[\/\s]?([A-Z]{3})\b', t)
        if m:
            args["symbol"] = m.group(1) + m.group(2)

    async def _schema_guided_extract(self, cmd_text: str, known_args: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        system = "Extract and complete required arguments for a trading command. Output strictly valid JSON only."
        prompt = (
            "User text:\n"
            f"{cmd_text}\n\n"
            "Known arguments (may be incomplete):\n"
            f"{json.dumps(known_args)}\n\n"
            "Produce a JSON object that satisfies this JSON Schema. "
            "Only include keys defined by the schema. Do not include explanations.\n"
            f"Schema:\n{json.dumps(schema)}"
        )
        # reuse JSON helper to enforce single-object output
        obj = await self._llm_json(system=system, prompt=prompt, required_keys=None, max_retries=1)
        return obj if isinstance(obj, dict) else {}

    def _satisfies_schema(self, args: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        req = schema.get("required") or []
        for k in req:
            if k not in args or args[k] in (None, "", []):
                return False
        props = schema.get("properties") or {}
        for k, spec in props.items():
            if k in args and isinstance(spec, dict):
                pat = spec.get("pattern")
                if pat and isinstance(args[k], str):
                    if re.fullmatch(pat, args[k]) is None:
                        return False
        return True

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
            compress=getattr(self.cfg, "compress_outbound", False),
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
            compress=getattr(self.cfg, "compress_outbound", False),
        )
        await self.bus.publish(msg)

    # -------------------------------------------------------------------------
    # LLM orchestration + prompts
    # -------------------------------------------------------------------------
    async def _llm_plan(self, cmd: str, args: dict, mapping: CommandMapping) -> LlmPlan:
        prompt = self._build_plan_prompt(cmd, args, mapping)
        obj = await self._llm_json(
            system=getattr(self.cfg, "llm_system_prompt", ""),
            prompt=prompt,
            required_keys={"action"},
            max_retries=getattr(self.cfg, "llm_max_retries", 2),
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
            system=getattr(self.cfg, "llm_iterative_system_prompt", ""),
            prompt=prompt,
            required_keys={"action"},
            max_retries=getattr(self.cfg, "llm_max_retries", 2),
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
        if len(prompt) > getattr(self.cfg, "max_prompt_chars", 12000):
            prompt = prompt[: getattr(self.cfg, "max_prompt_chars", 12000)]

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
