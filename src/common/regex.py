###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import re

beatmap_id_rx = re.compile(r"^(?P<bmapid>[0-9]+)$")
beatmap_link_rx = re.compile(
    r"(https?)://(?P<domain>osu|lazer)\.ppy\.sh/(b(eatmaps)?/(?P<bmapid1>[0-9]+)|s/(?P<bmapsetid1>[0-9]+)|beatmapsets/(?P<bmapsetid2>[0-9]+)(#(?P<mode>[a-z]+)/(?P<bmapid2>[0-9]+))?)",
)
user_link_rx = re.compile(
    r"(https?)://(?P<domain>osu|lazer)\.ppy\.sh/u(sers)?/(?P<userid>[0-9]+)",
)
alphanumeric_rx = re.compile(r"[^a-zA-Z0-9]")
