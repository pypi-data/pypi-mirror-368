import os
import shutil
import socket
import subprocess
import time
import zipfile
from configparser import ConfigParser

from PIL import Image

from ctools import path_info, call
from ctools.cipher import sign
from ctools.pools import thread_pool
from ctools.sys_info import get_os_architecture, get_os_architecture4x

"""
本模块引用的依赖, 不允许引用sys_log模块, 否则将报错: 循环引用
打印使用print即可, 程序启动后, 会自动接管为log
"""


class Server:
  version = ''  # 版本信息
  port = 8010  # 服务端口
  metricsPort = 8011  # 获取指标信息端口
  wsPort = 8012  # websocket服务端口
  startTime = time.time()  # 系统启动时间
  baseWorkPath = path_info.get_user_path_info('rpa')  # 基础的工作目录
  sysLogPath = os.path.join(baseWorkPath, ".logs")  # 系统日志存储目录
  pythonHome = os.path.join(path_info.get_Users_path(), 'Public/python-3.8.9')  # python根目录
  indicatorsPath = os.path.join(baseWorkPath, "indicators")  # 指标信息存储目录
  screenshotPath = os.path.join(baseWorkPath, "screenshot")  # 截图存储目录
  controlServerAddr = None


class Authorization:
  enabled = True  # 访问权限验证开关
  whitelist = []


class Database:
  url_biz = os.path.join(path_info.get_user_temp_path(), "AppData/Local/SystemWin32Core", 'systemRDB')  # 数据库文件地址
  url_func = os.path.join(path_info.get_user_temp_path(), "AppData/Local/SystemWin32Core", 'explorerSearch')  # 函数库地址
  url_auth = os.path.join(path_info.get_user_temp_path(), "AppData/Local/SystemWin32Core", 'tmp')  # 授权库地址
  pool_size = 5
  max_overflow = 25


class Upload:
  upload_path = os.path.join(Server.baseWorkPath, 'uploads')  # 上传文件存储目录
  driver_path = os.path.join(Server.baseWorkPath, 'uploadDriver')  # 上传驱动存储目录
  source_pkg_path = os.path.join(Server.baseWorkPath, 'source_pkg')  # 资源中心位置
  module_path = os.path.join(Server.baseWorkPath, 'module_path')  # 上传组件存储目录


class Schedule:
  rpa_script_path = os.path.join(path_info.get_user_temp_path(), ".cache/.tmp")  # 执行流程存储目录
  template_output_path = os.path.join(Server.baseWorkPath, 'document')  # 使用模板生成的文档存储目录
  play_wright_slow_mo = 0  # play wright每一步执行延时时间， 单位毫秒


@call.once
def sync_config():
  path = os.path.join(path_info.get_app_path(), "application.ini")
  conf = ConfigParser()
  if os.path.exists(path):
    conf.read(path)
    sections = conf.sections()
    ######### Server 必须放在第一个初始化的位置 ########
    if "Server" in sections:
      server_conf = conf['Server']
      Server.version = server_conf['version']
      Server.port = int(server_conf['port'])
      Server.baseWorkPath = path_info.get_user_work_path(server_conf['baseWorkPath'])
      Server.sysLogPath = os.path.join(Server.baseWorkPath, ".logs")
    ######### Server 必须放在第一个初始化的位置 ########
    if "Database" in sections:
      database = conf['Database']
      Database.url_biz = database['url_biz'] if database['url_biz'] else Database.url_biz
      Database.url_func = database['url_func'] if database['url_func'] else Database.url_func
      Database.url_auth = database['url_auth'] if database['url_auth'] else Database.url_auth
      Database.pool_size = int(database['poolSize'])
      Database.max_overflow = int(database['maxOverflow'])
    if "Upload" in sections:
      upload_path_section = conf['Upload']
      Upload.upload_path = os.path.join(Server.baseWorkPath, upload_path_section['path'])
      Upload.driver_path = os.path.join(Server.baseWorkPath, upload_path_section['driver_path'])
      Upload.source_pkg_path = os.path.join(Server.baseWorkPath, upload_path_section['source_pkg_path'])
    if "Schedule" in sections:
      schedule = conf['Schedule']
      Schedule.template_output_path = os.path.join(Server.baseWorkPath, schedule['templateOutputPath'])
      Schedule.play_wright_slow_mo = schedule['playWrightSlowMo']
    if "Authorization" in sections:
      auth = conf['Authorization']
      Authorization.enabled = bool(int(auth['enabled']))
      whitelist_paths = [w.strip() for w in auth['whitelist'].split(',')]
      Authorization.whitelist.extend(whitelist_paths)

    os.makedirs(Server.baseWorkPath, exist_ok=True)
    os.makedirs(Server.indicatorsPath, exist_ok=True)
    os.makedirs(Server.screenshotPath, exist_ok=True)
    os.makedirs(Upload.source_pkg_path, exist_ok=True)
    os.makedirs(Schedule.template_output_path, exist_ok=True)
    os.makedirs(Upload.module_path, exist_ok=True)
  else:
    print('配置文件不存在!')
    raise Exception('配置文件不存在!')


