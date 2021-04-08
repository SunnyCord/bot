from classes.bot import Sunny
import asyncio, sys, traceback, os, discord, pyfiglet

bot = Sunny (
        description='Sunny Bot', activity=discord.Streaming (
                                name='Nice Aesthetics', type=1, url='https://www.twitch.tv/niceaesth'
                            )
    )

try:
    import sentry_sdk
    sentry_sdk.init(bot.config.sentry)
except ImportError:
    print("[SENTRY] Failed to initialize sentry.")

def list_module(directory):
    return (f for f in os.listdir(directory) if f.endswith('.py'))

@bot.listen('on_ready')
async def on_ready():
        f = pyfiglet.Figlet()
        print(f.renderText(bot.config.splashArt))
        print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
        print(f'Successfully logged in and booted...!')

        #Load Modules
        module_folders = ['listeners', 'cogs', 'tasks']
        for module in module_folders:
            for extension in list_module(module):
                try:
                    bot.load_extension(f'{module}.{os.path.splitext(extension)[0]}')
                except Exception:
                    print(f'Failed to load module {module}.{os.path.splitext(extension)[0]}.', file=sys.stderr)
                    traceback.print_exc()


async def run():
    bot.load_extension("jishaku")
    bot.remove_command('help')

    await bot.start(bot.config.token, bot=True, reconnect=True)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        print("Stopping bot!")
