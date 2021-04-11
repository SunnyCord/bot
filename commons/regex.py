import re

id_rx = re.compile(r'[^0-9]')
url_rx = re.compile(r'https?://(?:www\.)?.+')
beatmap_id_rx = re.compile(r"^(?P<bmapid>[0-9]+)$")
beatmap_link_rx = re.compile(r"(https?):\/\/([-\w._]+)(\/[-\w._]\?(.+)?)?(\/b(eatmaps)?\/(?P<bmapid1>[0-9]+)|\/s\/(?P<bmapsetid1>[0-9]+)|\/beatmapsets\/(?P<bmapsetid2>[0-9]+)(#(?P<mode>[a-z]+)\/(?P<bmapid2>[0-9]+))?)")
track_title_rx = re.compile(r"\([^()]*\)")