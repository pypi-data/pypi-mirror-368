import requests


def get(url, params=None, headers=None):
  result = ""
  try:
    response = requests.get(url, params=params, headers=headers, timeout=60, verify=False)
    response.raise_for_status()
    if response.status_code == 200:
      result = response.content
  except Exception as e:
    print("GET请求异常:", e)
  if isinstance(result, bytes): return result.decode('utf-8')
  return result


def post(url, data=None, json=None, headers=None, files=None):
  result = ""
  response = requests.post(url, data=data, json=json, files=files, headers=headers, timeout=600, verify=False)
  response.raise_for_status()
  if response.status_code == 200:
    result = response.content
  if isinstance(result, bytes): return result.decode('utf-8')
  return result
