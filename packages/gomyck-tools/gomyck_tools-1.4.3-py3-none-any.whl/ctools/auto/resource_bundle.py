import hashlib
import io
import json
import os
import shutil
import zipfile
from base64 import b64decode
from base64 import b64encode

from Crypto.Hash import MD5
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from ctools import sys_log, application, path_info

log = sys_log.flog


def data_layout(manifest: dict):
  """
  数据重新排版
  :param manifest:
  :return:
  """
  data = ""
  for key in sorted(manifest):
    if key != "signature":
      data += "%s=%s," % (key, manifest[key])
  return data[:-1]


def get_md5_sum(data):
  return hashlib.md5(data + "gomyck-daning".encode()).hexdigest()


def signature(manifest: dict):
  """
  定义签名函数，能够使用指定的私钥对数据文件进行签名，并将签名结果输出到文件返回
  :param manifest: 元数据字典
  :return:
  """
  with open(path_info.get_app_path() + '/keys/resource_private_key.pem', 'r') as pri:
    private_key = RSA.import_key(pri.read())
    digest = MD5.new(data_layout(manifest).encode('utf-8'))
    return b64encode(pkcs1_15.new(private_key).sign(digest)).decode()


def sign_verify(manifest: dict, sign_val: str):
  """
  定义签名验证函数，能够使用指定的公钥对任务2中的签名文件进行验证，返回验证结果
  :param manifest: 元数据字典
  :param sign_val: 对比的签名值
  :return:
  """
  with open(path_info.get_app_path() + '/keys/resource_public_key.pem', 'r') as pub:
    public_key = RSA.import_key(pub.read())
    digest = MD5.new(data_layout(manifest).encode('utf-8'))
    try:
      pkcs1_15.new(public_key).verify(digest, b64decode(sign_val))
      return True
    except:
      return False


def unpack_resource(resource_name, file):
  """
  解压资源包并验证包的完整性和签名
  :param resource_name:
  :param file:
  :return:
  """
  message = None
  file_md5_sum = os.path.splitext(resource_name)[0].split('-')[-1]
  if file_md5_sum != get_md5_sum(file.read()):
    message = "资源包已损坏, 请重新打包"
  else:
    manifest = {}
    with zipfile.ZipFile(file, 'r') as zf:
      for file in zf.filelist:
        if file.filename == "manifest.json":
          manifest = json.loads(zf.read(file.filename))
          break
      # 校验签名
      if sign_verify(manifest, manifest.get('signature')):
        resource_path = os.path.join(application.Upload.source_pkg_path, manifest['name'])
        shutil.rmtree(resource_path, ignore_errors=True)
        zf.extractall(resource_path)
      else:
        message = "资源包签名校验未通过"
  return message


def pack_resource(resource_path):
  """
  压缩打包资源包为zip文件
  :param resource_path:
  :return:
  """
  file_name = None
  buffer = io.BytesIO()
  manifest_path = os.path.join(resource_path, 'manifest.json')
  if os.path.exists(manifest_path):
    resource_name = os.path.split(resource_path)[-1]
    with open(manifest_path, mode="r", encoding='utf-8') as f:
      manifest = json.loads(f.read())
      manifest["signature"] = signature(manifest)
    with open(manifest_path, mode="w", encoding='utf-8') as f:
      f.write(json.dumps(manifest, indent=2, ensure_ascii=False))

    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED, allowZip64=False) as zf:
      for dir_path, dir_names, file_names in os.walk(resource_path):
        for filename in file_names:
          filepath = os.path.join(dir_path, filename)
          arcname = os.path.join(dir_path.split(resource_name)[-1], filename)
          zf.write(filepath, arcname=arcname)
    buffer.seek(0)
    md5_sum = get_md5_sum(buffer.getvalue())
    file_name = "%s-%s.zip" % (resource_name, md5_sum)
  else:
    log.info("资源包%s不存在manifest.json元数据文件， 无法打包" % resource_path)
  return file_name, buffer
