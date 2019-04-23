import discord
from discord.ext import commands
import config as cfg 

#https://gist.github.com/StudioMFTechnologies/ad41bfd32b2379ccffe90b0e34128b8b

def get_config():
    if cfg.DEBUG==True:
        return cfg.debugConf
    else:
        return cfg.conf

class Help(commands.Cog):
    """Displays the message you are currently viewing!"""
    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(add_reactions=True,embed_links=True)
    async def help(self,ctx,*cog):
        """Gets all cogs and commands of mine."""
        if not cog:
            helpEmbed=discord.Embed(title='Available Cogs',
                            description=f'Use `{ctx.prefix}help *cog*` to find out more about them!', color=get_config().COLOR)
            cogs_desc = ''
            for x in self.bot.cogs:
                cogs_desc += f'**{x}** - {self.bot.cogs[x].__doc__}\n'
            helpEmbed.add_field(name='\u200b', value=cogs_desc[0:len(cogs_desc)-1] if cogs_desc[0:len(cogs_desc)-1] else '\u200b',inline=False)
            await ctx.message.add_reaction(emoji='✉')
            await ctx.message.author.send(embed=helpEmbed)
        else:
            if len(cog) > 1:
                helpEmbed = discord.Embed(title='Error!',description='That is way too many cogs!',color=discord.Color.red())
                await ctx.message.author.send(embed=helpEmbed)
            else:
                found = False
                for x in self.bot.cogs:
                    for y in cog:
                        if x == y:
                            helpEmbed=discord.Embed(title=f'{cog[0]} Commands',description=self.bot.cogs[cog[0]].__doc__, color=get_config().COLOR)
                            for c in self.bot.get_cog(y).get_commands():
                                if not c.hidden:
                                    helpEmbed.add_field(name=c.name,value=c.help,inline=False)
                            found = True
                if not found:
                    helpEmbed = discord.Embed(title='Error!',description=f'Cog "{cog[0]}" does not exist! Maybe check your spelling?',color=discord.Color.red())
                else:
                    await ctx.message.add_reaction(emoji='✉')
                await ctx.message.author.send(embed=helpEmbed)

def setup(bot):
    bot.add_cog(Help(bot))