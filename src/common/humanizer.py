###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from datetime import timedelta

from thefuzz import fuzz

from common.regex import alphanumeric_rx

FUZZY_MATCH_THRESHOLD = 80
FUZZY_MATCH_THRESHOLD_LOW = 35


__all__ = (
    "fuzzy_string_match",
    "milliseconds_to_duration",
    "number",
    "ordinal",
    "seconds_to_text",
    "song_title_match",
)


def ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix


def number(n: float) -> str:
    n = float(f"{n:.3g}")
    magnitude = 0
    while abs(n) >= 1000:
        magnitude += 1
        n /= 1000.0
    return "{}{}".format(
        f"{n:f}".rstrip("0").rstrip("."),
        ["", "k", "m", "b", "t"][magnitude],
    )


def seconds_to_text(secs: int) -> str:
    if secs == 0:
        return "0 seconds"

    time_units = [
        ("d", secs // 86400),
        ("h", (secs // 3600) % 24),
        ("m", (secs // 60) % 60),
        ("s", secs % 60),
    ]

    formatted_units = [f"{value}{unit}" for unit, value in time_units if value > 0]

    return " ".join(formatted_units)


def milliseconds_to_duration(position: float) -> str:
    return str(timedelta(milliseconds=position)).split(".")[0].zfill(8)


def fuzzy_string_match(str1: str, str2: str, permit_low_match: bool = False) -> bool:
    THRESHOLD = FUZZY_MATCH_THRESHOLD_LOW if permit_low_match else FUZZY_MATCH_THRESHOLD
    return fuzz.ratio(str1.casefold(), str2.casefold()) >= THRESHOLD


def song_title_match(guess: str, answer: str) -> bool:
    banned_word_combos = [
        "tv size",
        "cut ver",
        "full ver",
        "short ver",
        "op ver",
        "ed ver",
        "extended ver",
        "sped up ver",
        "sped up",
    ]

    alphanumeric = alphanumeric_rx.split(answer)[0]
    minimum_words_required = 2 if len(answer.split(" ")) > 2 else 1
    guess_length = max(len(alphanumeric.split(" ")), minimum_words_required)

    for combo in banned_word_combos:
        if fuzzy_string_match(guess, combo):
            return False

    partial_words_start = " ".join(answer.split(" ")[:guess_length])
    partial_words_end = " ".join(answer.split(" ")[-guess_length:])
    partial_words_start_alphanumeric = " ".join(alphanumeric.split(" ")[:guess_length])
    partial_words_end_alphanumeric = " ".join(alphanumeric.split(" ")[-guess_length:])
    return (
        fuzzy_string_match(guess, answer)
        or fuzzy_string_match(guess, alphanumeric)
        or fuzzy_string_match(guess, partial_words_start)
        or fuzzy_string_match(guess, partial_words_end)
        or fuzzy_string_match(guess, partial_words_start_alphanumeric)
        or fuzzy_string_match(guess, partial_words_end_alphanumeric)
    )
