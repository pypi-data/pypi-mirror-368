import jsonpickle

# 需要转换成str的属性
str_value_keys = []
jsonpickle.set_preferred_backend('json')
jsonpickle.set_encoder_options('json', ensure_ascii=False)
jsonpickle.set_decoder_options('json')


def dumps(obj, **kwargs) -> str:
  """
  将对象转换为json字符串
  :param obj: 对象
  :return: json 字符串
  """
  # indent = 2 可以美化输出
  if obj is None: return None
  if type(obj) == str: return obj
  return f'{jsonpickle.encode(obj, unpicklable=False, make_refs=False, **kwargs)}'


def loads(json_str: str, **kwargs) -> dict:
  """
  将json字符串转换为对象
  :param json_str: json 字符串
  :return: 对象
  """
  return jsonpickle.decode(json_str, **kwargs)


def unify_to_str(json_str: str) -> str:
  if not str_value_keys and len(str_value_keys) == 0: return json_str
  obj = loads(json_str)
  if isinstance(obj, list):
    _handle_list(obj)
  elif isinstance(obj, dict):
    _handle_dict(obj)
  return dumps(obj)


def _handle_list(data):
  for o in data:
    if isinstance(o, list):
      _handle_list(o)
    elif isinstance(o, dict):
      _handle_dict(o)


def _handle_dict(data):
  for k, v in data.items():
    if isinstance(v, list):
      _handle_list(v)
    elif isinstance(v, dict):
      _handle_dict(v)
    elif k in str_value_keys:
      try:
        data[k] = str(v)
      except Exception:
        pass
