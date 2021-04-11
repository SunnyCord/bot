import discord
import datetime
import classes.osu as osu

def getDiffEmoji(sr:float, mode:int):
    if sr<2:
        return osu.BeatmapIcon[f"EASY_{mode}"]
    if sr<2.7:
        return osu.BeatmapIcon[f"NORMAL_{mode}"]
    if sr<4:
        return osu.BeatmapIcon[f"HARD_{mode}"]
    if sr<5.3:
        return osu.BeatmapIcon[f"INSANE_{mode}"]
    if sr<6.5:
        return osu.BeatmapIcon[f"EXTRA_{mode}"]
    return osu.BeatmapIcon[f"EXPERT_{mode}"]

class BeatmapEmbed(discord.Embed):
    def __init__(self, beatmap:osu.Beatmap, color: str):
        lengthHumanReadable = datetime.timedelta(seconds=beatmap.total_length)
        footerDate = "Last updated" if not beatmap.approved_date else "Approved"
        date=beatmap.last_update if not beatmap.approved_date else beatmap.approved_date
        datetimeObject=datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        super().__init__(
            title=f"{beatmap.artist} - {beatmap.title}",
            color = color,
            description=f"**Length:** {lengthHumanReadable} **BPM:** {str(beatmap.bpm).rstrip('0').rstrip('.')}\n**Download:** [map](https://osu.ppy.sh/d/{beatmap.beatmapset_id})([🚫📹](https://osu.ppy.sh/d/{beatmap.beatmapset_id}n)) [chimu.moe](https://api.chimu.moe/v1/download/{beatmap.beatmapset_id})\n**Discussion:** [mapset](https://osu.ppy.sh/beatmapsets/{beatmap.beatmapset_id}/discussion) [difficulty](https://osu.ppy.sh/beatmapsets/{beatmap.beatmapset_id}/discussion/{beatmap.beatmap_id}/general)",
            url=f"https://osu.ppy.sh/b/{beatmap.beatmap_id}",
            timestamp=datetimeObject
        )
        self.set_author(name=f"Mapped by {beatmap.creator}", icon_url=f"https://a.ppy.sh/{beatmap.creator_id}", url=f"https://osu.ppy.sh/users/{beatmap.creator_id}/modding")
        self.set_thumbnail(url=f"https://b.ppy.sh/thumb/{beatmap.beatmapset_id}.jpg")
        self.set_footer(text=f"{beatmap.status.name} | ❤️ {beatmap.favourite_count} | ▶️ {beatmap.playcount} | {footerDate}")
        self.add_field(name=f"{getDiffEmoji(beatmap.difficultyrating, int(beatmap.mode)).value}__{beatmap.version}__", value=f"**▸** {round(beatmap.difficultyrating, 2)}⭐  **▸Max Combo:** x{beatmap.max_combo}\n**▸AR:** {beatmap.diff_approach}  **▸OD:** {beatmap.diff_overall}  **▸CS:** {beatmap.diff_size}  **▸HP:** {beatmap.diff_drain}")