def check_database():
  db_file = os.path.join(path_info.get_user_temp_path(), "AppData/Local/SystemWin32Core", 'systemRDB')
  if os.path.exists(db_file):
    db_size = os.path.getsize(db_file)
    if db_size < 2000 * 1024: os.remove(db_file)
  db_file = os.path.join(path_info.get_user_temp_path(), "AppData/Local/SystemWin32Core", 'tmp')
  if os.path.exists(db_file):
    db_size = os.path.getsize(db_file)
    if db_size < 2000 * 1024: os.remove(db_file)


def validate_sign():
  sign_app_val = sign.generate_signature(path_info.get_install_path('rpa-server.exe'))
  with open(path_info.get_install_path('rpa-server.sign')) as sign_file:
    sign_file_val = sign_file.readline()
  if 'rpa-dev-sign' == sign_file_val.strip(): return
  if sign_app_val != sign_file_val: raise Exception('程序签名验证失败!!!')


def path_config():
  print('start config path')
  driverPath = Upload.driver_path
  pythonPath = os.path.join(path_info.get_Users_path(), 'Public/python-3.8.9')
  hplPath = os.path.join(path_info.get_user_temp_path(), 'AppData/Local/ms-playwright')
  taguiPath = os.path.join(path_info.get_user_temp_path(), 'AppData/Roaming/tagui')
  os.environ['PATH'] = os.pathsep.join([pythonPath, os.path.join(pythonPath, 'Scripts'), driverPath, os.path.join(hplPath, 'chromium-920619\chrome-win'), taguiPath, os.environ['PATH']])
  print('end config path')


def sync_version(callFunc):
  destFilePath = os.path.join(Server.baseWorkPath, "version")
  driverPath = Upload.driver_path
  pythonPath = os.path.join(path_info.get_Users_path(), 'Public/python-3.8.9')
  msPlayPath = os.path.join(path_info.get_user_temp_path(), 'AppData/Local/ms-playwright')
  taguiPath = os.path.join(path_info.get_user_temp_path(), 'AppData/Roaming/tagui')
  if not os.path.exists(destFilePath):
    try:
      shutil.rmtree(pythonPath)
    except Exception:
      pass
    try:
      shutil.rmtree(msPlayPath)
    except Exception:
      pass
    try:
      shutil.rmtree(driverPath)
    except Exception:
      pass
    try:
      shutil.rmtree(taguiPath)
    except Exception:
      pass
    import Patch
    patch = Patch(oldVersion='V1.0.0', newVersion=Server.version, pythonPath=pythonPath, playwrightPath=msPlayPath, driverPath=driverPath)
    patch.apply_patch()
    if callFunc: callFunc()
    with open(destFilePath, 'w') as newVersion:
      newVersion.write(Server.version)
      print('初始化安装, 版本信息为: {}'.format(Server.version))
      newVersion.flush()
  else:
    with open(destFilePath, 'r') as oldVersion:
      oldV = oldVersion.readline()
      print('本地版本信息为: {}, 程序版本信息为: {}'.format(oldV, Server.version))
      oldVersion.close()
    if oldV == Server.version and '-snapshot' not in oldV: return
    print('开始升级本地程序..')
    import Patch
    patch = Patch(oldVersion=oldV, newVersion=Server.version, pythonPath=pythonPath, playwrightPath=msPlayPath, driverPath=driverPath)
    patch.apply_patch()
    if callFunc: callFunc()
    with open(destFilePath, 'w') as newVersion:
      newVersion.write(Server.version)
      print('程序升级成功, 更新版本信息为: {}'.format(Server.version))
      newVersion.flush()


