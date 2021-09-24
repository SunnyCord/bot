import discord
import datetime
import classes.exceptions as Exceptions

class mongoIO():

	def __init__(self, bot):
		self.config = bot.config
		self.db=bot.motorClient[self.config.mongo['database']]

	async def addUser(self, member: discord.Member, blacklist: bool = False, osuID: int = None, osuServer: int = 0):
		await self.db.users.insert_one(
			{
				"blacklisted": blacklist,
				"id": member.id,
				"name": member.name,
				"osu": osuID,
				"preferredServer": osuServer
			}
		)

	async def removeUser(self, member: discord.Member):
		await self.db.users.delete_many({"id": member.id})

	async def userExists(self, member:discord.Member):
		return ( await self.db.users.find_one( {"id": {"$eq": member.id} } ) ) is not None

	async def getOsu(self, member: discord.Member):
		if ( databaseUser := await self.db.users.find_one( {"id": {"$eq": member.id} } ) ) is None:
			raise Exceptions.DatabaseMissingError("osu")
		if "preferredServer" not in databaseUser:
			databaseUser["preferredServer"] = 0
		return databaseUser["osu"], int(databaseUser["preferredServer"])

	async def setOsu(self, member: discord.Member, osuID: int, osuServer: int = 0):
		if not await self.userExists(member):
			await self.addUser(member, False, osuID)
		else:
			await self.db.users.update_one(
				{"id": member.id},
				{
					"$set": {
						"osu": osuID,
						"preferredServer": osuServer
					},
					"$currentDate": {"lastModified": True}
				}
			)

	async def blacklistUser(self, member: discord.Member):
		if not await self.userExists(member):
			await self.addUser(member, False, member.id)
		else:
			await self.db.users.update_one(
				{"id": member.id},
				{
					"$set": {
						"blacklisted": True
					},
					"$currentDate": {"lastModified": True}
				}
			)

	async def unblacklistUser(self, member: discord.Member):
		if not await self.userExists(member):
			await self.addUser(member, False, member.id)
		else:
			await self.db.users.update_one(
				{"id": member.id},
				{
					"$set": {
						"blacklisted": False
					},
					"$currentDate": {"lastModified": True}
				}
			)

	async def muteUser(self, member: discord.Member, guild: discord.Guild, ends):
		await self.db.mutes.update_one(
			{"memberID": member.id, "guildID": guild.id},
			{
				"$set": {
					"memberID": member.id,
					"guildID": guild.id,
					"ends":  ends
				}
			}, upsert=True
		)

	async def unmuteUser(self, member: discord.Member, guild: discord.Guild):
		await self.db.mutes.delete_many({"memberID": member.id, "guildID": guild.id})

	async def getExpiredMutes(self):
		return await self.db.mutes.find({ "ends": {"$lt": datetime.datetime.utcnow()} }).to_list(None)

	async def isBlacklisted(self, member: discord.Member):
		if ( databaseUser := await self.db.users.find_one({"id": {"$eq": member.id} }) ) is None:
			return False
		return databaseUser["blacklisted"]

	async def addServer(self, server: discord.Guild, prefix: str = None):
		await self.db.settings.insert_one(
			{
		        "id": server.id,
	            "prefix": prefix
			}
		)

	async def removeServer(self, guild: discord.Guild):
		await self.db.settings.delete_many({"guildID": guild.id})
		await self.db.mutes.delete_many({"guildID": guild.id})

	async def serverExists(self, server: discord.Guild):
		return ( await self.db.settings.find_one( {"id": {"$eq": server.id} } ) is not None )

	async def getSetting(self, server: discord.Guild, setting: str):
		if ( databaseGuild := await self.db.settings.find_one( {"id": {"$eq": server.id} } ) ) is None:
			return None
		return databaseGuild[setting]

	async def setPrefix(self, server: discord.Guild, prefix: str):
		if not await self.serverExists(server):
			await self.addServer(server, prefix)
		else:
			await self.db.settings.update_one(
				{"id": server.id},
				{
	                "$set": {
	                    "prefix": prefix
	                },
					"$currentDate": {"lastModified": True}
				}
			)

	async def wipe(self):
		await self.db.users.delete_many({})
		await self.db.mutes.delete_many({})
		await self.db.settings.delete_many({})