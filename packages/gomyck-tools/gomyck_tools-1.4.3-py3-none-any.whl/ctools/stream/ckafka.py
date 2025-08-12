#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2024/9/5 10:39'

import time
from threading import Thread

from kafka import KafkaProducer, errors, KafkaConsumer
from kafka.producer.future import FutureRecordMetadata

from ctools.cjson import dumps

"""
import time
from datetime import datetime

from ctools import thread_pool, string_tools
from ctools.ckafka import CKafka

c = CKafka(kafka_url='192.168.3.160:9094', secure=True)

producer = c.init_producer()
consumer = c.init_consumer(enable_auto_commit=False)

def send_msg():
  while True:
    command = input('发送消息: Y/n \n')
    if command.strip() not in ['N', 'n']:
      producer.send_msg('jqxx', '{{"jqid": "{}", "xxxx": "{}"}}'.format(string_tools.get_snowflake_id(), datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')))
    else:
      break

thread_pool.submit(send_msg)

def consumer_callback(msg):
  print(msg)
  return True

consumer.receive_msg('jqxx', callBack=consumer_callback)

while True: time.sleep(1)
"""


class KafkaInstance:
  def __init__(self, producer: KafkaProducer, consumer: KafkaConsumer):
    self.start_consumer = False
    self.quited = False
    self.producer = producer
    self.consumer = consumer
    self.consumer_callback = {"topic_key": []}

  # FutureRecordMetadata 可以添加回调, 来监听是否发送成功
  # r.add_callback(lambda x: print(x))
  # r.get() 可以同步获取结果
  def send_msg(self, topic, msg, key: str = None, partition: int = None) -> FutureRecordMetadata:
    if self.producer is None: raise RuntimeError("Producer is not initialized")
    if self.quited: return
    return self.producer.send(topic=topic, value=msg, key=None if key is None else key.encode('utf-8'), partition=partition)

  def receive_msg(self, topics: str, callBack=print):
    if self.consumer is None: raise RuntimeError("Consumer is not initialized")
    for topic in topics.split(','):
      if topic not in self.consumer_callback.keys():
        self.consumer_callback[topic] = []
        self.consumer.subscribe(self.consumer_callback.keys())
      self.consumer_callback[topic].append(callBack)
    if not self.start_consumer:
      t = Thread(target=self._start_consumer_poll, daemon=True)
      t.start()

  def _start_consumer_poll(self):
    self.start_consumer = True
    for msg in self.consumer:
      if self.quited: break
      funcList = []
      begin_time = time.time()
      for func in self.consumer_callback[msg.topic]:
        if self.quited: break
        res = func(msg)
        if not self.consumer.config['enable_auto_commit'] and res: self.consumer.commit()
        funcList.append(func.__name__)
      end_time = time.time()
      if end_time - begin_time > 1: print(f"kafka consume too slow!!! {funcList} time cost: ", f'{round(end_time - begin_time, 2)}s')
      funcList.clear()

  def shutdown(self):
    self.quited = True
    try:
      self.consumer.close()
    except Exception:
      pass
    try:
      self.producer.close()
    except Exception:
      pass


class CKafka:

  def __init__(self, kafka_url: str = '127.0.0.1:9092', secure: bool = False, username: str = 'client', password: str = 'hylink_user_password'):
    self.kafka_url = kafka_url
    self.secure = secure
    self.username = username
    self.password = password

  def init_producer(self, acks=1) -> KafkaInstance:
    print("[ Producer ] Connecting to Kafka [{}]".format(self.kafka_url))
    for i in range(0, 6):
      try:
        if self.secure:
          producer = KafkaProducer(
            acks=acks,
            bootstrap_servers=self.kafka_url,
            value_serializer=lambda x: dumps(x).encode('utf-8'),
            sasl_plain_username=self.username,
            sasl_plain_password=self.password,
            security_protocol='SASL_PLAINTEXT',
            sasl_mechanism='PLAIN'
          )
        else:
          producer = KafkaProducer(
            acks=acks,
            bootstrap_servers=self.kafka_url,
            value_serializer=lambda x: dumps(x).encode('utf-8')
          )
        print("[ Producer ] Success Connected to Kafka [{}]".format(self.kafka_url))
        return KafkaInstance(producer=producer, consumer=None)
      except errors.NoBrokersAvailable:
        print("[ Producer ] Waiting for Kafka [{}] to become available...".format(self.kafka_url))
        time.sleep(3)
    raise RuntimeError("[ Producer ] Failed to connect to Kafka [{}] within 60 seconds".format(self.kafka_url))

  def init_consumer(self, client_id: str = 'ck-py-kafka-consumer', consumer_group: str = 'ck-py-kafka-consumer', enable_auto_commit: bool = True) -> KafkaInstance:
    print("[ Consumer ] Connecting to Kafka [{}]".format(self.kafka_url))
    for i in range(0, 6):
      try:
        if self.secure:
          consumer = KafkaConsumer(
            client_id=client_id,
            group_id=consumer_group,
            enable_auto_commit=enable_auto_commit,
            bootstrap_servers=self.kafka_url,
            value_deserializer=lambda x: x.decode('utf-8'),
            sasl_plain_username=self.username,
            sasl_plain_password=self.password,
            security_protocol='SASL_PLAINTEXT',
            sasl_mechanism='PLAIN'
          )
        else:
          consumer = KafkaProducer(
            client_id=client_id,
            group_id=consumer_group,
            enable_auto_commit=enable_auto_commit,
            bootstrap_servers=self.kafka_url,
            value_deserializer=lambda x: x.decode('utf-8')
          )
        print("[ Consumer ] Success Connected to Kafka [{}]".format(self.kafka_url))
        return KafkaInstance(producer=None, consumer=consumer)
      except errors.NoBrokersAvailable:
        print("[ Consumer ] Waiting for Kafka [{}] to become available...".format(self.kafka_url))
        time.sleep(3)
    raise RuntimeError("[ Consumer ] Failed to connect to Kafka [{}] within 60 seconds".format(self.kafka_url))
