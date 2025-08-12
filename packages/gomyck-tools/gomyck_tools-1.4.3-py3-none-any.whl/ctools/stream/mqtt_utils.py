import time
from enum import Enum
from typing import Dict

from paho.mqtt import client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

from ctools import cid, cdate
from ctools import sys_log, cjson, sys_info
from ctools.cipher import sm_util
from ctools.dict_wrapper import DictWrapper as DictToObj
from ctools.pools import thread_pool


class MQTTEvent(Enum):
  pass


'''
MQTT服务使用示例:

mqtt_utils = MQTTUtils("192.168.3.100")
mqtt_utils.connect(username="rpa", password="123")

# 订阅
mqtt_utils.subscribe("test/topic1", "test/topic2")

# 异步发送
msg = {"name": "测试消息"}
mqtt_utils.publish_async(msg, event=MQTTEvent.END_TASK)

# 同步发送
mqtt_resp = mqtt_utils.publish_sync(msg, event=MQTTEvent.UPLOAD_PROCESS, timeout=60)
status = mqtt_resp.status
body = mqtt_resp.body
print("%s, %s" % (status, body))
'''

log = sys_log.flog

NO_LOG_EVENT = [MQTTEvent.HEARTBEAT]


class MQTTRequest:

  def __init__(self, **kwargs):
    self.event: str = kwargs.get('event')
    self.trace_id: str = kwargs.get('trace_id') if kwargs.get('trace_id') else cid.get_uuid()
    self.client_id: str = kwargs.get('client_id')
    self.time: str = kwargs.get('time') if kwargs.get('time') else cdate.get_date_time()
    self.body = kwargs.get('body')

  def __str__(self):
    res_str = ""
    for k, v in self.__dict__.items():
      res_str += "%s=%s," % (k, v)
    return res_str[:-1]


class MQTTResponse:

  def __init__(self, **kwargs):
    self.event: str = kwargs.get('event')
    self.trace_id: str = kwargs.get('trace_id')
    self.status: int = kwargs.get('status')
    self.time: str = kwargs.get('time') if kwargs.get('time') else cdate.get_date_time()
    self.msg: str = kwargs.get('msg')
    self.body = kwargs.get('body')

  def __str__(self):
    res_str = ""
    for k, v in self.__dict__.items():
      res_str += "%s=%s," % (k, v)
    return res_str[:-1]


