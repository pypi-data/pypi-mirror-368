import uuid
from nanoid import generate

def setNode(n='ff001122334455'):
	pass

def getID(size=21):
	return generate(size=size)

def validate_code(id, cnt=6):
	b = int(len(id) / cnt)
	j = 0
	code = []
	v = 0
	print(f'{b=}, {cnt=}')
	for c in id:
		if j >= b:
			v = v % 10
			code.append(str(v))
			j = 0
		v += ord(c)
		j += 1
		if len(code) >= cnt:
			break
	return ''.join(code)

def check_code(id, code):
	c = validate_code(id)
	return c==code

if __name__ == '__main__':
	id = getID()
	code = validate_code(id)
	b = check_code(id, code)
	print(id, code, b)

