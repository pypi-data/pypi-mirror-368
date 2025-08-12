#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/7/15 13:08'

import sys

import jieba
from jieba import posseg as pseg

jqfx_exclude = ('ul', 'uj', 'uz', 'a', 'c', 'm', 'f', 'ad', 'an', 'r', 'q', 'u', 't', 'd', 'p', 'x')

def add_dict(dic_word: str = None, dic_path: str = None):
  """
  添加自定义词库(自定义词库添加之后, 如果不适用全模式切词, 有时也不好使, 因为权重没有默认的高)
  :param dic_word: 一个单词
  :param dic_path: 单词表文件地址
  单词表文件格式:
  单词  词频  标签
  单词1  3    i
  单词2  3    i
  单词3  3    i
  """
  if dic_word: jieba.add_word(dic_word)
  if dic_path: jieba.load_userdict(dic_path)

def add_freq(word: ()):
  """
  添加词频
  :param word: 一个单词
  """
  jieba.suggest_freq(word, True)

def get_declare_type_word(word: str, word_flag=(), use_paddle=False, exclude_flag="x"):
  #import paddle
  #paddle.enable_static()
  #sys.stdout = sys.__stdout__
  #sys.stderr = sys.__stderr__
  """
  获取声明类型的单词
  :param word: 单词
  :param word_flag: 标签
  :param use_paddle: 是否使用 paddle
  :param exclude_flag: 排除的标签
  :return:  筛选之后的单词(数组)
  """
  # linux 可以开放下面的语句, 并发执行分词, windows 不支持
  # if platform.system() == 'Linux': jieba.enable_parallel(4)
  ret = []
  for w, flag in pseg.cut(word, use_paddle=use_paddle):
    if (flag in word_flag or len(word_flag) == 0) and flag not in exclude_flag:
      ret.append((w, flag))
  return ret
