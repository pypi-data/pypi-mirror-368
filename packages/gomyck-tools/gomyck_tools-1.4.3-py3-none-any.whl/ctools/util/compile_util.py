import importlib
import os
import time


def code_to_pyc(code: str, out_file_path: str):
  file_name = os.path.split(out_file_path)[-1]
  compiled_code = compile(code, file_name, 'exec')
  bytecode = importlib._bootstrap_external._code_to_timestamp_pyc(compiled_code, time.time(), len(code))
  with open(out_file_path, 'wb') as f:
    f.write(bytecode)


def file_to_pyc(file_path: str, out_file_path: str):
  with open(file_path, 'r') as f:
    code = f.read()
  if code:
    code_to_pyc(code, out_file_path)
