from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Any

@dataclass(frozen=True)
class CommandMapping:
    command: str
    request_subject: str
    response_subject: Optional[str] = None
    llm_instructions: str = ""
    llm_postprocess: bool = False
    request_schema: Optional[Dict[str, Any]] = None
    example_payload: Optional[Dict[str, Any]] = None
    llm_iterative: bool = True  # enable iterative mode for this command

class CommandRegistry:
    def __init__(self) -> None:
        self._by_command: Dict[str, CommandMapping] = {}
        self._response_subjects: Dict[str, List[str]] = {}

    def register(self, mapping: CommandMapping) -> None:
        key = mapping.command.strip().lower()
        self._by_command[key] = mapping
        if mapping.response_subject:
            self._response_subjects.setdefault(mapping.response_subject, []).append(key)

    def get(self, command: str) -> Optional[CommandMapping]:
        return self._by_command.get(command.strip().lower())

    def list_commands(self) -> Iterable[str]:
        return list(self._by_command.keys())

    def all_response_subjects(self) -> Sequence[str]:
        return list(self._response_subjects.keys())
