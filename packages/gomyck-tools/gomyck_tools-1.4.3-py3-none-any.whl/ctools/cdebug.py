import subprocess
import sys
import threading
from datetime import datetime
from queue import Queue, Empty


class ProgramInterceptor:
  def __init__(self, command):
    self.command = command
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    self.log_filename = f"program_io_log_{timestamp}.txt"
    self.process = None
    self.log_queue = Queue()

  def start(self):
    if self.command[0] == "--log":
      # 启动日志写入线程
      log_thread = threading.Thread(target=self._write_log_thread, daemon=True)
      log_thread.start()
      self.command = self.command[1:]
    # 启动子进程
    self.process = subprocess.Popen(
      self.command,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      bufsize=0,
      universal_newlines=True
    )

    # 记录初始信息
    self._enqueue_log("header", f"Command: {' '.join(self.command)}")
    self._enqueue_log("header", f"Start time: {datetime.now()}")
    self._enqueue_log("header", "-" * 50)

    # 启动输出转发线程
    stdout_thread = threading.Thread(
      target=self._forward_stream,
      args=(self.process.stdout, sys.stdout, "stdout"),
      daemon=True
    )
    stderr_thread = threading.Thread(
      target=self._forward_stream,
      args=(self.process.stderr, sys.stderr, "stderr"),
      daemon=True
    )

    stdout_thread.start()
    stderr_thread.start()

    # 主线程处理输入转发
    try:
      while True:
        if self.process.poll() is not None:
          break

        # 读取用户输入
        try:
          user_input = sys.stdin.readline()
          if not user_input:  # EOF
            break

          # 记录输入
          self._enqueue_log("stdin", user_input)

          # 转发到子进程
          try:
            self.process.stdin.write(user_input)
            self.process.stdin.flush()
          except (BrokenPipeError, OSError):
            break

        except KeyboardInterrupt:
          break

    finally:
      # 清理工作
      self.process.terminate()

      # 等待所有输出处理完成
      stdout_thread.join(timeout=1)
      stderr_thread.join(timeout=1)

      # 记录结束信息
      self._enqueue_log("header", "-" * 50)
      self._enqueue_log("header", f"End time: {datetime.now()}")
      self._enqueue_log("header", f"Exit code: {self.process.returncode}")

      # 等待日志写入完成
      self.log_queue.put(None)  # 结束信号
      if hasattr(self, "log_thread") and isinstance(self.log_thread, threading.Thread):
        if self.log_thread.is_alive():
          self.log_thread.join(timeout=2)

  def _forward_stream(self, source, target, stream_name):
    """转发数据流并记录"""
    for line in iter(source.readline, ''):
      # 转发到目标
      target.write(line)
      target.flush()

      # 记录输出
      self._enqueue_log(stream_name, line)

  def _enqueue_log(self, stream_type, content):
    """将日志内容放入队列"""
    self.log_queue.put((stream_type, content))

  def _write_log_thread(self):
    """日志写入线程"""
    with open(self.log_filename, 'w', encoding='utf-8') as log_file:
      while True:
        try:
          item = self.log_queue.get(timeout=0.5)
          if item is None:  # 结束信号
            break

          stream_type, content = item

          if stream_type == 'stderr': continue

          if stream_type == "header":
            log_file.write(content + "\n")
          else:
            direction = ">>>" if stream_type == "stdin" else "<<<"
            log_file.write(f"{direction} {stream_type}: {content}")

          log_file.flush()

        except Empty:
          if self.process.poll() is not None:
            continue


def main():
  if len(sys.argv) < 2:
    print("Usage: cdebug.py <program> [args...]")
    print("Example: cdebug.py python script.py arg1 arg2")
    sys.exit(1)
  interceptor = ProgramInterceptor(sys.argv[1:])
  interceptor.start()


if __name__ == "__main__":
  main()
