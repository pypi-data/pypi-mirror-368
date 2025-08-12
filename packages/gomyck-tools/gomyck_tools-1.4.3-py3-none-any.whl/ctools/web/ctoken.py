#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/1/21 16:01'

import time

import jwt
from bottle import request

from ctools import cid
from ctools.dict_wrapper import DictWrapper


class CToken:
  token_audience = ["gomyck"]
  token_secret_key = 'gomyck123'
  token_header = 'Authorization'

def gen_token(userid, username, payload={}, expired: int = 3600, rules= []) -> str:
  if expired and expired > 0: payload.update({'exp': time.time() + expired})
  payload.update({'iss': "gomyck", 'jti': cid.get_snowflake_id_str(), 'nbf': time.time(), 'iat': time.time()})
  payload.update({'rules': rules})
  payload.update({'uid': userid})
  payload.update({'sub': username})
  payload.update({'aud': CToken.token_audience})
  payload.update({'rules': rules})
  return jwt.encode(payload, CToken.token_secret_key, algorithm='HS256')

def get_payload(token=None):
  try:
    if token is None: token = get_token()
    payload = jwt.decode(token, options={"verify_signature": False}, algorithms=['HS256'])
    return DictWrapper(payload)
  except Exception as e:
    return None

def get_token_payload(token=None):
  if token is None: token = get_token()
  return get_payload(token)

def is_valid(token=None):
  """
  判断token是否有效
  :param token: token 信息
  :return: 是否有效
  """
  if token is None: token = get_token()
  if token is None: return False
  try:
    jwt.decode(token, CToken.token_secret_key, algorithms=['HS256'], audience=CToken.token_audience)
  except Exception as e:
    print(e)
    return False
  return True

def get_user_name():
  """
  获取用户名称
  :return: 用户ID
  """
  token_obj = get_token_attr("sub")
  return token_obj

def get_user_id():
  """
  获取用户ID
  :return: 用户ID
  """
  token_obj = get_token_attr("uid")
  return token_obj

def get_token_id():
  """
  获取token id
  :return: token id
  """
  token_obj = get_token_attr("jti")
  return token_obj

def get_app_flag() -> []:
  """
  获取服务标识
  :return: 服务标识 []
  """
  token_obj = get_token_attr("aud")
  return token_obj

def get_token_attr(attr):
    token_obj = get_token_payload()
    return getattr(token_obj, attr, None)

def get_token():
  auth_token = request.get_header(CToken.token_header)
  if auth_token is None:
    auth_token = request.get_cookie(CToken.token_header)
  return auth_token

# if __name__ == '__main__':
#   token = gen_token(123, username='xxx', expired=0)
#   print(token)
#   print(get_payload(token))
#   print(is_valid(token))
