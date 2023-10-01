###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import datetime
import math
from io import BytesIO

import matplotlib as mpl
import matplotlib.dates as mdates
import numpy
from aiosu.models import User

mpl.use("Agg")
import matplotlib.pyplot as plt


def compute_ticks(x) -> list[int]:
    x_max, x_min = math.ceil(max(x)), math.floor(min(x))
    if x_max == x_min:
        return [x_max]
    if x_min + 1 == x_max:
        return [x_min, x_max]
    return [x_min, (x_min + x_max) // 2, x_max]


def plot_rank_graph(user: User) -> BytesIO:
    plt.rcParams.update(
        {
            "xtick.color": "#9A9A9A",
            "ytick.color": "#9A9A9A",
            "savefig.pad_inches": 0,
        },
    )

    rank_history_data = user.rank_history.data

    base = datetime.datetime.today()
    dates = [base - datetime.timedelta(days=x) for x in range(len(rank_history_data))]
    x_ticks = mdates.drange(dates[-1], base, datetime.timedelta(days=15))
    x_ticks = numpy.append(x_ticks, mdates.date2num(base))
    fig = plt.figure(figsize=(4, 0.75), dpi=100)

    ax = fig.add_subplot(111)
    ax.grid()
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.plot(dates, rank_history_data[::-1], "g")
    ax.set_ylim(ax.get_ylim()[::-1])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    plt.xticks(x_ticks)
    plt.yticks(compute_ticks(rank_history_data))
    ax.tick_params(axis="both", which="major", labelsize=8)
    ax.tick_params(axis="both", which="minor", labelsize=5)
    plt.tight_layout(pad=0)

    buf = BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    buf.seek(0)

    return buf
