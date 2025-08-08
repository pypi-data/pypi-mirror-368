import json
from json import JSONEncoder
from inspect import ismethod, isfunction, isbuiltin, isabstract

def multiDict2Dict(md):
	ns = {}
	for k,v in md.items():
		ov = ns.get(k,None)
		if ov is None:
			ns[k] = v
		elif type(ov) == type([]):
			ov.append(v)
			ns[k] = ov
		else:
			ns[k] = [ov,v]
	return ns

class DictObject:
	def __init__(self,**kw):
		self.org_keys__ = []
		self.org_keys__ = [ k for k in self.__dict__.keys()]
		for k,v in kw.items():
			self.update({k:self.__DOitem(v)})
	
	def __getattr__(self,name):
		if name in self._addon().keys():
			return self.__getitem__(name)
		return None

	def update(self,kw):
		self.__dict__.update(kw)

	def _addon(self):
		ks = [ k for k in self.__dict__.keys() if k not in self.org_keys__]
		return {k:v for k,v in self.__dict__.items() if k in ks}

	def clear(self):
		for k in self._addon().keys():
			self.__dict__.pop(k)

	def get(self,name,default=None):
		return self._addon().get(name,default)

	def pop(self,k,default=None):
		return self.__dict__.pop(k,default)

	def popitem(self):
		return self.__dict__.popitem()

	def items(self):
		return self._addon().items()

	def keys(self):
		return self._addon().keys()

	def values(self):
		return self._addon().values()

	def __delitem__(self,key):
		self.pop(key)

	def __getitem__(self,name):
		return self._addon().get(name)
	
	def __setitem__(self,name,value):
		self.__dict__[name] = value

	def __str__(self):
		return str(self._addon())

	def __expr__(self):
		return self.addon().__expr__()

	def copy(self):
		return {k:v for k,v in self._addon().items()}

	def to_dict(self):
		d = self._addon()
		newd =  self.dict_to_dict(d)
		return newd

	def dict_to_dict(self,dic):
		d = {}	
		for k,v in dic.items():
			if isinstance(v,DictObject):
				d[k] = v.to_dict()
			elif isinstance(v,dict):
				d[k] = self.dict_to_dict(v)
			elif isinstance(v,list):
				d[k] = self.array_to_dict(v)
			elif k == '__builtins__':
				pass
			elif isbuiltin(v) or isfunction(v) or ismethod(v) or isabstract(v):
				pass
			else:
				d[k] = v
		return d

	def array_to_dict(self,v):
		r = []
		for i in v:
			if isinstance(i,list):
				r.append(self.array_to_dict(i))
			elif isinstance(i,dict):
				r.append(self.dict_to_dict(i))
			elif isinstance(i,DictObject):
				r.append(i.to_dict())
			elif isbuiltin(i) or isfunction(i) or ismethod(i) or isabstract(i):
				pass
			else:
				r.append(i)
		return r

	@classmethod
	def isMe(self,name):
		return name == 'DictObject'
		
	def __DOArray(self,a):
		b = [ self.__DOitem(i) for i in a ]
		return b
	
	def __DOitem(self, i):
		if isinstance(i,DictObject):
			return i
		if isinstance(i,dict):
			i = {k:v for k,v in i.items() if isinstance(k,str)}
			try:
				d = DictObject(**i)
				return d
			except Exception as e:
				print("****************",i,"*******dictObject.py")
				raise e
		if type(i) == type([]) or type(i) == type(()) :
			return self.__DOArray(i)
		return i

class DictObjectEncoder(JSONEncoder):
	def default(self, o):
		return o._addon()
		
	

def dictObjectFactory(_klassName__,**kwargs):
	def findSubclass(_klassName__,klass):
		for k in klass.__subclasses__():
			if k.isMe(_klassName__):
				return k
			k1 = findSubclass(_klassName__,k)
			if k1 is not None:
				return k1
		return None
	try:
		if _klassName__=='DictObject':
			return DictObject(**kwargs)
		k = findSubclass(_klassName__,DictObject)
		if k is None:
			return DictObject(**kwargs)
		return k(**kwargs)
	except Exception as e:
		print("dictObjectFactory()",e,_klassName__)
		raise e
