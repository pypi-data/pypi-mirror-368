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
                "name": a.name,
                "request_subject": a.request_subject,
                "response_subject": a.response_subject,
                "payload_schema": a.payload_schema or {},
                "example_payload": a.example_payload or {},
                "description": a.description,
            }
        return out
