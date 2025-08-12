# ai_gateway/config.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Sequence

@dataclass(frozen=True)
class LlmAgentConfig:
    human_command_subject: str = "ai.human.commands"
    default_reply_subject: str = "ai.human.replies"
    compress_outbound: bool = True
    max_prompt_chars: int = 16000
    extra_response_subjects: Sequence[str] = field(default_factory=tuple)
    llm_postprocess_default: bool = False
    pending_timeout_seconds: int = 120
    llm_max_retries: int = 2

    # Iterative planning support
    llm_iterative_default: bool = True

    # NEW: canonicalization controls
    enable_canonicalization: bool = False
    canonicalization_min_confidence: float = 0.6
    canon_max_attempts: int = 1                 # new: cap extraction attempts
    ack_on_canon_failure: bool = True           # new: do not loop on missing fields

    # System prompts
    llm_system_prompt: str = (
        "You are an API planner. Output only one JSON object with keys: "
        "action, subject, payload, await_response, response_subject optional. No commentary."
    )
    llm_postprocess_system_prompt: str = (
        "You are a formatter. Output only JSON of shape {result:object}. Do not invent data."
    )
    llm_iterative_system_prompt: str = (
        "You are an API planner operating in a loop (plan → act → observe). "
        "You must output only one JSON object. Use:\n"
        "- {\"action\":\"send_request\",\"subject\":str,\"payload\":object,"
        "\"await_response\":bool,\"response_subject\"?:str} to call a service; or\n"
        "- {\"action\":\"final_reply\",\"result\":object} to end the workflow."
    )
