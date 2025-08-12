#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/6/9 09:02'

from ctools.web.api_result import R


class LLMException(Exception):

  def __init__(self, code, message):
    super(LLMException, self).__init__(message)
    self.code = code
    self.message = message

  def __str__(self):
    return R.error(resp=R.Code.cus_code(self.code, self.message))