class MQTTUtils:
  def __init__(self, broker_address, port=1883, publish_topic=None, client_id=None, keepalive=60, clean_session=False,
               userdata=None, protocol=mqtt.MQTTv311, message_handle=None, broker_encrypt_key=None):
    self.publish_topic = publish_topic
    self.broker_address = broker_address
    self.port = port
    self.client_id = client_id if client_id else sys_info.get_machine_code()
    self.keepalive = keepalive
    self.clean_session = clean_session
    self.userdata = userdata
    self.protocol = protocol
    self.message_handle = message_handle
    self.broker_encrypt_key = broker_encrypt_key

    self.client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id=self.client_id, clean_session=self.clean_session,
                              userdata=self.userdata, protocol=self.protocol)
    self.client.on_connect = self._on_connect
    self.client.on_message = self._on_message_thread
    self.client.on_disconnect = self._on_disconnect
    if self.publish_topic:
      will_msg = {
        "event": "offline",
        "client_id": self.client_id,
        "trace_id": cid.get_uuid(),
        "time": cdate.get_date_time(),
        "body": {"type": "will_msg"}
      }
      self.client.will_set(self.publish_topic, cjson.dumps(will_msg), 2, False)
    self.connected = False
    self._publish_trace_id = []
    self._received_message: Dict[str: MQTTResponse] = {}

  def _on_connect(self, client, userdata, flags, rc, properties):
    if rc == 0:
      log.info("mqtt服务连接成功")
      self.connected = True
    else:
      log.info("mqtt服务连接失败, broker地址: %s:%s, rc: %s" % (self.broker_address, self.port, rc))

  def _on_message_thread(self, client, userdata, message):
    thread_pool.submit(self._on_message, client=client, userdata=userdata, message=message)

  def _on_message(self, client, userdata, message):
    # try:
    if message.topic != self.publish_topic and message.payload:
      mqtt_msg = cjson.loads(message.payload.decode())
      trace_id = mqtt_msg.get('trace_id')
      if trace_id in self._publish_trace_id:
        mqtt_resp = MQTTResponse(**mqtt_msg)
        self._received_message[trace_id] = mqtt_resp
        self._publish_trace_id.remove(trace_id)
      else:
        mqtt_req = MQTTRequest(**mqtt_msg)

        try:
          if mqtt_req.event not in NO_LOG_EVENT:
            log.debug("异步接收mqtt消息: %s" % str(mqtt_req))
          if mqtt_req.body:
            try:
              mqtt_req.body = self.decrypt_body(mqtt_req.body)
            except Exception:
              if mqtt_req.event != MQTTEvent.HAND_SHARK:
                log.error('解密消息失败: {}'.format(mqtt_req))
                return
          if isinstance(mqtt_req.body, dict):
            mqtt_req.body = DictToObj(mqtt_req.body)
        except Exception as e:
          log.info("异步接收mqtt消息异常: %s" % e)
        self.message_handle(mqtt_req, message.topic)
    # except Exception as e:
    #   log.error("接收mqtt消息异常: %s" % e)

  def _on_disconnect(self, client, userdata, flags, rc, properties):
    self.connected = False
    log.info("mqtt服务已断开连接, rc: %s" % rc)

  def encrypt_body(self, body):
    if self.broker_encrypt_key:
      try:
        return sm_util.encrypt_with_sm4(self.broker_encrypt_key, cjson.dumps(body))
      except Exception:
        return sm_util.encrypt_with_sm4(self.broker_encrypt_key, body)

  def decrypt_body(self, body):
    if self.broker_encrypt_key:
      try:
        return cjson.loads(sm_util.decrypt_with_sm4(self.broker_encrypt_key, body))
      except Exception:
        sm_util.decrypt_with_sm4(self.broker_encrypt_key, body)

  def connect(self, username=None, password=None, timeout=10):
    if username and password:
      self.client.username_pw_set(username, password)
    self.client.connect_async(host=self.broker_address, port=self.port, keepalive=self.keepalive)
    self.client.loop_start()

    start_time = time.time()
    while not self.connected and time.time() - start_time < timeout:
      time.sleep(0.1)

    if not self.connected:
      log.info("mqtt服务连接超时, broker地址: %s:%s" % (self.broker_address, self.port))

  def publish_resp(self, mqtt_resp: MQTTResponse, topic=None, encrypt=True, qos=2, retain=False):
    """
    发送mqtt响应信息
    :param mqtt_resp: 响应信息, 使用 mqtt_service.init_resp('ok', req)
    :param topic: 主题, 默认用订阅的主题
    :param encrypt: 是否加密
    :param qos: 消息质量
    :param retain: 是否保留
    """
    topic = topic if topic else self.publish_topic
    if self.connected:
      if mqtt_resp:
        try:
          if encrypt and mqtt_resp.body:
            mqtt_resp.body = self.encrypt_body(mqtt_resp.body)
          mqtt_resp.client_id = self.client_id
          mqtt_data = cjson.dumps(mqtt_resp)
          self.client.publish(topic, mqtt_data, qos=qos, retain=retain)
          log.debug("异步发送mqtt响应消息: topic: %s message: %s" % (topic, mqtt_data))
        except Exception as e:
          log.error('异步发送mqtt响应消息异常: %s' % e)
    else:
      log.info("异步发送mqtt响应-mqtt服务未连接, 无法发送消息")

  def publish_async(self, message, event: MQTTEvent = None, encrypt=True, topic=None, qos=2, retain=False):
    topic = topic if topic else self.publish_topic
    if self.connected:
      try:
        if encrypt and message:
          message = self.encrypt_body(message)

        mqtt_req = MQTTRequest()
        mqtt_req.client_id = self.client_id
        mqtt_req.body = message
        if event:
          mqtt_req.event = event.value
        mqtt_data = cjson.dumps(mqtt_req)
        self.client.publish(topic, mqtt_data, qos=qos, retain=retain)
        if event not in NO_LOG_EVENT:
          log.debug("异步发送mqtt消息: topic: %s message: %s" % (topic, mqtt_data))
      except Exception as e:
        log.error('异步发送mqtt消息异常: %s' % e)
    else:
      log.info("异步发送mqtt消息-mqtt服务未连接, 无法发送消息")

  def publish_sync(self, message, event: MQTTEvent, topic=None, encrypt=True,
                   qos=2, retain=False, timeout: int = 15, send_time: str = None) -> MQTTResponse:
    if not event: raise Exception("事件不能为空")
    mqtt_resp = MQTTResponse()
    mqtt_resp.status = 500
    mqtt_resp.msg = "服务端未响应, 请联系管理员!"
    topic = topic if topic else self.publish_topic
    if self.connected:
      try:
        if encrypt and message:
          message = self.encrypt_body(message)

        mqtt_req = MQTTRequest()
        mqtt_req.source = "client"
        mqtt_req.client_id = self.client_id
        mqtt_req.body = message
        mqtt_req.time = send_time if send_time else mqtt_req.time
        mqtt_req.event = event.value
        mqtt_data = cjson.dumps(mqtt_req)
        self._publish_trace_id.append(mqtt_req.trace_id)
        self.client.publish(topic, mqtt_data, qos=qos, retain=retain)
        if event not in NO_LOG_EVENT:
          log.debug("同步发送mqtt消息: topic: %s message: %s" % (topic, mqtt_data))
        is_timeout = False
        start_time = time.time()
        while True:
          if mqtt_req.trace_id in self._received_message:
            mqtt_resp = self._received_message.pop(mqtt_req.trace_id)
            if mqtt_resp.body and encrypt:
              mqtt_resp.body = self.decrypt_body(mqtt_resp.body)
            break
          if (time.time() - start_time) >= timeout:
            is_timeout = True
            break
          time.sleep(0.5)
        if not is_timeout:
          if event not in NO_LOG_EVENT:
            log.debug("同步接收mqtt消息: topic: %s message: %s" % (topic, mqtt_resp))
        else:
          log.info("同步发送mqtt消息, 等待返回信息超时: %s" % mqtt_req)
      except Exception as e:
        log.error('同步发送mqtt消息异常: %s-%s' % (event.value, e))
    else:
      log.info("同步接收mqtt消息-mqtt服务未连接, 无法发送消息")
    return mqtt_resp

  def subscribe(self, *topic, qos=0):
    if self.connected:
      if topic and len(topic) > 0:
        for t in topic:
          self.client.subscribe(t, qos=qos)
          log.info("已订阅mqtt主题[%s]" % t)
    else:
      log.info("mqtt服务未连接, 无法订阅主题")

  def unsubscribe(self, *topic):
    if self.connected:
      if topic and len(topic) > 0:
        for t in topic:
          self.client.unsubscribe(t)
          log.info("已解除订阅mqtt主题[%s]" % t)
    else:
      log.info("mqtt服务未连接, 无法解除订阅主题")

  def disconnect(self):
    if self.connected:
      self.client.disconnect()
      self.client.loop_stop()
      log.info("已关闭mqtt服务连接")
