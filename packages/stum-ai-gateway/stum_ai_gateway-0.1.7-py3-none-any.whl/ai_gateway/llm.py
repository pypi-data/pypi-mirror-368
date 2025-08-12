from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
import json
import re
import logging

log = logging.getLogger(__name__)

class LLMClient(ABC):
    @abstractmethod
    async def complete(self, prompt: str, system: Optional[str] = None) -> str:
        ...

class EchoLLM(LLMClient):
    # Simple stub for tests; echoes a plan that forwards the human command as payload
    async def complete(self, prompt: str, system: Optional[str] = None) -> str:
        plan = {"action": "send_request", "subject": "noop.req", "payload": {"echo": prompt}, "await_response": False}
        return json.dumps(plan)

class JsonExtractor:
    @staticmethod
    def extract_first_json_block(text: str) -> str:
        # Try strict parse first
        try:
            json.loads(text)
            return text
        except Exception:
            pass
        # Fallback: find first {...} block
        m = re.search(r"\{(?:[^{}]|(?R))*\}", text, re.DOTALL)
        if not m:
            raise ValueError("No JSON object found in LLM output")
        return m.group(0)
