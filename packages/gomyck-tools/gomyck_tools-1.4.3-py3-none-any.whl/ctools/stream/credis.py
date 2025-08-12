#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/2/14 11:09'

import redis
from redis import Redis

from ctools import cdate, cid
from ctools.pools import thread_pool

# 最后一次连接的redis
_ck_redis: Redis = None

def get_redis(): return _ck_redis

def init_pool(host: str = 'localhost', port: int = 6379, db: int = 0, password: str = None,
              username: str = None, decode_responses: bool = True, max_connections: int = 75,
              health_check_interval: int = 30, retry_count: int = 3) -> Redis:
  for attempt in range(retry_count):
    try:
      r: Redis = redis.StrictRedis(
        host=host, port=port, db=db,
        username=username, password=password,
        retry_on_timeout=True,
        max_connections=max_connections,
        decode_responses=decode_responses,
        health_check_interval=health_check_interval,
        socket_connect_timeout=5,
        socket_timeout=5
      )
      if r.ping():
        print('CRedis connect {} {} success!'.format(host, port))
        global _ck_redis
        _ck_redis = r
        return _ck_redis
    except redis.ConnectionError as e:
      if attempt == retry_count - 1:
        raise Exception(f"Failed to connect to Redis after {retry_count} attempts: {str(e)}")
      print(f"Connection attempt {attempt + 1} failed, retrying...")


def add_lock(r: Redis, key: str, timeout: int = 30):
  if r.exists(key):
    expire_time = r.get(key)
    if expire_time and cdate.time_diff_in_seconds(expire_time, cdate.get_date_time()) > 0:
      return False
    else:
      r.delete(key)
  return r.set(key, cdate.opt_time(seconds=timeout), nx=True, ex=timeout) is not None


def remove_lock(r: Redis, key: str):
  r.delete(key)


def subscribe(r: Redis, channel_name, callback):
  def thread_func():
    pubsub = r.pubsub()
    pubsub.subscribe(channel_name)
    for message in pubsub.listen():
      callback(message)

  thread_pool.submit(thread_func)


def _process_pending_messages(r: Redis, stream_name: str, group_name: str, consumer_name: str, callback):
  """
  处理未确认的消息
  :param r: Redis 连接
  :param stream_name: 流名称
  :param group_name: 消费者组名称
  :param consumer_name: 消费者名称
  :param callback: 消息处理回调函数
  """
  # 检查未确认的消息
  pending_messages = r.xpending(stream_name, group_name)
  if pending_messages['pending'] > 0:
    print(f"Found {pending_messages['pending']} pending messages.")
    # 获取未确认的消息列表
    pending_list = r.xpending_range(stream_name, group_name, min='-', max='+', count=pending_messages['pending'])
    for message in pending_list:
      message_id = message['message_id']
      claimed_messages = r.xclaim(stream_name, group_name, consumer_name, min_idle_time=0, message_ids=[message_id])
      if claimed_messages:
        # 处理消息
        for claimed_message in claimed_messages:
          message_id, data = claimed_message
          print(f"Processing pending message: {message_id}, data: {data}")
          try:
            if callback(message_id, data):
              r.xack(stream_name, group_name, message_id)
          except Exception as e:
            print(f"Error processing message {message_id}: {e}")
  else:
    print("No pending messages found.")


def stream_subscribe(r: Redis, stream_name, group_name, callback, from_id: str = '$', noack: bool = False):
  def thread_func():
    try:
      # $表示从最后面消费, 0表示从开始消费
      r.xgroup_create(name=stream_name, groupname=group_name, id=from_id, mkstream=True)
      print(f"Consumer group '{group_name}' created successfully.")
    except Exception as e:
      if "already exists" in str(e):
        print(f"Consumer group '{group_name}' already exists.")
      else:
        print(f"Error creating consumer group '{group_name}': {e}")
    consumer_name = 'consumer-{}'.format(cid.get_uuid())
    # 处理未确认的消息
    _process_pending_messages(r, stream_name, group_name, consumer_name, callback)
    while True:
      messages = r.xreadgroup(group_name, consumer_name, {stream_name: '>'}, block=1000, noack=noack)
      for message in messages:
        try:
          message_id, data = message[1][0]
          res = callback(message_id, data)
          if res: r.xack(stream_name, group_name, message_id)
        except Exception as e:
          print('stream_subscribe error: ', e)

  thread_pool.submit(thread_func)


def stream_publish(r: Redis, stream_name, message):
  r.xadd(stream_name, message)
