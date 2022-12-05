from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Generator


def list_module(directory: str) -> Generator[str, None, None]:
    return (f for f in os.listdir(directory) if f.endswith(".py"))
