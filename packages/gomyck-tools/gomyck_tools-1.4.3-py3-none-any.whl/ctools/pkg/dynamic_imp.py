#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/7/15 11:03'

import importlib
import pkgutil


def load_modules_from_package(package, exclude=None, recursive=True):
  """
  递归加载指定包下所有模块（不包括包本身）

  :param package: 要加载模块的包对象（如 mypkg.plugins）
  :param exclude: 排除的模块完整路径列表（如 ['mypkg.plugins.demo.mod2']）
  :param recursive: 是否递归子包
  :return: 模块列表（不含子包本身，只包含模块）
  """
  if exclude is None: exclude = []
  modules = []
  for finder, modname, ispkg in pkgutil.iter_modules(package.__path__):
    full_modname = f"{package.__name__}.{modname}"
    if ispkg and recursive:
      try:
        subpkg = importlib.import_module(full_modname)
        modules.extend(load_modules_from_package(subpkg, exclude, recursive))
      except Exception as e:
        print(f"递归子包 {full_modname} 失败：{e}")
      continue
    if full_modname in exclude:
      continue
    try:
      module = importlib.import_module(full_modname)
      modules.append(module)
    except Exception as e:
      print(f"!!!!!!加载模块 {full_modname} 失败：{e}!!!!!!")
      continue
  return modules
