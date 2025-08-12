#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2024/10/25 09:42'


class DictWrapper(dict):

  def __getattr__(self, key):
    res = self.get(key)
    if res is None:
      raise AttributeError(f" ==>> {key} <<== Not Found In This Entity!!!")
    if isinstance(res, dict):
      return DictWrapper(res)
    return res

  def __setattr__(self, key, value):
    self[key] = value

  def __delattr__(self, key):
    del self[key]
