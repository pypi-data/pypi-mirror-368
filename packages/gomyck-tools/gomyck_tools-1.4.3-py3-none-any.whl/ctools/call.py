import os
import sched
import threading
import time
from functools import wraps


# annotation
_global_once_cache = {}
def once(func):
  code = func.__code__
  key = f"{os.path.abspath(code.co_filename)}:{code.co_firstlineno}"
  def wrapper(*args, **kwargs):
    if key not in _global_once_cache:
      _global_once_cache[key] = func(*args, **kwargs)
    return _global_once_cache[key]
  return wrapper

# annotation
_cache = {}
def init(func):
  code = func.__code__
  key = f"{os.path.abspath(code.co_filename)}:{code.co_firstlineno}"
  if key not in _cache:
    _cache[key] = func()
  def wrapper():
    return _cache[key]
  return wrapper

# annotation
_scheduler_cache = {}
def schd(interval_seconds, start_by_call=False, run_now=False):
  def decorator(func):
    key = f"{os.path.abspath(func.__code__.co_filename)}:{func.__code__.co_firstlineno}"
    lock = threading.Lock()
    @wraps(func)
    def wrapper(*args, **kwargs):
      if key in _scheduler_cache:
        return  # 已经调度过
      scheduler = sched.scheduler(time.time, time.sleep)
      def job():
        func(*args, **kwargs)
        scheduler.enter(interval_seconds, 1, job)
      def start_scheduler():
        with lock:
          if _scheduler_cache.get(key): return
          _scheduler_cache[key] = True
          if run_now:
            func(*args, **kwargs)
          scheduler.enter(interval_seconds, 1, job)
          scheduler.run()
      threading.Thread(target=start_scheduler, daemon=True).start()
    if not start_by_call:
      wrapper()
    return wrapper
  return decorator