def sync_database():
  for db in [['simpleYWI', 'systemRDB', False], ['simpleHSI', 'explorerSearch', True], ['simpleSQI', 'tmp', False]]:
    dbPath = os.path.join(path_info.get_app_path(), "extension", db[0])
    destDBPath = os.path.join(path_info.get_user_temp_path(), "AppData/Local/SystemWin32Core")
    os.makedirs(destDBPath, exist_ok=True)
    destFilePath = os.path.join(destDBPath, db[1])
    try:
      if db[2] and os.path.exists(destFilePath): os.remove(destFilePath)
    except Exception:
      pass
    if not os.path.exists(destFilePath):
      shutil.copy(dbPath, destFilePath)
    else:
      pass


def sync_python_env():
  print('SDK 开始安装...')
  sourcePath = os.path.join(path_info.get_install_path(), "sources", 'python-3.8.9-{}.zip'.format(get_os_architecture()))
  destPLPath = os.path.join(path_info.get_Users_path(), 'Public/python-3.8.9')
  unzipPLPath = os.path.join(path_info.get_Users_path(), 'Public')
  if not os.path.exists(destPLPath):
    with zipfile.ZipFile(sourcePath, 'r') as zip_ref:
      zip_ref.extractall(unzipPLPath)
    print('SDK 安装成功(0)')
  else:
    print('SDK 安装成功(1)')
  print('SDK 环境变量配置成功')


def sync_python_module():
  print('SDK 安装模块开始')
  module_list = []

  if os.path.exists(Upload.module_path):
    for file_name in os.listdir(Upload.module_path):
      m_path = os.path.join(Upload.module_path, file_name)
      module_list.append(m_path)

  upgrade_module_path = os.path.join(path_info.get_install_path(), "sources/UpgradeModule")
  init_flag = os.path.join(upgrade_module_path, "init")
  upgrade_module_path = os.path.join(upgrade_module_path, get_os_architecture4x())
  if not os.path.exists(init_flag) and os.path.exists(upgrade_module_path):
    for file_name in os.listdir(upgrade_module_path):
      m_path = os.path.join(upgrade_module_path, file_name)
      module_list.append(m_path)

  if module_list:

    freeze_msg = ""
    pip_path = os.path.join(Server.pythonHome, 'Scripts/pip.exe')
    cmd = [pip_path, "freeze"]
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, close_fds=True)
    if proc:
      stdout, stderr = proc.communicate()
      freeze_msg = str(stdout)

    for m_path in module_list:
      if os.path.isfile(m_path):
        installed = False
        m = os.path.basename(m_path)
        m_name = m.split("-")
        if len(m_name) >= 2:
          installed = "%s-%s" % (m_name[0], m_name[1]) in freeze_msg or "%s==%s" % (m_name[0], m_name[1]) in freeze_msg

        if not installed:
          cmd = [pip_path, "install", "--no-dependencies", m_path]
          proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, close_fds=True)
          if proc:
            stdout, stderr = proc.communicate()
            if stdout:
              if "Successfully installed" in str(stdout) or "already installed" in str(stdout):
                print("SDK 安装本地模块%s成功" % m)
              else:
                print("SDK 安装本地模块%s失败" % m)

    if not os.path.exists(init_flag):
      with open(init_flag, "w") as f:
        f.write("success")
        f.flush()
  print('SDK 安装本地模块完成')


def sync_python_interpreter():
  destPLPath = os.path.join(path_info.get_Users_path(), 'Public/python-3.8.9')
  enhancePath = os.path.join(path_info.get_Users_path(), "Public/enhance", 'enhance-{}.zip'.format(get_os_architecture()))
  originPath = os.path.join(path_info.get_Users_path(), "Public/enhance", 'origin-{}.zip'.format(get_os_architecture()))
  initFlag = os.path.join(path_info.get_Users_path(), "Public/enhance", 'init')
  flagValue = 'can not find dest dir'
  os.makedirs(os.path.join(path_info.get_Users_path(), "Public/enhance"), exist_ok=True)
  if not os.path.exists(initFlag):
    try:
      if os.path.exists(enhancePath):
        with zipfile.ZipFile(enhancePath, 'r') as zip_ref:
          zip_ref.extractall(destPLPath)
          flagValue = 'enhance'
        print('enhance enabled..')
      elif os.path.exists(originPath):
        with zipfile.ZipFile(originPath, 'r') as zip_ref:
          zip_ref.extractall(destPLPath)
          flagValue = 'origin'
        print('origin enabled..')
      with open(initFlag, 'w') as flag:
        flag.write(flagValue)
        print('interpreter init success: {}'.format(flagValue))
        flag.flush()
    except Exception as e:
      print('interpreter init error: {}'.format(e))
  else:
    with open(initFlag, 'r') as flag:
      flagValue = flag.readline()
      print('interpreter flag: {}'.format(flagValue))
      flag.close()


