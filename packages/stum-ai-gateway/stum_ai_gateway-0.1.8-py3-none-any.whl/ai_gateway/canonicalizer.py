from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional

@dataclass
class CanonicalizationResult:
    command: str
    args: Dict[str, Any]
    confidence: float

class LlmCanonicalizer:
    def __init__(
        self,
        llm_call: Callable[[str, Optional[str]], Awaitable[str]],
        min_confidence: float = 0.6,
        max_attempts: int = 1,
    ) -> None:
        self.llm_call = llm_call
        self.min_confidence = float(min_confidence)
        self.max_attempts = int(max_attempts)

    async def canonicalize(self, cmd: str, abilities, registry) -> Optional[CanonicalizationResult]:
        # Existing implementation you already have; leave as-is
        # Shown here as a placeholder for context.
        return None

    async def fill_required_args(
        self,
        *,
        command_text: str,
        mapping,            # CommandMapping
        current_args: Dict[str, Any],
        max_attempts: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Use the LLM to infer any missing required properties defined by mapping.request_schema.
        Returns a dict with only the inferred keys. If none can be inferred, returns {}.
        """
        max_attempts = int(self.max_attempts if max_attempts is None else max_attempts)
        schema = mapping.request_schema or {}
        required = list(schema.get("required", []))
        if not required:
            return {}

        missing = [k for k in required if k not in current_args]
        if not missing:
            return {}

        sys = (
            "You extract structured arguments from a short human command.\n"
            "Return ONLY a JSON object containing a subset of keys strictly from the provided 'required_keys'.\n"
            "If a value cannot be confidently inferred, return an empty JSON object {}.\n"
            "Normalize financial instrument symbols when applicable (e.g., prefer 'AAA/BBB' upper-case form for FX pairs).\n"
            "Do not include commentary or extra keys."
        )
        user = {
            "command_text": command_text,
            "current_args": current_args,
            "required_keys": missing,
            "request_schema": schema,
            "example_payload": mapping.example_payload or {},
            "notes": (
                "Infer only what is present or strongly implied in command_text. "
                "Respect JSON types in request_schema."
            ),
        }
        prompt = (
            "Extract the missing required keys.\n"
            f"{json.dumps(user, ensure_ascii=False)}\n"
            "Output only a JSON object."
        )

        last_err: Optional[str] = None
        for _ in range(max_attempts + 1):
            text = await self.llm_call(prompt, sys)
            try:
                obj = json.loads(self._first_json(text))
                # Keep only requested missing keys; drop anything else
                out = {k: obj[k] for k in missing if k in obj}
                # Basic type conformity: if schema specifies type string for key, coerce via str
                for k in list(out.keys()):
                    typ = (schema.get("properties", {}).get(k, {}) or {}).get("type")
                    if typ == "string" and not isinstance(out[k], str):
                        out[k] = str(out[k])
                return out
            except Exception as e:
                last_err = str(e)
                prompt = (
                    "Extract the missing required keys.\n"
                    f"{json.dumps(user, ensure_ascii=False)}\n"
                    "Reminder: Output ONLY a single JSON object with the missing keys. No comments."
                )
        return {}

    @staticmethod
    def _first_json(text: str) -> str:
        i = text.find("{")
        if i < 0:
            raise ValueError("no JSON object found")
        depth = 0
        for j in range(i, len(text)):
            ch = text[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[i : j + 1]
        raise ValueError("unterminated JSON")
