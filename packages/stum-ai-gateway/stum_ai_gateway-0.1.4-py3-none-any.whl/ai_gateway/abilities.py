from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class Ability:
    name: str
    request_subject: str
    response_subject: Optional[str] = None
    payload_schema: Optional[Dict[str, Any]] = None
    description: str = ""
    example_payload: Optional[Dict[str, Any]] = None

class AbilityCatalog:
    def __init__(self) -> None:
        self._by_name: dict[str, Ability] = {}
        self._by_subject: dict[str, Ability] = {}

    def register(self, ability: Ability) -> None:
        key = ability.name.strip().lower()
        self._by_name[key] = ability
        self._by_subject[ability.request_subject] = ability

    def get_by_name(self, name: str) -> Optional[Ability]:
        return self._by_name.get(name.strip().lower())

    def get_by_subject(self, subject: str) -> Optional[Ability]:
        return self._by_subject.get(subject)

    def as_contract(self) -> dict:
        # Compact, machine-consumable description for prompts
        out = {}
        for k, a in self._by_name.items():
            out[k] = {
                "request_subject": a.request_subject,
                "response_subject": a.response_subject,
                "payload_schema": a.payload_schema or {},
                "example_payload": a.example_payload or {},
                "description": a.description,
            }
        return out


"""
Short version
CommandMapping = human intent → default routing + prompting.
Ability = machine capability contract (subjects + JSON schema) used for planning/validation.

Details

Purpose
• CommandMapping: Binds a user-facing command string to a default request_subject/response_subject, adds per-command instructions, iterative flag, and optional examples. Drives the first plan and the human reply route.
• Ability: Describes what the platform can do regardless of phrasing. Each ability defines request_subject, response_subject, payload_schema, and an example. Feeds the LLM’s “toolbox” and enforces schema validation on any plan that targets that subject.

Scope
• CommandMapping: Per intent (“show active trades”, “place forex trade”). Many mappings can reuse the same underlying service.
• Ability: Global catalog of callable actions across services; reused by many commands and by iterative steps.

Prompting role
• CommandMapping: Supplies context and command-specific llm_instructions for the first LLM call; can set llm_iterative and llm_postprocess.
• Ability: Injected into every plan/iterate prompt as the allowed operations with parameter specs; lets the LLM choose valid subjects and produce valid payloads.

Routing
• CommandMapping: Provides the default response_subject for the initial request and the human reply subject (from the incoming message).
• Ability: Provides canonical response_subjects so the agent can pre-/auto-subscribe and so iterative plans can introduce new subjects safely.

Validation
• CommandMapping: May include a request_schema just for that command’s initial call (optional).
• Ability: Owns the authoritative payload_schema per subject; agent validates every plan (initial and iterative) against the ability schema.

Change surface
• Add a new human phrasing → add/modify a CommandMapping.
• Add/modify a platform action (new service/field/rule) → add/modify an Ability (schema, subjects, example).
• Tighten constraints → update Ability schema; all commands benefit automatically.

Runtime behavior
• Initial step: CommandMapping guides the first request; Ability validates the payload.
• Iterative steps: The LLM can select any Ability (e.g., fetch snapshot, then trade) without adding new CommandMappings; schemas still validate.
• Dynamic subscription: If an Ability’s response_subject wasn’t pre-known, the agent subscribes on demand when a plan references it.

Example
• Commands: “show active trades”, “what positions are open?”, “list open trades” → three CommandMappings, all default to forex.trades.list.req/.resp.
• Abilities: get_market_snapshot, get_account_info, place_trade → three reusable, schema-defined capabilities that any command (or iterative step) can call.

Bottom line
Use CommandMapping to translate human language into an initial, constrained plan and reply path. Use Abilities to declare the system’s callable operations with strict schemas, enabling safe planning, iteration, and evolution without rewriting commands.
"""

