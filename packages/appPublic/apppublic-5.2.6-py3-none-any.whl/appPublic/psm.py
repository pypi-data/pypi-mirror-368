import json
from time import sleep
from multiprocessing import Manager
from multiprocessing.shared_memory import SharedMemory
from multiprocessing.resource_tracker import unregister

class PSharedMemory:
    tailstring=b'#:@#'
    def __init__(self, name, datalen, data=None):
        self.sm = None
        self.name = name
        self.datalen = datalen
        self.lock = Manager().Lock()
        if data:
            self.sm = SharedMemory(name=self.name, create=True, size=self.datalen)
            self.creator = True
            self.set(data)
        else:
            self.sm = SharedMemory(name=self.name)
            unregister(self.sm._name, 'shared_memory')
            self.creator = False

    def get(self):
        b = self.sm.buf.tobytes().split(self.tailstring)[0]
        d = b.decode('utf-8')
        return json.loads(d)

    def set(self, data):
        with self.lock:
            d = json.dumps(data)
            b = d.encode('utf-8') + self.tailstring
            if self.datalen < len(b):
                raise Exception(f'SharedMemory allocated size is {self.datalen} set size is {len(b)}')
            self.sm.buf[:len(b)] = b

    def __del__(self):
        if self.sm is None:
            return
        self.sm.close()
        if self.creator:
            self.sm.unlink()

if __name__ == '__main__':
    import sys
    data = {
        "aaa":"134902t34gf",
        "bbb":36
    }
    if len(sys.argv) > 1:
        sm = PSharedMemory('rtgerigreth', datalen=200, data=data)
        sleep(10000)
    else:
        sm = PSharedMemory('rtgerigreth', datalen=200 )
        x = sm.get()
        print(f'data in shared memory: {x}')

