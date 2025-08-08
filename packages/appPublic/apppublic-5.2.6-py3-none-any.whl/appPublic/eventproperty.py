from eventpy.eventdispatcher import EventDispatcher
from appPublic.dictObject import DictObject

def bind(self, eventname, handler):
	self.appendListener(eventname, handler)

def unbind(self, eventname, handler):
	self.removeListener(eventname, handler);

EventDispatcher.bind = bind
EventDispatcher.unbind = unbind

class EventProperty:
	def __init__(self, event_name, initial_value=None):
		self._value = initial_value
		self.event_name = event_name

	def __get__(self, instance, owner):
		return self._value

	def __set__(self, instance, value):
		if self._value != value:
			self._value = value
			d = DictObject()
			d.target = instance
			d.data = value
			d.event = self.event_name
			instance.dispatch(self.event_name, d)


if __name__ == '__main__':
	class SomeClass(EventDispatcher):
		state = EventProperty('onstate', 0)
		age = EventProperty('onage', 20)

		def __init__(self):
			super().__init__()

	def observer1(data):
		print(f"Observer 1 received: {data}")

	def observer2(data):
		print(f"Observer 2 received: {data}")

	def observer3(data):
		print(f"Observer 3 received: {data}")

	# 创建实例
	si = SomeClass()
	# 添加监听
	si.bind('onstate', observer1)
	si.bind('onstate', observer2)
	si.bind('onage', observer3)

	# 改变状态
	si.state = 10  # 输出: Observer 1 received: 10, Observer 2 received: 10
	# 再次改变状态
	# si.unbind('onstate', observer1) unbind has error
	si.state = 20  # 输出: Observer 2 received: 20
	# change age's value
	si.age = 30

