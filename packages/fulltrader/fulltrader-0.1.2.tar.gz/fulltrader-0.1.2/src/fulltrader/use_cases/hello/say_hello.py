from __future__ import annotations

from typing import Optional


def say_hello(name: Optional[str] = None) -> str:
    target_name = name or "FullTrader"
    return f"Hello, {target_name}!"


