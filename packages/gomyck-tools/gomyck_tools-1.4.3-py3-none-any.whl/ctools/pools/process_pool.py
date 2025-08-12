#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2024/9/20 12:00'

import os
import time
from concurrent.futures import ProcessPoolExecutor

from ctools import call

_process_pool: ProcessPoolExecutor = None


@call.init
def init():
  global _process_pool
  max_workers = min(32, os.cpu_count())  # 最多 32 个
  _process_pool = ProcessPoolExecutor(max_workers=max_workers)


def cb(f, callback):
  exc = f.exception()
  if exc:
    if callback: callback(exc)
    raise exc
  else:
    if callback: callback(f.result())


def submit(func, *args, callback=None, **kwargs):
  if _process_pool is None: raise Exception('process pool is not init')
  future = _process_pool.submit(func, *args, **kwargs)
  future.add_done_callback(lambda f: cb(f, callback))
  time.sleep(0.01)
  return future


def shutdown(wait=True):
  if _process_pool is None: raise Exception('process pool is not init')
  _process_pool.shutdown(wait=wait)
