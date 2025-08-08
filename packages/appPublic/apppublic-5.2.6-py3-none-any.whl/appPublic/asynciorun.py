import asyncio
import sys
from sqlor.dbpools import DBPools
from appPublic.jsonConfig import getConfig

def run(coro):
	p = '.'
	if len(sys.argv) > 1:
		p = sys.argv[1]
	config = getConfig(p, {'woridir':p})
	DBPools(config.databases)
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	loop.run_until_complete(coro())

