
def arrayExtend(s,addon):
	ret = []
	s_cnt = len(s)
	a_cnt = len(addon)
	for i,v in enumerate(addon):
		if i < s_cnt:
			if type(v)!=type(s[i]):
				ret.append(v)
				continue
			if isinstance(v,dict):
				x = dictExtend(v,s[i])
				ret.append(x)
				continue
		ret.append(v)
	if s_cnt < a_cnt:
		ret += s[i:]
	return ret

def dictExtend(s,addon):
	ret = {}
	ret.update(s)
	skeys = ret.keys()
	for k,v in addon.items():
		if k not in skeys:
			ret[k] = v
			continue
		if type(v)!=type(ret[k]):
			ret[k] = v
			continue
		if type(v)==type({}):
			ret[k] = dictExtend(ret[k],v)
			continue
		if type(v)==type([]):
			ret[k] = arrayExtend(ret[k],v)
			continue
		ret[k] = v
	return ret
