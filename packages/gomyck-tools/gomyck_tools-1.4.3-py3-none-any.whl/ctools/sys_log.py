import logging
import os
import sys
import time

from ctools import call, path_info

clog: logging.Logger = None
flog: logging.Logger = None

neglect_keywords = [
  "OPTIONS",
]


# 文件日志
@call.once
def _file_log(sys_log_path: str = './', log_level: int = logging.INFO, mixin: bool = False) -> logging:
  try:
    os.mkdir(sys_log_path)
  except Exception:
    pass
  log_file = sys_log_path + os.path.sep + "log-" + time.strftime("%Y-%m-%d-%H", time.localtime(time.time())) + ".log"
  if mixin:
    handlers = [logging.FileHandler(filename=log_file, encoding='utf-8'), logging.StreamHandler()]
  else:
    handlers = [logging.FileHandler(filename=log_file, encoding='utf-8')]
  logging.basicConfig(level=log_level,
                      format='%(asctime)s | %(levelname)-5s | T%(thread)d | %(module)s.%(funcName)s:%(lineno)d: %(message)s',
                      datefmt='%Y%m%d%H%M%S',
                      handlers=handlers)
  logger = logging.getLogger('ck-flog')
  return logger


# 控制台日志
@call.once
def _console_log(log_level: int = logging.INFO) -> logging:
  handler = logging.StreamHandler()
  logging.basicConfig(level=log_level,
                      format='%(asctime)s | %(levelname)-5s | T%(thread)d | %(name)s | %(module)s.%(funcName)s:%(lineno)d: %(message)s',
                      datefmt='%Y%m%d%H%M%S',
                      handlers=[handler])
  logger = logging.getLogger('ck-clog')
  return logger


import io
import logging


class StreamToLogger(io.StringIO):
  def __init__(self, logger: logging.Logger, level: int = logging.INFO):
    super().__init__()
    self.logger = logger
    self.level = level
    self._buffer = ''

  def write(self, message: str):
    if not message:
      return
    self._buffer += message
    if '\n' in self._buffer:
      lines = self._buffer.splitlines(keepends=False)
      for line in lines:
        if line.strip():
          try:
            self.logger.log(self.level, line.strip(), stacklevel=3)
          except Exception:
            self.logger.log(self.level, line.strip())
      self._buffer = ''

  def flush(self):
    if self._buffer.strip():
      try:
        self.logger.log(self.level, self._buffer.strip(), stacklevel=3)
      except Exception:
        self.logger.log(self.level, self._buffer.strip())
    self._buffer = ''

  def fileno(self):
    return sys.__stdout__.fileno()


@call.init
def _init_log() -> None:
  global flog, clog
  flog = _file_log(path_info.get_user_work_path(".ck/ck-py-log", mkdir=True), mixin=True, log_level=logging.DEBUG)
  clog = _console_log()
  sys.stdout = StreamToLogger(flog, level=logging.INFO)
  sys.stderr = StreamToLogger(flog, level=logging.ERROR)


def setLevel(log_level=logging.INFO):
  flog.setLevel(log_level)
  clog.setLevel(log_level)
