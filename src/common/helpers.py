from __future__ import annotations

import os
from typing import TYPE_CHECKING

from common.regex import beatmap_id_rx
from common.regex import beatmap_link_rx

if TYPE_CHECKING:
    from typing import Generator


def list_module(directory: str) -> Generator[str, None, None]:
    return (f for f in os.listdir(directory) if f.endswith(".py"))


def get_beatmap_from_text(
    text: str,
    disallow_plain_id: bool = False,
) -> dict[str, int | None]:
    ids: dict[str, int | None] = {
        "beatmap_id": None,
        "beatmapset_id": None,
    }
    result_link = beatmap_link_rx.match(text)
    if result_link is None:
        if not disallow_plain_id:
            result_id = beatmap_id_rx.match(text)
            if result_id is not None:
                ids["beatmap_id"] = int(result_id.group("bmapid"))

        return ids

    if result_link.group("bmapsetid2") is not None:
        ids["beatmapset_id"] = int(result_link.group("bmapsetid2"))
        if result_link.group("bmapid2") is not None:
            ids["beatmap_id"] = int(result_link.group("bmapid2"))

    elif result_link.group("bmapid1") is not None:
        ids["beatmap_id"] = int(result_link.group("bmapid1"))

    else:
        ids["beatmapset_id"] = int(result_link.group("bmapset1"))

    return ids
