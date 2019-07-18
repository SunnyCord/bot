import asyncio, sys, traceback, os, discord, sentry_sdk
from discord.ext import commands
import config as cfg
from commons import mongoIO

def get_config():
    if cfg.DEBUG==True:
        return cfg.debugConf
    else:
        return cfg.conf

def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""
    if mongoIO.isBlacklisted(message.author) or not message.guild:
        return ' '
    guildPref = mongoIO.getSetting(message.guild.id, 'prefix') if message.guild else None
    return guildPref if guildPref is not None else bot.configs.PREFIXES

def list_module(directory):
    return (f for f in os.listdir(directory) if f.endswith('.py'))

sentry_sdk.init(cfg.SENTRY)

class Sunny(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(
            description=kwargs.pop("description"),
            command_prefix=kwargs.pop("command_prefix"),
            activity=kwargs.pop("activity")
        )
        self.configs=get_config()

    async def on_ready(self):
        print(r"""
  .--.--.
 /  /    '.
|  :  /`. /          ,--,      ,---,      ,---,
;  |  |--`         ,'_ /|  ,-+-. /  | ,-+-. /  |
|  :  ;_      .--. |  | : ,--.'|'   |,--.'|'   |     .--,
 \  \    `. ,'_ /| :  . ||   |  ,"' |   |  ,"' |   /_ ./|
  `----.   \|  ' | |  . .|   | /  | |   | /  | |, ' , ' :
  __ \  \  ||  | ' |  | ||   | |  | |   | |  | /___/ \: |
 /  /`--'  /:  | : ;  ; ||   | |  |/|   | |  |/ .  \  ' |
'--'.     / '  :  `--'   \   | |--' |   | |--'   \  ;   :
  `--'---'  :  ,      .-./   |/     |   |/        \  \  ;
             `--`----'   '---'      '---'          :  \  \
                                                    \  ' ;
                                                     `--`
        """)
        print(f'\n\nLogged in as: {self.user.name} - {self.user.id}\nVersion: {discord.__version__}\n')
        print(f'Successfully logged in and booted...!')

        #Load Listeners
        for extension in list_module('listeners'):
            try:
                self.load_extension('listeners.' + os.path.splitext(extension)[0])
            except Exception:
                print(f'Failed to load listener {extension}.', file=sys.stderr)
                traceback.print_exc()

        #Load Extensions
        for extension in list_module('cogs'):
            try:
                self.load_extension('cogs.' + os.path.splitext(extension)[0])
            except Exception:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

    async def on_guild_join(self, guild):
        mongoIO.addServer(guild)

async def run():

    bot = Sunny(command_prefix=get_prefix, description='Sunny Bot', activity=discord.Streaming(name='Nice Aesthetics', type=1, url='https://www.twitch.tv/niceaesthetic'))
    bot.load_extension("jishaku")
    bot.remove_command('help')

    await bot.start(bot.configs.TOKEN, bot=True, reconnect=True)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        print("Stopping bot!")
