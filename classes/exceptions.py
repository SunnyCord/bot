from discord.ext import commands

class OsuAPIError(Exception):
    def __init__(self, server, queryType, message = ""):
        super().__init__(f"{server} API error occured when running getting {queryType}. {message}")
        self.server = server
        self.queryType = queryType

class DatabaseMissingError(Exception):
    def __init__(self, queryType, message = ""):
        super().__init__(message)
        self.queryType = queryType

class MusicPlayerError(commands.CommandError):
    def __init(self, message=""):
        super().__init__(message)