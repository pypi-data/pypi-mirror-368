import os,sys
import json
from pathlib import Path
from appPublic.dictObject import DictObject
from appPublic.Singleton import SingletonDecorator
from appPublic.folderUtils import ProgramPath
from appPublic.argsConvert import ArgsConvert

def key2ansi(dict):
	#print dict
	return dict
	a = {}
	for k,v in dict.items():
		k = k.encode('utf-8')
		#if type(v) == type(u" "):
		#	v = v.encode('utf-8')
		a[k] = v
	
	return a
	
class JsonObject(DictObject):
	"""
	JsonObject class load json from a json file
	"""
	def __init__(self,jsonholder,keytype='ansi',NS=None):
		jhtype = type(jsonholder)
		if jhtype == type("") or jhtype == type(u''):
			f = open(jsonholder,'r')
		else:
			f = jsonholder
		try:
				a = json.load(f)
		except Exception as e:
			print("exception:",self.__jsonholder__,e)
			raise e
		finally:
			if type(jsonholder) == type(""):
				f.close()
		
		if NS is not None:
			ac = ArgsConvert('$[',']$')
			a = ac.convert(a,NS)
		a['__jsonholder__'] = jsonholder
		a['NS'] = NS
		DictObject.__init__(self,**a)
	
@SingletonDecorator
class JsonConfig(JsonObject):
	pass

def getConfig(path=None,NS=None):
	pp = ProgramPath()
	if path==None:
		path = os.getcwd()
	cfname = os.path.abspath(os.path.join(path,"conf","config.json"))
	# print __name__,cfname
	ns = {
		'home':str(Path.home()),
		'workdir':path,
		'ProgramPath':pp
	}
	if NS is not None:
		ns.update(NS)
	a = JsonConfig(cfname,NS=ns)
	return a
	
if __name__ == '__main__':
	conf = JsonConfig(sys.argv[1])
	#print conf.db,conf.sql
	#conf1 = JsonConfig(sys.argv[1],keytype='unicode')
	conf1 = JsonConfig(sys.argv[1],keytype='ansi')

	print("conf=",dir(conf))
	print("conf1=",dir(conf1)	)	
