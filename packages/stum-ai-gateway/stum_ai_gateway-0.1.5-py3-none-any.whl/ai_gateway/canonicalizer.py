from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Optional, Callable, Awaitable

from .prompts_router import build_command_router_system
from .callbacks import LlmCallback

@dataclass
class CanonicalizationResult:
    command: str
    args: dict
    confidence: float

class LlmCanonicalizer:
    def __init__(self, llm_call: LlmCallback, min_confidence: float = 0.6):
        self.llm_call = llm_call
        self.min_confidence = min_confidence

    async def canonicalize(self, text: str, abilities, registry) -> Optional[CanonicalizationResult]:
        system = build_command_router_system(abilities, registry)
        raw = await self.llm_call(text, system)
        try:
            obj = json.loads(raw)
        except Exception:
            return None
        cmd = obj.get("command")
        args = obj.get("args", {}) or {}
        conf = float(obj.get("confidence", 0.0) or 0.0)
        if not isinstance(cmd, str):
            return None
        if cmd.lower() == "unknown" or conf < self.min_confidence:
            return None
        return CanonicalizationResult(command=cmd, args=args, confidence=conf)
