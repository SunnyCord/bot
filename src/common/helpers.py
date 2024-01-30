###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from common.regex import beatmap_id_rx
from common.regex import beatmap_link_rx
from common.regex import user_link_rx

if TYPE_CHECKING:
    from discord import MessageReference


def get_beatmap_from_text(
    text: str,
    disallow_plain_id: bool = False,
) -> dict[str, int | None]:
    beatmap_data = {
        "beatmap_id": None,
        "beatmapset_id": None,
    }

    if not disallow_plain_id:
        result_id = beatmap_id_rx.match(text)
        if result_id is not None:
            beatmap_data["beatmap_id"] = int(result_id.group("bmapid"))
            return beatmap_data

    result_link = beatmap_link_rx.search(text)
    if result_link is None:
        return beatmap_data

    if result_link.group("bmapsetid2") is not None:
        beatmap_data["beatmapset_id"] = int(result_link.group("bmapsetid2"))
        if result_link.group("bmapid2") is not None:
            beatmap_data["beatmap_id"] = int(result_link.group("bmapid2"))
    elif result_link.group("bmapid1") is not None:
        beatmap_data["beatmap_id"] = int(result_link.group("bmapid1"))
    else:
        beatmap_data["beatmapset_id"] = int(result_link.group("bmapsetid1"))

    return beatmap_data


def get_beatmap_from_reference(reference: MessageReference) -> dict[str, int | None]:
    beatmap_query = reference.resolved.content

    first_embed = next(
        (embed for embed in reference.resolved.embeds if embed.type == "rich"),
        None,
    )

    if first_embed is not None:
        beatmap_query += (
            f"{first_embed.url} {first_embed.title} {first_embed.description} {first_embed.footer.text} "
            + " ".join(field.value for field in first_embed.fields)
        )

    return get_beatmap_from_text(beatmap_query)


def get_user_from_text(text):
    if match := user_link_rx.match(text):
        lazer = match.group("domain") == "lazer"
        return match.group("userid")
    return None


async def get_bot_version():
    import aiohttp

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.github.com/repos/SunnyCord/bot/commits/master",
            ) as resp:
                data = await resp.json()
                return f"sunny{data['commit']['author']['date'].split('T')[0].replace('-', '.')}"
    except Exception:
        return "sunny?.?.?"
