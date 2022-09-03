from __future__ import annotations

import discord
from discord.ext import commands


class Help(commands.Cog):
    """
    Displays the message you are currently viewing!
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def help(self, ctx, *cog):
        """Gets all cogs and commands of mine."""
        if not cog:
            helpEmbed = discord.Embed(
                title="Available Cogs",
                description=f"Use `{ctx.prefix}help *cog*` to find out more about them!",
                color=self.bot.config.color,
            )
            cogs_desc = ""
            for x in self.bot.cogs:
                cogs_desc += f"**{x}** {self.bot.cogs[x].__doc__}\n"
            helpEmbed.add_field(
                name="\u200b",
                value=cogs_desc[0 : len(cogs_desc) - 1]
                if cogs_desc[0 : len(cogs_desc) - 1]
                else "\u200b",
                inline=False,
            )
            await ctx.message.add_reaction("✉")
            await ctx.author.send(embed=helpEmbed)
        else:
            if len(cog) > 1:
                helpEmbed = discord.Embed(
                    title="Error!",
                    description="That is way too many cogs!",
                    color=discord.Color.red(),
                )
                await ctx.author.send(embed=helpEmbed)
            else:
                found = False
                for x in self.bot.cogs:
                    for y in cog:
                        if x == y:
                            helpEmbed = discord.Embed(
                                title=f"{cog[0]} Commands",
                                description=self.bot.cogs[cog[0]].__doc__,
                                color=self.bot.config.color,
                            )
                            for c in self.bot.get_cog(y).get_commands():
                                if not c.hidden:
                                    helpEmbed.add_field(
                                        name=c.name,
                                        value=c.help,
                                        inline=False,
                                    )
                            found = True
                if not found:
                    helpEmbed = discord.Embed(
                        title="Error!",
                        description=f'Cog "{cog[0]}" does not exist! Maybe check your spelling?',
                        color=discord.Color.red(),
                    )
                else:
                    await ctx.message.add_reaction("✉")
                await ctx.author.send(embed=helpEmbed)


async def setup(bot):
    await bot.add_cog(Help(bot))
