import os, time
from git import Repo
from discord.ext import commands


class OwnerCog(commands.Cog, command_attrs=dict(hidden=True), name="Owner"):
    """Commands meant for the owner only."""

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def pull(self, ctx) -> None:
        """Pulls the bot from GitHub."""
        start_t = time.perf_counter()
        message = ""
        repo = Repo(path=os.getcwd())
        for fetch_info in repo.remotes.origin.pull():
            message += f"\n Updated base '{fetch_info.ref}' To '{fetch_info.commit}'"
        for submodule in repo.submodules:
            submodule.update(init=True)
            message += f"\n Updated '{submodule}'"
        end_t = time.perf_counter()
        delta_t = end_t - start_t
        await ctx.send(
            f"Operation completed succesfully in {delta_t:.2f}s. Output: ```prolog\n{message}\n```"
        )

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx) -> None:
        """Shuts the bot down."""
        await ctx.send("Goodbye!")
        await self.bot.close()

    @commands.command(aliases=["pr"])
    @commands.is_owner()
    async def pull_reload(self, ctx) -> None:
        await ctx.invoke(self.pull)
        await ctx.invoke(self.shutdown)


async def setup(bot) -> None:
    await bot.add_cog(OwnerCog(bot))
