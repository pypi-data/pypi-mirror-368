#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/6/11 09:35'


def is_list(v: str):
  try:
    list(v)
    if v[0] == "[" and v[-1] == "]":
      return True
    else:
      return False
  except Exception:
    return False


def is_digit(v: str):
  try:
    float(v)
    return True
  except Exception:
    return False


def is_bool(v: str):
  if v in ["False", "True"]:
    return True
  else:
    return False


def dict_to_params(obj: dict):
  params = ""
  for k, v in obj.items():
    if k == 'varname':
      continue
    v = str(v)
    if not is_list(v) and not is_digit(v) and not is_bool(v):
      if k == "path" and v[:4] != "http":
        v = "r'%s'" % v
      else:
        v = "'%s'" % v
    params += "%s=%s, " % (k, v)
  params = params[:params.rfind(',')]
  return params
