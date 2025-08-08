import os,re,sys
import codecs
from appPublic.folderUtils import _mkdir
from appPublic.Singleton import SingletonDecorator
from appPublic.folderUtils import ProgramPath
import threading
import time

import locale

comment_re = re.compile(r'\s*#.*')
msg_re = re.compile(r'\s*([^:]*)\s*:\s*([^\s].*)')

def dictModify(d, md) :
	for i in md.keys() :
		if md[i]!=None :
			d[i] = md[i]
	return d

convert_pairs = 	{':':'\\x3A',
	'\n':'\\x0A',
	'\r':'\\x0D',
}

def charEncode(s) :
	r = ''
	v = s.split('\\')
	s = '\\\\'.join(v)
	for i in convert_pairs.keys() :
		v = s.split(i)
		s = convert_pairs[i].join(v)
		# print 'i=',i,'iv=',convert_pairs[i],'s=',s
	return s
 
def charDecode(s) :
	for i in convert_pairs.items() :
		v = s.split(i[1])
		s = i[0].join(v)
	v = s.split('\\\\')
	s = '\\'.join(v)
	return s
     
def getTextDictFromLines(lines) :
	d = {}
	for l in lines :
		l = ''.join(l.split('\r'))
		if comment_re.match(l) :
			continue
		m = msg_re.match(l)
		if m :
			grp = m.groups()
			d[charDecode(grp[0])] = charDecode(grp[1])
	return d

def getFirstLang(lang) :
	s = lang.split(',')
	return s[0]

@SingletonDecorator
class MiniI18N:
	"""
	"""
	def __init__(self,path,lang=None,coding='utf8') :
		self.path = path
		l = locale.getdefaultlocale()
		self.curLang = l[0]
		self.coding = coding
		self.id = 'i18n'
		self.langTextDict = {}
		self.setupMiniI18N()
		self.missed_pt = None
		self.translated_pt = None
		self.header_pt = None
		self.footer_pt = None
		self.show_pt=None
		self.clientLangs = {}
		self.languageMapping = {}
		self.timeout = 600
	
	def __call__(self,msg,lang=None) :
		"""
		"""
		if type(msg) == type(b''):
			msg = msg.decode(self.coding)
		return self.getLangText(msg,lang)
		
	def setLangMapping(self,lang,path):
		self.languageMapping[lang] = path
		
	def getLangMapping(self,lang):
		return self.languageMapping.get(lang,lang)

	def setTimeout(self,timeout=600):
		self.timeout = timeout
	
	def delClientLangs(self):
		t = threading.currentThread()
		tim = time.time() - self.timeout
		[ self.clientLangs.pop(k,None) for k in self.clientLangs.keys() if self.clientLangs[k]['timestamp'] < tim ]
				
	def getLangDict(self,lang):
		lang = self.getLangMapping(lang)
		return self.langTextDict.get(lang,{})
		
	def getLangText(self,msg,lang=None) :
		"""
		"""
		if lang==None :
			lang = self.getCurrentLang()
		textMapping = self.getLangDict(lang)
		return textMapping.get(msg,msg)

	def setupMiniI18N(self) :
		"""
		"""

		p = os.path.join(self.path,'i18n')
		langs = []
		
		for f in os.listdir(p) :
			if os.path.isdir(os.path.join(p,f)) :
				langs.append(f)
		for dir in langs :
			p1 = os.path.join(p,dir,'msg.txt')
			if os.path.exists(p1) :
				f = codecs.open(p1,'r',self.coding)
				textDict = getTextDictFromLines(f.readlines())
				f.close()
				self.langTextDict[dir] = textDict
				
		self._p_changed = 1
		
	def setCurrentLang(self,lang):
		lang = self.getLangMapping(lang)
		t = time.time()
		threadid = threading.currentThread()
		a = dict(timestamp=t,lang=lang)
		self.clientLangs[threadid] = a

	def getCurrentLang(self) :
		"""
		"""
		threadid = threading.currentThread()
		return self.clientLangs[threadid]['lang']

def getI18N(coding='utf8'):
	path = ProgramPath()
	i18n = MiniI18N(path,coding)
	return i18n

