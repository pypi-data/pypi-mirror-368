#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/1/24 08:48'

import io
import os
import time

import pyzipper

"""
  target_directory = '/Users/haoyang/Desktop/知识库文件'
  zip_password = None
  process_directory_to_single_zip(target_directory, zip_password, "knowledge_base")

  files_to_compress = [
    '/path/to/file1.txt',
    '/path/to/file2.pdf',
    '/path/to/file3.jpg'
  ]
  output_directory = '/Users/haoyang/Desktop'
  compress_specific_files(files_to_compress, output_directory, zip_password, "my_files")
"""


def create_zip_with_files(file_dict, password=None) -> io.BytesIO:
  """Compress multiple files into a single password-protected ZIP archive in memory.
  Args:
      file_dict: Dictionary of {filename: file_content} pairs
                 filename = os.path.relpath(file_path, start=root_dir) # 相对路径获取, 用于在 zip 内的路径定位
      password: Optional password for the ZIP file
  Returns:
      BytesIO object containing the ZIP file
  """
  zip_buffer = io.BytesIO()
  try:
    if password:
      with pyzipper.AESZipFile(zip_buffer, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zipf:
        zipf.setpassword(password.encode('utf-8'))
        for filename, content in file_dict.items():
          zipf.writestr(filename, content)
    else:
      with pyzipper.ZipFile(zip_buffer, 'w', compression=pyzipper.ZIP_DEFLATED) as zipf:
        for filename, content in file_dict.items():
          zipf.writestr(filename, content)
    zip_buffer.seek(0)
    return zip_buffer
  except Exception as e:
    zip_buffer.close()
    raise e


def process_directory_to_single_zip(root_dir, password=None, zip_name=None):
  """Walk through directory and compress all files into a single ZIP.
  Args:
      root_dir: Root directory to scan for files
      password: Optional password for the ZIP file
      zip_name: Base name for the ZIP file (without extension)
  """
  file_dict = {}
  for dirpath, _, filenames in os.walk(root_dir):
    for filename in filenames:
      file_path = os.path.join(dirpath, filename)
      try:
        with open(file_path, 'rb') as f:
          rel_path = os.path.relpath(file_path, start=root_dir)
          file_dict[rel_path] = f.read()
      except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
  if not file_dict:
    print("No files found to compress.")
    return

  try:
    zip_buffer = create_zip_with_files(file_dict, password)
    timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    if zip_name:
      base_name = f"{zip_name}_{timestamp}.zip"
    else:
      base_name = f"archive_{timestamp}.zip"
    output_path = os.path.join(root_dir, base_name)
    with open(output_path, 'wb') as out_file:
      out_file.write(zip_buffer.read())
    print(f"Created single archive: {output_path}")
  except Exception as e:
    print(f"Error creating ZIP archive: {str(e)}")
  finally:
    if 'zip_buffer' in locals(): zip_buffer.close()


def compress_specific_files(file_paths: [], output_dir: str, password=None, zip_name=None):
  """Compress multiple specified files into a single ZIP archive.
  Args:
      file_paths: List of absolute file paths to compress
      output_dir: Directory where the ZIP file will be saved
      password: Optional password for the ZIP file
      zip_name: Base name for the ZIP file (without extension)
  """
  if not file_paths:
    print("No files specified to compress.")
    return
  file_dict = {}
  for file_path in file_paths:
    if not os.path.isfile(file_path):
      print(f"Warning: {file_path} is not a file or doesn't exist. Skipping.")
      continue
    try:
      with open(file_path, 'rb') as f:
        filename_in_zip = os.path.basename(file_path)
        file_dict[filename_in_zip] = f.read()
    except Exception as e:
      print(f"Error reading {file_path}: {str(e)}")
  if not file_dict:
    print("No valid files found to compress.")
    return
  try:
    zip_buffer = create_zip_with_files(file_dict, password)
    timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    if zip_name:
      base_name = f"{zip_name}_{timestamp}.zip"
    else:
      first_file = os.path.basename(file_paths[0])
      base_name = f"{os.path.splitext(first_file)[0]}_{timestamp}.zip"
    output_path = os.path.join(output_dir, base_name)
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'wb') as out_file:
      out_file.write(zip_buffer.read())
    print(f"Created archive: {output_path}")
  except Exception as e:
    print(f"Error creating ZIP archive: {str(e)}")
  finally:
    if 'zip_buffer' in locals(): zip_buffer.close()
