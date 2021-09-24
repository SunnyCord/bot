from discord.ext import commands

def check_permissions(ctx, perms):
    if is_owner_check(ctx):
        return True

    ch = ctx.message.channel
    author = ctx.author
    resolved = ch.permissions_for(author)
    return all(getattr(resolved, name, None) == value for name, value in perms.items())

def is_gowner(**perms):
    def predicate(ctx):
        if ctx.guild is None:
            return False
        guild = ctx.guild
        owner = guild.owner

        if ctx.author.id == owner.id:
            return True

        return check_permissions(ctx,perms)
    return commands.check(predicate)

def can_mute(**perms):
    def predicate(ctx):
        if ctx.author.guild_permissions.mute_members:
            return True
        else:
            return False
    return commands.check(predicate)

def can_kick(**perms):
    def predicate(ctx):
        if ctx.author.guild_permissions.kick_members:
            return True
        else:
            return False
    return commands.check(predicate)

def can_ban(**perms):
    def predicate(ctx):
        if ctx.author.guild_permissions.ban_members:
            return True
        else:
            return False
    return commands.check(predicate)

def can_managemsg(**perms):
    def predicate(ctx):
        if ctx.author.guild_permissions.manage_messages:
            return True
        else:
            return False
    return commands.check(predicate)

def can_manageguild(**perms):
    def predicate(ctx):
        if ctx.author.guild_permissions.manage_guild:
            return True
        else:
            return False
    return commands.check(predicate)

def is_admin(**perms):
    def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        else:
            return False
    return commands.check(predicate)