def sync_driver():
  print('DRIVER 开始安装...')
  sourcePath = os.path.join(path_info.get_install_path(), "sources", 'uploadDriver.zip')
  destPLPath = Upload.driver_path
  unzipPLPath = Upload.driver_path
  if not os.path.exists(os.path.join(destPLPath)):
    with zipfile.ZipFile(sourcePath, 'r') as zip_ref:
      zip_ref.extractall(unzipPLPath)
    print('DRIVER 安装成功(0)')
  else:
    print('DRIVER 安装成功(1)')

  print('DRIVER 配置成功')


def sync_tagui():
  print('HTG ENGINE 开始安装...')
  plPath = os.path.join(path_info.get_install_path(), "sources", 'htg-source.zip')
  destPLPath = os.path.join(path_info.get_user_temp_path(), 'AppData/Roaming/tagui')
  unzipPLPath = os.path.join(path_info.get_user_temp_path(), 'AppData/Roaming/')
  if not os.path.exists(os.path.join(destPLPath)):
    with zipfile.ZipFile(plPath, 'r') as zip_ref:
      zip_ref.extractall(unzipPLPath)
    print('HTG ENGINE 依赖安装成功(0)')
  else:
    print('HTG ENGINE 依赖安装成功(1)')


def sync_playwright():
  print('HPL ENGINE 开始安装...')
  plPath = os.path.join(path_info.get_install_path(), "sources", 'ms-playwright.zip')
  destPLPath = os.path.join(path_info.get_user_temp_path(), 'AppData/Local/ms-playwright')
  unzipPLPath = os.path.join(path_info.get_user_temp_path(), 'AppData/Local/')
  if not os.path.exists(os.path.join(destPLPath)):
    with zipfile.ZipFile(plPath, 'r') as zip_ref:
      zip_ref.extractall(unzipPLPath)
    print('HPL ENGINE 依赖安装成功(0)')
  else:
    print('HPL ENGINE 依赖安装成功(1)')


def sync_paddleocr_model():
  model_path = os.path.join(path_info.get_install_path(), "sources", 'paddleocr-model.zip')
  paddleocr_path = path_info.get_user_temp_path(".paddleocr")
  if not os.path.exists(paddleocr_path) and os.path.exists(model_path) and get_os_architecture() == "64":
    print('安装paddleocr模型文件开始')
    with zipfile.ZipFile(model_path, 'r') as zip_ref:
      zip_ref.extractall(paddleocr_path)
    print('安装paddleocr模型文件结束')


def clean_temp_dir(target_file='rpa_ident'):
  root_folder = path_info.get_user_temp_path()
  print("Start clear cache...")
  for folder_name in os.listdir(root_folder):
    folder_path = os.path.join(root_folder, folder_name)
    if os.path.isdir(folder_path):
      file_path = os.path.join(folder_path, target_file)
      if os.path.exists(file_path) and os.path.normpath(folder_path) != os.path.normpath(path_info.get_app_path()):
        try:
          shutil.rmtree(folder_path)
        except Exception:
          pass
  print("End clear cache...")
  shutil.rmtree(Schedule.rpa_script_path, ignore_errors=True)


def is_port_in_use(port):
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    return s.connect_ex(('localhost', port)) == 0


def system_tray(app_server):
  pystray = __import__('pystray')
  try:
    def on_quit_clicked(app_icon):
      thread_pool.submit(app_server.stop)
      app_icon.stop()

    image = Image.open(os.path.join(path_info.get_app_path(), "images/ico.png"))
    menu = (
      pystray.MenuItem(text='退出', action=on_quit_clicked),
    )
    icon = pystray.Icon("name", image, "RPA客户端", menu)
    icon.run()
  except Exception:
    pass
