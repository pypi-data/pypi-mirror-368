import os

from sqlalchemy.sql import text

from ctools import path_info
from ctools.database import database

"""
from ctools import patch
def xx():
  print('hello world')
def xx1():
  print('hello world1')
def xx2():
  print('hello world2')
patch_funcs = {
  'V1.0.2': xx,
  'V1.0.3': xx1,
  'V1.1.4': xx2
}
patch.sync_version("kwc", "V1.1.5", patch_funcs)
"""

class Patch:

  def __init__(self, oldVersion, newVersion, patch_func: dict) -> None:
    super().__init__()
    if oldVersion:
      self.oldV = version_to_int(oldVersion)
    else:
      self.oldV = 0
    self.currentV = version_to_int(newVersion)
    self.snapshot = '-snapshot' in newVersion or (oldVersion is not None and '-snapshot' in oldVersion)
    self.patch_func = patch_func

  def apply_patch(self):
    patch_methods = [method for method in self.patch_func.keys() if method and (method.startswith('V') or method.startswith('v'))]
    patch_methods.sort(key=lambda x: version_to_int(x))
    max_method_name = patch_methods[-1]
    exec_max_method = False
    for method_name in patch_methods:
      slVersion = version_to_int(method_name)
      if self.currentV > slVersion >= self.oldV:
        if max_method_name == method_name: exec_max_method = True
        method = self.patch_func[method_name]
        print('start exec patch {}'.format(method_name))
        method()
        print('patch {} update success'.format(method_name))
    if self.snapshot and not exec_max_method:
      print('start exec snapshot patch {}'.format(max_method_name))
      method = self.patch_func[max_method_name]
      method()
      print('snapshot patch {} update success'.format(max_method_name))

def version_to_int(version):
  return int(version.replace('V', '').replace('v', '').replace('.', '').replace('-snapshot', ''))

def run_sqls(sqls):
  with database.get_session() as s:
    for sql in sqls.split(";"):
      try:
        s.execute(text(sql.strip()))
        s.commit()
      except Exception as e:
        print('结构升级错误, 请检查!!! {}'.format(e.__cause__))

def sync_version(app_name, new_version, patch_func: dict):
  destFilePath = os.path.join(path_info.get_user_work_path(".ck/{}".format(app_name), mkdir=True), "version")
  if not os.path.exists(destFilePath):
    patch = Patch(oldVersion=None, newVersion=new_version, patch_func=patch_func)
    patch.apply_patch()
    with open(destFilePath, 'w') as nv:
      nv.write(new_version)
      print('初始化安装, 版本信息为: {}'.format(new_version))
      nv.flush()
  else:
    with open(destFilePath, 'r') as oldVersion:
      oldV = oldVersion.readline()
      print('本地版本信息为: {}, 程序版本信息为: {}'.format(oldV, new_version))
      oldVersion.close()
    if oldV >= new_version and '-snapshot' not in oldV: return
    print('开始升级本地程序..')
    patch = Patch(oldVersion=oldV, newVersion=new_version, patch_func=patch_func)
    patch.apply_patch()
    with open(destFilePath, 'w') as newVersion:
      newVersion.write(new_version)
      print('程序升级成功, 更新版本信息为: {}'.format(new_version))
      newVersion.flush()
