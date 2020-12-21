import queue
import types
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ObjectPool(object):
    def __init__(self, fn_cls, *args, **kwargs):
        super(ObjectPool, self).__init__()
        self.fn_cls = fn_cls
        self.maxSize = int(kwargs.get("max_size", 1))
        self.queue = queue.Queue()

    def _get_obj(self):
            if isinstance(self.fn_cls, types.FunctionType):
                return self.fn_cls
            elif isinstance(self.fn_cls, type):
                return self.fn_cls()
            else:
                raise("invalid type")
    
    def borrow_obj(self):
        if self.queue.qsize() < self.maxSize and self.queue.empty():
            self.queue.put(self._get_obj())
        return self.queue.get()

    def recover_obj(self, obj):
        self.queue.put(obj)

@contextmanager
def get_object(pool):
    obj = pool.borrow_obj()
    try:
        yield obj
    except Exception as err:
        logger.error("get object failed, error info: {}".format(err))
        yield None
    finally:
        pool.recover_obj(obj)


if __name__ == "__main__":
    pool_func = ObjectPool(echo_func, max_size=4)
    pool_cls = ObjectPool(echo_cls, max_size=4)
    
    with get_object(pool_func) as func:
        func(23)
    with get_object(pool_cls) as obj:
        obj.run()