import os

from ctools import cdate
from ctools import sys_log

log = sys_log.flog

"""
文件上传服务
"""


def save(upload, output_dir: str, file_name: str = None):
  """
  根据上传的upload对象保存上传文件
  :param output_dir:
  :param upload:
  :param file_name:
  :return: 保存文件路径
  """

  # 确保文件夹存在
  os.makedirs(output_dir, exist_ok=True)

  unique_filename = file_name
  if not unique_filename:
    # 生成不重复的文件名，加上时间戳
    file_name, ext = os.path.splitext(upload.raw_filename)
    timestamp = cdate.get_time()
    unique_filename = f'{file_name}_{timestamp}{ext}'
  else:
    dot_index = unique_filename.find(".")
    suffix = os.path.splitext(upload.raw_filename)[-1]
    if dot_index != -1:
      unique_filename = os.path.splitext(unique_filename)[0] + suffix
    else:
      unique_filename = unique_filename + suffix
  save_path = os.path.join(output_dir, unique_filename)
  upload.save(save_path, overwrite=True)
  log.info("上传文件成功: %s" % save_path)
  return file_name, save_path
