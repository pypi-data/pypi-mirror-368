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

class DictObjectEncoder(JSONEncoder):
	def default(self, o):
		return o._addon()

class DictObject(dict):
	def __init__(self, *args, **kwargs):
		super().__init__()
		self.update(*args, **kwargs)

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			return None
			# raise AttributeError(f"No such attribute: {key}")

	def __setattr__(self, key, value):
		self[key] = value

	def __delattr__(self, key):
		try:
			del self[key]
		except KeyError:
			raise AttributeError(f"No such attribute: {key}")

	def __setitem__(self, key, value):
		super().__setitem__(key, self._wrap(value))

	def update(self, *args, **kwargs):
		for k, v in dict(*args, **kwargs).items():
			self[k] = self._wrap(v)

	def to_dict(self):
		return {k:DictObject._dict(v) for k,v in self.items()}

	def copy(self):
		return DictObject(**{k:DictObject._wrap(v) for k,v in self.items()})

	@staticmethod
	def _dict(value):
		if isinstance(value, dict):
			return value.to_dict()
		elif isinstance(value, list):
			return [DictObject._dict(v) for v in value]
		else:
			return value

	@staticmethod
	def _wrap(value):
		if isinstance(value, dict):
			return DictObject(value)
		elif isinstance(value, list):
			return [DictObject._wrap(v) for v in value]
		else:
			return value

"""
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
"""
