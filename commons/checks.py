from discord.ext import commands
import os
from commons.mongoIO import isBlacklisted

#
# This is a modified version of checks.py, originally made by Rapptz
#
#                 https://github.com/Rapptz
#          https://github.com/Rapptz/RoboDanny/tree/async
#
# The permission system of the bot is based on a "just works" basis
# You have permissions and the bot has permissions. If you meet the permissions
# required to execute the command (and the bot does as well) then it goes through
# and you can execute the command.
# If these checks fail, then there are two fallbacks.
# A role with the name of Bot Mod and a role with the name of Bot Admin.
# Having these roles provides you access to certain commands without actually having
# the permissions required for them.
# Of course, the owner will always be able to execute commands.

def is_owner_check(ctx):
    return ctx.message.author.id == '151670779782758400'

def check_permissions(ctx, perms):
    if is_owner_check(ctx):
        return True

    ch = ctx.message.channel
    author = ctx.message.author
    resolved = ch.permissions_for(author)
    return all(getattr(resolved, name, None) == value for name, value in perms.items())

def is_gowner(**perms):
    def predicate(ctx):
        if ctx.message.guild is None:
            return False
        guild = ctx.message.guild
        owner = guild.owner

        if ctx.message.author.id == owner.id:
            return True

        return check_permissions(ctx,perms)
    return commands.check(predicate)

def can_mute(**perms):
    def predicate(ctx):
        if ctx.message.author.guild_permissions.mute_members:
            return True
        else:
            return False
    return commands.check(predicate)

def can_kick(**perms):
    def predicate(ctx):
        if ctx.message.author.guild_permissions.kick_members:
            return True
        else:
            return False
    return commands.check(predicate)

def can_ban(**perms):
    def predicate(ctx):
        if ctx.message.author.guild_permissions.ban_members:
            return True
        else:
            return False
    return commands.check(predicate)

def can_managemsg(**perms):
    def predicate(ctx):
        if ctx.message.author.guild_permissions.manage_messages:
            return True
        else:
            return False
    return commands.check(predicate)

def can_manageguild(**perms):
    def predicate(ctx):
        if ctx.message.author.guild_permissions.manage_guild:
            return True
        else:
            return False
    return commands.check(predicate)

def is_admin(**perms):
    def predicate(ctx):
        if ctx.message.author.guild_permissions.administrator:
            return True
        else:
            return False
    return commands.check(predicate)

def is_blacklisted(**perms):
    def predicate(ctx):
        return not isBlacklisted(ctx.message.author)
    return commands.check(predicate)