import os
from urllib.parse import urlencode

from bottle import static_file, HTTPResponse

from ctools import sys_log
from ctools.util import http_util

log = sys_log.flog

"""
文件下载服务
"""


def download(file_path: str, download_name: str = None):
  """
  文件下载
  :param file_path: 静态文件路径
  :param download_name: 下载文件名
  :return:
  """
  if os.path.exists(file_path):
    root_path = os.path.split(file_path)[0]
    file_name = os.path.split(file_path)[1]
    download_filename = urlencode({'filename': download_name or file_name}).split("=")[-1]  # 对文件名进行URL编码
    response = static_file(file_name, root=root_path, download=True)
    # 设置响应头，告诉浏览器这是一个文件下载
    response.headers['Content-Type'] = 'application/octet-stream;charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename={download_filename}'
    log.debug(f"下载文件成功, file_path： {file_path}, file_name： {file_name}, download_name： {download_name}")
  else:
    response = None
    log.info("下载文件失败, 此文件不存在, file_path： %s" % file_path)
  return response


def download_bytes(file_bytes: bytes, download_name: str):
  """
  文件下载
  :param file_bytes: file_bytes
  :param download_name: download_name
  :return:
  """
  download_filename = urlencode({'filename': download_name}).split("=")[-1]  # 对文件名进行URL编码
  # 设置响应头，告诉浏览器这是一个文件下载
  headers = {"Accept-Ranges": "bytes", "Content-Length": len(file_bytes),
             'Content-Type': 'application/octet-stream;charset=utf-8',
             'Content-Disposition': f'attachment; filename={download_filename}'}
  return HTTPResponse(file_bytes, **headers)


def download_url(url: str, save_path: str):
  content = http_util.get(url)
  if content:
    with open(save_path, "wb") as f:
      f.write(content)
  return save_path
