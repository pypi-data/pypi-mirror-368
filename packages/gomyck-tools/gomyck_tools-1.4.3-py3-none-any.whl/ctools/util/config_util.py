#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/7/16 14:19'

"""
config = load_config("application.ini")
print(config)
print(config.base.app_name)
print(config.base.version)
"""
from configparser import ConfigParser

cache = {}

class AttrNoneNamespace:
  def __init__(self):
    pass
  def __setattr__(self, key, value):
    super().__setattr__(key, value)
  def __getattr__(self, item):
    return None

def _convert_value(value: str):
  val = value.strip()
  if val.lower() in ('true', 'yes', 'on'):
    return True
  if val.lower() in ('false', 'no', 'off'):
    return False
  if val.isdigit():
    return int(val)
  try:
    return float(val)
  except ValueError:
    return val

def _config_to_object(config: ConfigParser):
  result = AttrNoneNamespace()
  for section in config.sections():
    section_obj = AttrNoneNamespace()
    for key, value in config.items(section):
      setattr(section_obj, key, _convert_value(value))
    setattr(result, section, section_obj)
  return result

def load_config(file_path):
  if file_path in cache: return cache[file_path]
  config = ConfigParser()
  config.read(file_path)
  cf = _config_to_object(config)
  cache[file_path] = cf
  return cf
