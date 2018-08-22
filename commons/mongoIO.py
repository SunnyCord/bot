from pymongo import MongoClient 
import discord
import config as cfg

client = MongoClient(cfg.mongoDB.URI)
db = client['sunny']

def getSetting(id, setting: str):
	a = db.settings.find({'id':id})
	b = None
	for x in a:
		b=x[setting]
	return b

def addUser(member: discord.Member, blacklist: bool = False):
	exists = db.users.find( {  "id":{"$eq":member.id}  }  ).count()
	if not exists:
		db.users.insert_one(
			{
				"blacklisted": blacklist,
				"id": member.id,
				"name": member.name
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
	db.users.update_one(
		{"id": member.id},
		{
			"$set": {
				"blacklisted": 1
			},
			"$currentDate": {"lastModified": True}
		}
	)
	
def unblacklistUser(member: discord.Member):
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