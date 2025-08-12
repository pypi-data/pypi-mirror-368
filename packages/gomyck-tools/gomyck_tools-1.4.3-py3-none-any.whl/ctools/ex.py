import time
import traceback
from functools import wraps

"""
@exception_handler(fail_return=['解析错误'], print_exc=True)
"""

# annotation
def exception_handler(fail_return, retry_num=0, delay=3, catch_e=Exception, print_exc=False):
  def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
      try:
        return func(*args, **kwargs)
      except catch_e as e:
        print(f"{func.__name__} runtime exception: {str(e)}")
        if print_exc: traceback.print_exc()
        nonlocal retry_num
        renum = retry_num
        if renum == 0:
          return fail_return
        else:
          while renum > 0:
            time.sleep(delay)
            renum -= 1
            try:
              return func(*args, **kwargs)
            except catch_e:
              pass
          return fail_return

    return wrapper

  return decorator
