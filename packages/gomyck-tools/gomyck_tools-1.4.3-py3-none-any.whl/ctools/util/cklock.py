#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/7/18 15:46'

import contextvars
import threading
from contextlib import contextmanager
from functools import wraps

from ctools.stream.credis import get_redis, add_lock, remove_lock
from ctools.web import ctoken
from ctools.web.api_result import R

# 全局锁容器
_lock_dict = {}
_lock_dict_lock = threading.Lock()

def try_acquire_lock(key: str) -> bool:
  with _lock_dict_lock:
    if key not in _lock_dict:
      _lock_dict[key] = threading.Lock()
    return _lock_dict[key].acquire(blocking=False)

def try_acquire_lock_block(key: str):
  with _lock_dict_lock:
    if key not in _lock_dict:
      _lock_dict[key] = threading.Lock()
    _lock = _lock_dict[key]
  _lock.acquire()  # 这里是阻塞的

def release_lock(key: str):
  with _lock_dict_lock:
    _lock = _lock_dict.get(key)
    if _lock and _lock.locked():
      _lock.release()
    if _lock and not _lock.locked():
      _lock_dict.pop(key, None)

@contextmanager
def try_lock(key: str="sys_lock", block=False):
  if not block:
    acquired = try_acquire_lock(key)
    try:
      yield acquired
    finally:
      if acquired:
        release_lock(key)
  else:
    try_acquire_lock_block(key)
    try:
      yield
    finally:
      release_lock(key)

#annotation
"""
@lock("params.attr")
"""
# 上下文保存锁key集合
current_locks = contextvars.ContextVar("current_locks", default=set())

def lock(lock_attrs=None):
  def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
      lock_key = ""
      nonlocal lock_attrs
      user_level_lock = False

      if not lock_attrs:
        user_id = ctoken.get_user_id()
        if user_id:
          user_level_lock = True
          lock_key = f"USER_ID_LOCK_{user_id}"
        else:
          raise ValueError("请设置 lock_attrs 或使用 token！")

      if not user_level_lock:
        if isinstance(lock_attrs, str): lock_attrs = [lock_attrs]
        try:
          for attr in lock_attrs:
            parts = attr.split(".")
            if len(parts) != 2:
              raise ValueError(f"lock_attr: {attr} 格式错误")
            obj = kwargs.get(parts[0]) or args[0]
            if obj is None:
              raise ValueError(f"参数 {parts[0]} 不存在")
            lock_key += f"_{getattr(obj, parts[1], None)}"
        except Exception as e:
          raise ValueError(f"生成锁键失败: {e}")

      lock_set = current_locks.get()
      if lock_key in lock_set:
        return func(*args, **kwargs)
      token = current_locks.set(lock_set | {lock_key})

      try:
        if not get_redis():
          with try_lock(lock_key) as locked:
            if not locked:
              return R.error("操作过于频繁, 请稍后再试")
            return func(*args, **kwargs)
        else:
          locked = add_lock(get_redis(), lock_key)
          try:
            if locked:
              return func(*args, **kwargs)
            else:
              return R.error("操作过于频繁, 请稍后再试")
          finally:
            if locked:
              remove_lock(get_redis(), lock_key)
      finally:
        current_locks.reset(token)
    return wrapper
  return decorator

