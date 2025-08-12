#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/7/23 08:33'

import functools
import sys

from ctools.pools import thread_pool

def _ensure_list(funcs):
  if callable(funcs):
    return [funcs]
  if isinstance(funcs, (list, tuple, set)):
    return list(funcs)
  raise TypeError("必须是可调用对象或可迭代对象")

def before(before_funcs):
  """
  用于将无参函数注入目标函数的调用前
  支持多个函数
  """
  before_funcs = _ensure_list(before_funcs)
  def decorator(func, sync=True):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      for bf in before_funcs:
        if callable(bf):
          if sync:
            bf()
          else:
            thread_pool.submit(bf)
      return func(*args, **kwargs)
    _replace_func_binding(func, wrapper)
    return wrapper
  return decorator

def after(after_funcs, sync=True):
  """
  用于将无参函数注入目标函数的调用后
  支持多个函数
  """
  after_funcs = _ensure_list(after_funcs)
  def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      result = func(*args, **kwargs)
      for af in after_funcs:
        if callable(af):
          if sync:
            af()
          else:
            thread_pool.submit(af)
      return result
    _replace_func_binding(func, wrapper)
    return wrapper
  return decorator

def _replace_func_binding(old_func, new_func):
  """
  替换函数在其模块中的绑定，确保所有使用点都生效
  """
  mod = sys.modules.get(old_func.__module__)
  if mod and hasattr(mod, old_func.__name__):
    setattr(mod, old_func.__name__, new_func)
