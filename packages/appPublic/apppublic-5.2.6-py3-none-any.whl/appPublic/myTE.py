import os
import sys
try:
	import ujson as json
except:
	import json
from jinja2 import Environment,FileSystemLoader, BaseLoader, meta
import codecs
from appPublic.argsConvert import ArgsConvert
from appPublic.dictObject import DictObject
def isNone(obj):
	return obj is None


def string_template_render(tmp_string, data):
	rtemplate = Environment(loader=BaseLoader()).from_string(tmp_string)
	return rtemplate.render(**data)

class MyTemplateEngine:
	def __init__(self,pathList,file_coding='utf-8',out_coding='utf-8', env={}):
		self.file_coding = file_coding
		self.out_coding = out_coding
		loader = FileSystemLoader(pathList, encoding=self.file_coding)
		self.env = Environment(loader=loader, enable_async=False)
		denv={
			'json':json,
			'hasattr':hasattr,
			'int':int,
			'float':float,
			'str':str,
			'type':type,
			'isNone':isNone,
			'len':len,
			'render':self.render,
			'renders':self.renders,
			'ArgsConvert':ArgsConvert,
			'renderJsonFile':self.renderJsonFile,
			'ospath':lambda x:os.path.sep.join(x.split(os.altsep)),
			'basename':lambda x:os.path.basename(x),
			'basenameWithoutExt':lambda x:os.path.splitext(os.path.basename(x))[0],
			'extname':lambda x:os.path.splitext(x)[-1],
		}
		self.env.globals.update(denv)
		if env:
			self.env.globals.update(env)

	def get_template_variables(tmpl):
		parsed_content = self.env.parse(tmpl)
		return meta.find_undeclared_variables(parsed_content)

	def set(self,k,v):
		self.env.globals.update({k:v})
		
	def _render(self,template,data):
		# print('**********template=',template,'**data=',data,'type_data=',type(data),'************')
		uRet = template.render(**data)
		return uRet
		
	def renders(self,tmplstring,data):
		def getGlobal():
			return data
		self.set('global',getGlobal)
		template = self.env.from_string(tmplstring)
		return self._render(template,data)

	def render(self,tmplfile,data):
		def getGlobal():
			return data
		self.set('global',getGlobal)
		template = self.env.get_template(tmplfile)
		return self._render(template,data)

	def renderJsonFile(self,tmplfile,jsonfile):
		with codecs.open(jsonfile,"r",self.file_coding) as f:
			data = json.load(f)
			return self.render(tmplfile,data)

def tmpTml(f, ns):
	te = MyTemplateEngine('.')
	with codecs.open(f, 'r', 'utf-8') as fd:
		d = fd.read()
		b = te.renders(d, ns)
		filename = os.path.basename(f)
		p = f'/tmp/{filename}'
		with codecs.open(p, 'w', 'utf-8') as wf: 
			wf.write(b)
			return p

if __name__ == '__main__':
	import sys
	import json
	if len(sys.argv) < 3:
		print(f'{sys.argv[0]} tmplfile jsonfile')
		sys.exit(1)
		
	te = MyTemplateEngine('.')
	with codecs.open(sys.argv[1], 'r', 'utf-8') as f:
		tmpl = f.read()
		with codecs.open(sys.argv[2], 'r', 'utf-8') as f1:
			ns = json.loads(f1.read())
			print(te.renders(tmpl, ns))
	
