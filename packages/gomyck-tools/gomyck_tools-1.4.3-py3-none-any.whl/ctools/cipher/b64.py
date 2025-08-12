import base64


def encode(param: str):
  return base64.b64encode(param.encode('UTF-8')).decode('UTF-8')


def decode(param: str):
  return base64.b64decode(param.encode('UTF-8')).decode('UTF-8')