"""
Command
Single user-facing command that kicks off an iterative plan:

python
Copy
Edit
from ai_gateway import CommandRegistry, CommandMapping

registry = CommandRegistry()

registry.register(CommandMapping(
    command="should we trade audusd",
    request_subject="forex.market.snapshot.req",     # default first call
    response_subject="forex.market.snapshot.resp",
    llm_instructions=(
        "Decide using plan→act→observe. "
        "If symbol not in args, use 'AUD/USD'. "
        "Step 1: get_market_snapshot. "
        "Optionally fetch account/positions if needed. "
        "If spread < threshold and risk allows, place market order 10k with IOC; else final_reply with reason."
    ),
    llm_iterative=True,   # enables multi-step loop
))
Abilities
Machine capability catalog used for planning and validation. At minimum:

python
Copy
Edit
from ai_gateway.abilities import Ability, AbilityCatalog

abilities = AbilityCatalog()

abilities.register(Ability(
    name="get_market_snapshot",
    request_subject="forex.market.snapshot.req",
    response_subject="forex.market.snapshot.resp",
    description="Latest bid/ask/last for a forex symbol",
    payload_schema={
        "type": "object",
        "required": ["symbol"],
        "additionalProperties": False,
        "properties": {"symbol": {"type": "string", "pattern": "^[A-Z]{3}/[A-Z]{3}$"}}
    },
    example_payload={"symbol": "AUD/USD"},
))

abilities.register(Ability(
    name="get_account_info",
    request_subject="forex.account.info.req",
    response_subject="forex.account.info.resp",
    description="Balances, margin, buying power",
    payload_schema={"type": "object", "additionalProperties": False, "properties": {}},
    example_payload={},
))

abilities.register(Ability(
    name="get_open_positions",
    request_subject="forex.positions.list.req",
    response_subject="forex.positions.list.resp",
    description="Current open positions (size, avg price)",
    payload_schema={"type": "object", "additionalProperties": False, "properties": {}},
    example_payload={},
))

abilities.register(Ability(
    name="place_trade",
    request_subject="forex.trade.place.req",
    response_subject="forex.trade.place.resp",
    description="Submit a new order",
    payload_schema={
        "type": "object",
        "required": ["symbol", "side", "qty", "order_type", "time_in_force", "client_order_id"],
        "additionalProperties": False,
        "properties": {
            "symbol": {"type": "string", "pattern": "^[A-Z]{3}/[A-Z]{3}$"},
            "side": {"type": "string", "enum": ["buy", "sell"]},
            "qty": {"type": "number", "exclusiveMinimum": 0},
            "order_type": {"type": "string", "enum": ["market", "limit", "stop"]},
            "limit_price": {"type": "number"},
            "stop_price": {"type": "number"},
            "time_in_force": {"type": "string", "enum": ["GTC", "IOC", "FOK"]},
            "client_order_id": {"type": "string", "minLength": 1},
            "tags": {"type": "array", "items": {"type": "string"}}
        },
        "allOf": [
            {"if": {"properties": {"order_type": {"const": "limit"}}}, "then": {"required": ["limit_price"]}},
            {"if": {"properties": {"order_type": {"const": "stop"}}}, "then": {"required": ["stop_price"]}}
        ]
    },
    example_payload={
        "symbol": "AUD/USD", "side": "buy", "qty": 10000,
        "order_type": "market", "time_in_force": "IOC", "client_order_id": "cli-123"
    },
))
How the loop executes

Human sends “should we trade audusd”.

Agent calls LLM with mapping context + full abilities.as_contract().

LLM emits a send_request to forex.market.snapshot.req with {"symbol":"AUD/USD"} and await_response=true.

Agent publishes; on response, agent calls LLM again with Observation (bid/ask, etc.).

LLM either:
• emits another send_request (e.g., forex.account.info.req or forex.positions.list.req) and waits, or
• emits a send_request to forex.trade.place.req with a payload validated by the Place Trade schema, or
• emits {"action":"final_reply","result":{...}} to end with reasons not to trade.

Example LLM outputs (happy path)
First plan:

json
Copy
Edit
{
  "action": "send_request",
  "subject": "forex.market.snapshot.req",
  "payload": {"symbol": "AUD/USD"},
  "await_response": true,
  "response_subject": "forex.market.snapshot.resp"
}
After snapshot observation:

json
Copy
Edit
{
  "action": "send_request",
  "subject": "forex.account.info.req",
  "payload": {},
  "await_response": true,
  "response_subject": "forex.account.info.resp"
}
After account info observation (decision to trade):

json
Copy
Edit
{
  "action": "send_request",
  "subject": "forex.trade.place.req",
  "payload": {
    "symbol": "AUD/USD",
    "side": "buy",
    "qty": 10000,
    "order_type": "market",
    "time_in_force": "IOC",
    "client_order_id": "audusd-mkt-001"
  },
  "await_response": true,
  "response_subject": "forex.trade.place.resp"
}
Final reply after trade ack:

json
Copy
Edit
{
  "action": "final_reply",
  "result": {"decision": "trade_placed", "order_id": "O1", "symbol": "AUD/USD"}
}
Example LLM outputs (no-trade)
After snapshot:

json
Copy
Edit
{"action":"final_reply","result":{"decision":"no_trade","reason":"spread>1 pip"}}
Why both layers
CommandMapping drives the first step and ties the user phrasing to an initial default route and reply path.
Abilities provide the toolbox with strict JSON Schemas so the LLM can legally choose subsequent actions (fetch data, inspect account, place trade).
The agent validates every payload against the Ability schema and dynamically subscribes to any new response_subject referenced by the plan.

"""