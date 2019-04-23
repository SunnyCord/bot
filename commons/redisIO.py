import redis
import config as cfg
r = redis.Redis(host='localhost', port=6379, db=0)

def getValue(name):
    return r.get(name)

def setValue(name, value):
    r.set(name, value)