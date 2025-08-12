from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class LlmPlan:
    action: str
    subject: str
    payload: Dict[str, Any]
    await_response: bool
    response_subject: Optional[str] = None

    @staticmethod
    def from_json(obj: Dict[str, Any]) -> "LlmPlan":
        action = str(obj.get("action", "")).strip()
        if action != "send_request":
            raise ValueError("LlmPlan requires action=='send_request'")
        subject = str(obj.get("subject", "")).strip()
        payload = obj.get("payload", {}) or {}
        await_response = bool(obj.get("await_response", False))
        response_subject = obj.get("response_subject")
        if response_subject is not None:
            response_subject = str(response_subject).strip() or None
        if not subject or not isinstance(payload, dict):
            raise ValueError("Invalid LLM plan JSON")
        return LlmPlan(
            action=action,
            subject=subject,
            payload=payload,
            await_response=await_response,
            response_subject=response_subject,
        )

@dataclass
class FinalReply:
    result: Dict[str, Any]

    @staticmethod
    def from_json(obj: Dict[str, Any]) -> "FinalReply":
        action = str(obj.get("action", "")).strip()
        if action != "final_reply":
            raise ValueError("FinalReply requires action=='final_reply'")
        result = obj.get("result", {})
        if not isinstance(result, dict):
            raise ValueError("FinalReply.result must be an object")
        return FinalReply(result=result)
