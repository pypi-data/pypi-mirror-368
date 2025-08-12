from __future__ import annotations
from typing import Awaitable, Callable, Optional

LlmCallback = Callable[[str, Optional[str]], Awaitable[str]]
