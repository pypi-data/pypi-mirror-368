import os
import threading
from enum import Enum

from prometheus_client import Counter, Gauge, Summary, Histogram, start_http_server

from ctools import call, cjson, sys_log, path_info

log = sys_log.flog

_metrics_port = 8889
_persistent_json = {}
_metrics_initial = {}
_lock = threading.Lock()
_metrics_persistent_path = os.path.join(path_info.get_user_work_path('metrics', True), 'persistent.json')


# 认证中间件
# @app.before_request
# def check_authentication():
#   auth = request.authorization
#   if not auth or auth.username != USERNAME or auth.password != PASSWORD:
#     return Response(
#       "Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'}
#     )

class MetricType(Enum):
  COUNTER = 'counter'
  GAUGE = 'gauge'
  SUMMARY = 'summary'
  HISTOGRAM = 'histogram'


class Metric:
  def __init__(self, metric_type: MetricType, metric_key: str, metric_labels: [], persistent: bool = False, buckets: [] = None, reset: bool = False, desc: str = ""):
    self.metric_type = metric_type
    self.metric_key = metric_key
    self.metric_labels = metric_labels
    self.buckets = buckets
    self.metric = None
    self.persistent = persistent
    self.reset = reset
    if metric_type == MetricType.COUNTER:
      self.metric = Counter(metric_key, desc, metric_labels)
    elif metric_type == MetricType.GAUGE:
      self.metric = Gauge(metric_key, desc, metric_labels)
    elif metric_type == MetricType.SUMMARY:
      self.metric = Summary(metric_key, desc, metric_labels)
    elif metric_type == MetricType.HISTOGRAM:
      if buckets is None: raise Exception('histogram buckets can not empty')
      self.metric = Histogram(metric_key, desc, metric_labels, buckets=self.buckets)
    else:
      raise Exception('metric type not found')
    _metrics_initial[metric_key] = self


@call.once
def init(reset_persistent: bool = False):
  if os.path.exists(_metrics_persistent_path) and not reset_persistent:
    with open(_metrics_persistent_path, 'r') as persistent_file:
      global _persistent_json
      try:
        content = persistent_file.readline()
        log.info("persistent初始化: %s" % content)
        _persistent_json = cjson.loads(content)
      except Exception:
        log.error('persistent.json is not valid json!!!!!')
        _persistent_json = {}
  _init_all_metrics()
  _persistent_json = _persistent_json or {}
  for key, item in _persistent_json.items():
    metrics_key = key.split("-")[0]
    if '_labels' in key or metrics_key not in _metrics_initial: continue
    opt(metrics_key, _persistent_json[key + '_labels'], _persistent_json[key])
  persistent_metrics()
  start_http_server(port=_metrics_port)


@call.schd(5, start_by_call=True)
def persistent_metrics():
  if _persistent_json and not _lock.locked():
    log.info('begin persistent metrics to file...')
    with open(_metrics_persistent_path, 'w') as persistent_file:
      persistent_file.write(cjson.dumps(_persistent_json))
      persistent_file.flush()


def opt(metric_key: str, label_values: [], metric_value: int):
  _lock.acquire(timeout=5)
  try:
    persistent_key = "%s-%s" % (metric_key, "_".join(map(str, label_values)))
    metric_entity: Metric = _metrics_initial[metric_key]
    if metric_entity.persistent:
      if not metric_entity.reset and persistent_key in _persistent_json:
        _persistent_json[persistent_key] += metric_value
      else:
        _persistent_json[persistent_key] = metric_value
      _persistent_json[persistent_key + '_labels'] = label_values

      if _persistent_json[persistent_key] < 0:
        _persistent_json[persistent_key] = 0
        metric_value = 0

    if metric_entity.metric_type == MetricType.COUNTER or metric_entity.metric_type == MetricType.GAUGE:
      if label_values is None or len(label_values) == 0:
        if metric_entity.metric_type == MetricType.COUNTER and metric_entity.reset:
          metric_entity.metric.labels('').reset()
        if metric_entity.metric_type == MetricType.GAUGE and metric_entity.reset:
          metric_entity.metric.labels('').set(0)
        metric_entity.metric.labels('').inc(metric_value)
      else:
        if metric_entity.reset:
          if metric_entity.metric_type == MetricType.COUNTER and metric_entity.reset:
            metric_entity.metric.labels(*label_values).reset()
          if metric_entity.metric_type == MetricType.GAUGE and metric_entity.reset:
            metric_entity.metric.labels(*label_values).set(0)
        metric_entity.metric.labels(*label_values).inc(metric_value)
    else:
      if label_values is None or len(label_values) == 0:
        metric_entity.metric.observe(metric_value)
      else:
        metric_entity.metric.labels(*label_values).observe(metric_value)
  except Exception as e:
    log.error("添加指标信息异常: %s" % e)
  _lock.release()


def _init_all_metrics():
  Metric(MetricType.GAUGE, 'gomyck', ['g_label1', 'g_label2'], persistent=True, reset=True)

# if __name__ == '__main__':
#   init()
#   import random
#   while True:
#     opt('data_reported_time', ['123', '123'], random.randint(1, 10))
#     opt('data_received_time', ['123', '123'], random.randint(1, 10))
#     opt('data_insert_time',   ['123', '123'], random.randint(1, 10))
#     time.sleep(1)
