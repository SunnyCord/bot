###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from datetime import timedelta


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


def seconds_to_long_text(secs: int) -> str:
    if secs == 0:
        return "0 seconds"

    time_units = [
        ("day", secs // 86400),
        ("hour", (secs // 3600) % 24),
        ("minute", (secs // 60) % 60),
        ("second", secs % 60),
    ]

    formatted_units = [
        f"{value} {unit}s" if value != 1 else f"{value} {unit}"
        for unit, value in time_units
        if value > 0
    ]

    return (
        " ".join(formatted_units[:-1]) + " and " + formatted_units[-1]
        if len(formatted_units) > 1
        else formatted_units[0]
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
