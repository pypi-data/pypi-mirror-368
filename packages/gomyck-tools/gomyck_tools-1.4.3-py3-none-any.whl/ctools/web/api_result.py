from ctools import cjson

cjson.str_value_keys = [
  "obj_id",
]


class _ResEnum(object):
  def __init__(self, code: int, message: str):
    self.code = code
    self.message = message

  def __eq__(self, o: object) -> bool:
    return self.code == o


class R(object):
  class Code:

    @staticmethod
    def cus_code(code, msg):
      return _ResEnum(code, msg)

    SUCCESS = _ResEnum(200, "成功")
    FAIL = _ResEnum(400, "失败")
    ERROR = _ResEnum(500, "异常")

  def __init__(self, code: int, message: str, data=""):
    self.code = code
    self.message = message
    self.data = data

  def _to_json_str(self):
    return cjson.unify_to_str(cjson.dumps(self))

  @staticmethod
  def parser(r_json: str):
    return R(**cjson.loads(r_json))

  @staticmethod
  def ok(data=None, resp=Code.SUCCESS, msg=None, to_json_str=True):
    if not to_json_str:
      return R(resp.code, msg if msg is not None else resp.message, data)
    return R(resp.code, msg if msg is not None else resp.message, data)._to_json_str()

  @staticmethod
  def fail(msg=None, resp=Code.FAIL, data=None, to_json_str=True):
    if not to_json_str:
      return R(resp.code, msg if msg is not None else resp.message, data)
    return R(resp.code, msg if msg is not None else resp.message, data)._to_json_str()

  @staticmethod
  def error(msg=None, resp=Code.ERROR, data=None, to_json_str=True):
    if not to_json_str:
      return R(resp.code, msg if msg is not None else resp.message, data)
    return R(resp.code, msg if msg is not None else resp.message, data)._to_json_str()
