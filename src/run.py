###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import sentry_sdk
from discord.ext.commands import Context
from sentry_sdk.tracing import Transaction

from classes.bot import Sunny

bot = Sunny()
sample_rate = 1.0 if bot.config.environment == "development" else 0.2

sentry_sdk.init(
    dsn=bot.config.sentry,
    environment=bot.config.environment,
    traces_sample_rate=1.0,
    profiles_sample_rate=sample_rate,
)


@bot.before_invoke
async def before_invoke(ctx: Context) -> None:
    transaction = Transaction(
        name=ctx.command.qualified_name,
        op="command",
    )
    transaction.set_context(
        "user",
        {
            "id": ctx.author.id,
            "username": ctx.author.name,
        },
    )
    transaction.set_tag("guild", ctx.guild.id)
    transaction.set_tag("channel", ctx.channel.id)
    ctx.transaction = sentry_sdk.start_transaction(transaction)


@bot.after_invoke
async def after_invoke(ctx: Context) -> None:
    ctx.transaction.set_status("ok")
    ctx.transaction.finish()


if __name__ == "__main__":
    bot.run(reconnect=True)
