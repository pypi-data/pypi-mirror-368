from __future__ import annotations

def _summarize_commands(registry) -> str:
    items = []
    if hasattr(registry, "values"):
        items = list(registry.values())
    elif hasattr(registry, "_by_command"):
        items = list(registry._by_command.values())  # type: ignore[attr-defined]
    elif hasattr(registry, "list_commands"):
        items = [registry.get(c) for c in registry.list_commands()]  # type: ignore
        items = [m for m in items if m]
    lines = []
    for m in items:
        lines.append(
            f'- name: "{m.command}" -> request="{m.request_subject}"'
            + (f', response="{m.response_subject}"' if m.response_subject else "")
            + (f'  # {m.llm_instructions}' if m.llm_instructions else "")
        )
    return "\n".join(lines) if lines else "(none registered)"

def _summarize_abilities(abilities) -> str:
    cats = abilities.as_contract() if hasattr(abilities, "as_contract") else {}
    lines = []
    for ab in cats.values():
        lines.append(
            f'- {ab.get("name","")} : request="{ab.get("request_subject","")}", '
            f'response="{ab.get("response_subject","")}"  # {ab.get("description","")}'
        )
    return "\n".join(lines) if lines else "(none declared)"

def build_command_router_system(abilities, registry) -> str:
    return (
f"""You are a strict command router. Your task is to read a free-form user message and map it to ONE of the known commands below, or 'unknown' if none fits. 
If you map to a command, also extract well-formed 'args' for that command. 
Output ONLY strict JSON in this schema:
{{
  "command": "<exact name from the list, or 'unknown'>",
  "args": <object with extracted arguments or {{}}>,
  "confidence": <float 0..1 summarizing your certainty>
}}

## Known commands
{_summarize_commands(registry)}

## Abilities (tools the agent can call during planning)
{_summarize_abilities(abilities)}

### Guidance
- Prefer commands that would lead to calling appropriate abilities (e.g., market data then place trade).
- If the user mentions a forex pair, normalize to upper-case XXX/YYY (e.g., "audusd" -> "AUD/USD").
- If unsure, return "unknown" with low confidence.
"""
    )
