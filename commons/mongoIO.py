from pymongo import MongoClient
import discord
import config as cfg

def get_config():
    if cfg.DEBUG==True:
        return cfg.debugConf
    else:
        return cfg.conf

client = MongoClient(cfg.mongoDB.URI)
db = client[get_config().MONGODB]

def addUser(member: discord.Member, blacklist: bool = False, username: str = None):
	db.users.insert_one(
		{
			"blacklisted": blacklist,
			"id": member.id,
			"name": member.name,
			"osu": username
		}
	)

def addServer(server: discord.Guild, prefix: str = None):
	db.settings.insert_one(
		{
			"id": server.id,
			"prefix": prefix
		}
	)

def userExists(member:discord.Member):
	exists = db.users.find({"id": {"$eq": member.id}}).count()
	if exists > 0:
		return True
	else:
		return False

def serverExists(server: discord.Guild):
	exists = db.settings.find({"id": {"$eq": server.id}}).count()
	if exists > 0:
		return True
	else:
		return False

def getSetting(uid, setting: str):
	a = db.settings.find({'id':uid})
	b = None
	for x in a:
		b=x[setting]
	return b

def getOsu(member):
	a = db.users.find({'id':member.id})
	b = None
	for x in a:
		b=x["osu"]
	return b

def setOsu(member, username):
	if not userExists(member):
		addUser(member, False, username)
	else:
		db.users.update_one(
			{"id": member.id},
			{
				"$set": {
					"osu": username
				},
				"$currentDate": {"lastModified": True}
			}
		)

def setPrefix(server: discord.Guild, prefix: str):
	if serverExists(server):
		db.settings.update_one(
			{"id": server.id},
			{
				"$set": {
					"prefix": prefix
				},
				"$currentDate": {"lastModified": True}
			}
		)
	else:
		addServer(server, prefix)

def blacklistUser(member: discord.Member):
	if not userExists(member):
		addUser(member, True)
	else:
		db.users.update_one(
			{"id": member.id},
			{
				"$set": {
					"blacklisted": True
				},
				"$currentDate": {"lastModified": True}
			}
		)

def unblacklistUser(member: discord.Member):
	if not userExists(member):
		addUser(member, False)
	else:
		db.users.update_one(
			{"id": member.id},
			{
				"$set": {
					"blacklisted": False
				},
				"$currentDate": {"lastModified": True}
			}
		)

def isBlacklisted(member: discord.Member):
	a = db.users.find({'id': member.id})
	b = False
	for x in a:
		b=x['blacklisted']
	return b

def wipe():
	db.users.delete_many({})
	db.settings.delete_many({})