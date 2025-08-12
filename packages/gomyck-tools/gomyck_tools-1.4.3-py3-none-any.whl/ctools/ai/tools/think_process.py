#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/6/3 14:30'

import re


def remove_think_blocks(text: str) -> str:
  cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
  return cleaned_text.strip()
