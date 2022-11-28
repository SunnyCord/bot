from __future__ import annotations

import os


def list_module(directory) -> list[str]:
    return (f for f in os.listdir(directory) if f.endswith(".py"))
