import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from ctools import call

thread_local = threading.local()

_threadPool: ThreadPoolExecutor = None


@call.init
def init():
  global _threadPool
  max_work_num = min(32, (os.cpu_count() or 1) + 4)  # 最多 32 个
  _threadPool = ThreadPoolExecutor(max_workers=max_work_num, thread_name_prefix='ck-')


def cb(f, callback):
  exc = f.exception()
  if exc:
    print(f"Task failed: {exc}")
    if callback: callback(exc)
  else:
    if callback: callback(f.result())


def submit(func, *args, callback=None, **kwargs):
  if _threadPool is None: raise Exception('thread pool is not init')
  future = _threadPool.submit(func, *args, **kwargs)
  future.add_done_callback(lambda f: cb(f, callback))
  time.sleep(0.01)
  return future


def shutdown(wait=True):
  if _threadPool is None: raise Exception('thread pool is not init')
  _threadPool.shutdown(wait=wait)
