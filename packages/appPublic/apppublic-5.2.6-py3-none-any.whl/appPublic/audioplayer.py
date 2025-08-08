import time
from ffpyplayer.player import  MediaPlayer
from ffpyplayer.tools import set_log_callback, get_log_callback, formats_in

class AudioPlayer:
	def __init__(self, source=None, autoplay=False, 
				loop=False, 
				on_stop=None):
		self.volume = 1
		self.state = None
		self.source = None
		self.quitted = False
		self.loop = loop
		self.autoplay = autoplay
		self.player = None
		self.on_stop = on_stop
		self.cmds = []
		if source:
			self.set_source(source)

	def set_source(self, source):
		self.source = source
		self.load()

	def player_callback(self, selector, value):
		print(f'player_callback(): {selector}, {value}')
		if self.player is None:
			print(f'player_callback():self.player is None, {selector}, {value}')
			return
		if selector == 'quit':
			def close(*args):
				self.quitted = True
				self.unload()
			close()
		
		elif selector == 'eof':
			self._do_eos()

	def load(self):
		if self.source is None:
			return
		source = self.source
		self.unload()
		ff_opts = {'vn':True, 'sn':True}
		self.player = MediaPlayer(source,
			callback=self.player_callback,
			loglevel='info',
			ff_opts=ff_opts)
		player = self.player
		self.state = 'pause'
		s = time.perf_counter()
		while (player.get_metadata()['duration'] is None and
				not self.quitted and 
				time.perf_counter() - s < 10.):
			time.sleep(0.005)
		player.toggle_pause()
		time.sleep(0.04)
		player.set_volume(self.volume)
		if self.autoplay:
			self.play()

	def unload(self):
		self.player = None
		self.state = 'stop'
		self.quitted = False

	def __del__(self):
		self.unload()

	def play(self):
		if self.player is None:
			self.load()
		if self.player is None:
			print('play():self.player is None')
			return
		if self.state == 'play':
			return
		self.player.toggle_pause()
		self.state = 'play'

	def pause(self):
		if self.player is None:
			self.load()
		if self.player is None:
			print('pause():self.player is None')
			return
		if self.state == 'pause':
			return
		self.player.toggle_pause()
		self.state = 'pause'

	def is_busy(self):
		if self.player and self.state == 'play':
			return True
		return False

	def stop(self):
		if self.player is None:
			return
		if self.state == 'play':
			self.player.toggle_pause()
		self.state = 'stop'
		self.seek(0)
		if self.on_stop:
			self.on_stop()
	
	def seek(self, pos):
		if self.player is None:
			print('seek():self.player is None')
			return
		self.player.seek(pos, relative=False)

	def get_pos(self):
		if self.player is None:
			return 0
		return self.player.get_pts()

	def _do_eos(self, *args):
		print('_do_eos() called ...')
		if self.loop:
			self.seek(0.)
		else:
			print('go stop')
			self.stop()


if __name__ == '__main__':
	import sys
	p = AudioPlayer(autoplay=True, loop=True)
	p.source = sys.argv[1]
	p.load()
	p.play()
	while True:
		while p._pump():
			pass

		print("""
play: play it,
stop: stop play
pause:pause it
quit: exit
""")
		x = input()
		if x == 'quit':
			p.quitted = True
			p.stop()
			break
		if x == 'play':
			p.play()
			continue
		if x == 'stop':
			p.stop()
			continue
		if x == 'pause':
			p.pause()
			continue

