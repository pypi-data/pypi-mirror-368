import hashlib
import os
import platform

from ctools import cjson, path_info
from ctools.cipher import sm_util

MACHINE_KEY = b'EnrGffoorbFyTYoS0902YyT1Fhehj4InpbezIDUuPOg='


class MachineInfo:
  machine_code = None


def get_user():
  import getpass
  return getpass.getuser()


def get_machine_code():
  if MachineInfo.machine_code: return MachineInfo.machine_code
  destPath = os.path.join(path_info.get_user_work_path(), "AppData/Local/machine")
  machine_file = os.path.join(destPath, 'machine_code.mc')
  origin_machine_code = get_origin_machine_code()
  if os.path.exists(machine_file):
    with open(machine_file, 'r') as f:
      file_code = f.readline()
      dec_code = ''
      try:
        dec_code = cjson.loads(sm_util.decrypt_with_sm4(MACHINE_KEY, file_code))
        origin_code = dec_code.get("origin_code")
        if origin_code == origin_machine_code:
          MachineInfo.machine_code = dec_code.get("hash_code")
          print("use current machine code {}".format(MachineInfo.machine_code))
          return MachineInfo.machine_code
      except Exception:
        print('machine code file is error: {} {}'.format(file_code, dec_code))
  hash_machine_code = get_hash_machine_code(origin_machine_code)
  machine_code = {"origin_code": origin_machine_code, "hash_code": hash_machine_code}
  enc_code = sm_util.encrypt_with_sm4(MACHINE_KEY, cjson.dumps(machine_code))
  os.makedirs(destPath, exist_ok=True)
  with open(machine_file, 'w') as f:
    f.write(enc_code)
    f.flush()
  MachineInfo.machine_code = hash_machine_code
  print("init new machine code {}".format(hash_machine_code))
  return MachineInfo.machine_code


def get_origin_machine_code():
  # 获取CPU序列号
  cpu_serial = platform.processor()
  # 获取硬盘序列号
  disk_serial = ''
  if platform.system() == 'Windows':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    volume_serial = ctypes.c_ulonglong(0)
    kernel32.GetVolumeInformationW(
      ctypes.c_wchar_p("C:\\"),
      None,
      0,
      ctypes.pointer(volume_serial),
      None,
      None,
      None,
      0
    )
    disk_serial = str(volume_serial.value)
  combined_info = cpu_serial + disk_serial + '-gomyck'
  return hashlib.md5(combined_info.encode()).hexdigest()


def get_hash_machine_code(origin_code):
  import uuid
  code = origin_code + uuid.uuid1().hex
  machine_code = hashlib.md5(code.encode()).hexdigest()
  return machine_code.upper()


def get_public_ip():
  import requests
  try:
    response = requests.get("https://api.ipify.org?format=json")
    ip = response.json()["ip"]
    return ip
  except Exception as e:
    return f"Failed to get public IP: {e}"


def get_local_ipv4():
  import psutil
  import socket
  interfaces = psutil.net_if_addrs()
  for interface, addresses in interfaces.items():
    for address in addresses:
      if address.family == socket.AF_INET and not address.address.startswith("127."):
        return address.address
  print("Failed to get local IPv4 address, try another way...")
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  try:
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
  except Exception:
    ip = '127.0.0.1'
  finally:
    s.close()
  return ip


def get_remote_ipv4():
  from bottle import request
  try:
    return request.remote_route[0]
  except:
    return '127.0.0.1'


def get_proc_pid_by(cmdline):
  import psutil
  """
  根据命令行信息获取进程pid
  :param cmdline:
  :return:
  """
  pid_list = []
  proc_list = psutil.process_iter()
  for proc in proc_list:
    try:
      cmdline_str = "".join(proc.cmdline())
      if cmdline in cmdline_str:
        pid_list.append(proc.pid)
    except Exception:
      pass
  return pid_list


def get_os_architecture():
  if '64' in platform.machine():
    return '64'
  else:
    return '32'


def get_os_architecture4x():
  if '64' in platform.machine():
    return 'x64'
  else:
    return 'x86'


def get_os_version():
  system = platform.system()
  if system == "Windows":
    version = platform.win32_ver()[0]
    return version
  else:
    return "Unsupported OS"


def get_platform_name():
  version = get_os_version()
  if version == '7':
    return 'win{}{}'.format(version, get_os_architecture4x())
  else:
    return 'win{}'.format(version)
