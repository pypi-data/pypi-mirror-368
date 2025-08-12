#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/6/9 09:49'

import asyncio
import base64
import json
import mimetypes
import sys
import uuid

from ctools.ai.env_config import bool_env
from ctools.web.aio_web_server import get_stream_resp


class ROLE:
  ASSISTANT = "assistant"
  USER = "user"
  SYSTEM = "system"


def build_message(role_type: ROLE, content):
  """
  快速构建消息
  Parameters
  ----------
  role_type 消息类型
  content 消息内容

  Returns 消息
  -------

  """
  return {"role": role_type, "content": content}


def build_image_message(content: str, file: bytes = None, file_path: str = None):
  """
  快速构建图片消息
  Parameters
  ----------
  content 问题内容
  file 图片文件
  file_path 图片文件路径

  Returns 消息
  -------

  """
  rep = _get_image_data_and_mime(file, file_path)
  img_content = [{
    "type": "image_url",
    "image_url": {
      "url": f'data:{rep["mime_type"]};base64,{rep["data"]}'
    }
  }, {
    "type": "text",
    "text": content
  }]
  return build_message(ROLE.USER, img_content)


async def build_call_back(debug=None, request=None, SSE=True):
  """
  快速构建回调函数
  Parameters
  ----------
  debug 是否开启调试
  request http请求

  Returns 响应对象, 消息队列, 回调函数
  -------
  """
  if not debug: debug = bool_env("LLM_DEBUG", False)
  response = None
  if request: response = await get_stream_resp(request)
  call_id = uuid.uuid4()
  message_queue = asyncio.Queue()

  async def on_msg(cid, role, msg):
    nonlocal response
    if debug: print(msg, file=sys.__stdout__, end='', flush=True)
    final_msg = {"id": cid, "role": role, "msg": msg}
    await message_queue.put(msg)
    if response:
      if SSE:
        await response.write(f"data: {json.dumps(final_msg)}\n\n".encode("utf-8"))
      else:
        await response.write(msg.encode("utf-8"))

  async def on_final(cid, is_final, msg):
    nonlocal response
    if debug: print("\n", cid, "\n", is_final, "\n", msg, "\n", file=sys.__stdout__, flush=True)
    if is_final:
      await message_queue.put("[DONE]")
      if response:
        if SSE: await response.write(b"data: [DONE]\n\n")
        await response.write_eof()
    else:
      nonlocal call_id
      call_id = uuid.uuid4()

  def get_call_id():
    return call_id.hex

  return response, message_queue, {"get_call_id": get_call_id, "get_event_msg_func": on_msg, "get_full_msg_func": on_final}


























def _get_image_data_and_mime(file: bytes = None, file_path: str = None):
  if file_path:
    with open(file_path, "rb") as f:
      file = f.read()
  if not file:
    raise ValueError("file 和 file_path 至少要提供一个")
  mime_type = "application/octet-stream"
  if file_path:
    mime_type_guess, _ = mimetypes.guess_type(file_path)
    if mime_type_guess:
      mime_type = mime_type_guess
  data = base64.b64encode(file).decode("utf-8")
  return {
    "mime_type": mime_type,
    "data": data
  }
