import _thread
import queue
import time

from winpty import PtyProcess


# 伪终端交互


class Code:
  SUCCESS = 200
  FAIL = 201
  PART = 206


class PtyTools:
  def __init__(self, cmd, prefix: str = ""):
    self._process = PtyProcess.spawn(cmd)
    self._read_queue = queue.Queue()
    self._prefix = prefix
    self._is_enable = False

  def _read(self):
    try:
      while True:
        msg = self._process.readline()
        self._is_enable = True
        if msg and self._prefix not in msg[:len(self._prefix)]:
          self._read_queue.put(msg)
        elif self._is_exit():
          break
    except Exception:
      pass

  def _is_exit(self):
    return self._process.exitstatus is not None

  def run(self):
    _thread.start_new_thread(self._read, ())
    while not self._is_enable:
      time.sleep(1)

  def read(self, end_str: str = None, is_async=False, timeout: int = 1):
    code = Code.SUCCESS
    content = ""
    start_time = time.time()
    while True:
      if not self._read_queue.empty():
        line = self._read_queue.get()
        content += line
        start_time = time.time()
        if end_str is not None and end_str in line:
          break
        if is_async:
          code = Code.PART
          break
      else:
        if time.time() - start_time >= timeout:
          break
        if self._is_exit():
          code = Code.FAIL
          break
      time.sleep(0.1)
    return code, content

  def send(self, msg, timeout: int = 0.5):
    self._process.write('%s\r\n' % msg)
    return self.read(timeout=timeout)

  def close(self):
    self._process.close(force=True)
