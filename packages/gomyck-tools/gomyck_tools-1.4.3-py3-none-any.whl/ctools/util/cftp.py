#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/1/24 08:53'

import io
import time
from ftplib import FTP, error_perm, error_temp


class CFTP:
  """
  with open('xx/xx.md', 'rb') as file:
    ftp_host = 'x.x.x.x'
    ftp_username = 'x'
    ftp_password = 'x'
    CFTP(ftp_host, ftp_username, ftp_password).upload_file_to_ftp('xx.md', file)
  """

  def __init__(self, host, username, password, timeout=30, max_retries=3, retry_delay=5):
    self.host = host
    self.username = username
    self.password = password
    self.ftp: FTP = None
    self.timeout = timeout
    self.max_retries = max_retries
    self.retry_delay = retry_delay

  def upload_file_to_ftp(self, file_name, file: io.BytesIO, ftp_directory='/'):
    if not file_name: raise Exception('文件名不能为空')
    if not file: raise Exception('文件不能为空')
    for attempt in range(self.max_retries):
      try:
        if not self.ftp:
          ftp = FTP(self.host, timeout=self.timeout)
          ftp.login(self.username, self.password)
          ftp.set_pasv(True)
          self.ftp = ftp
        try:
          self.ftp.cwd(ftp_directory)
        except error_perm:
          print(f"FTP 目录不存在：{ftp_directory}")
          self.ftp.mkd(ftp_directory)
          print(f"FTP 目录创建成功：{ftp_directory}, 正在切换到目录：{ftp_directory}")
          self.ftp.cwd(ftp_directory)
        print(f"正在上传文件：{file_name}")
        self.ftp.storbinary(f"STOR {file_name}", file)
        self.ftp.quit()
        print(f"文件成功上传到 FTP: {file_name}")
        return
      except (error_perm, error_temp) as e:
        try:
          self.ftp.quit()
        except Exception:
          pass
        self.ftp = None
        print(f"FTP 错误：{e}")
        if attempt < self.max_retries - 1:
          print(f"正在尝试重连... 第 {attempt + 1} 次重试...")
          time.sleep(self.retry_delay)
        else:
          print("重试次数已用尽，上传失败。")
          raise
      except Exception as e:
        try:
          self.ftp.quit()
        except Exception:
          pass
        self.ftp = None
        print(f"连接或上传出现异常：{e}")
        if attempt < self.max_retries - 1:
          print(f"正在尝试重连... 第 {attempt + 1} 次重试...")
          time.sleep(self.retry_delay)
        else:
          print("重试次数已用尽，上传失败。")
          raise
