import logging
import os

import httpx

from ctools import sys_log, cjson, call
from ctools.ai.env_config import float_env, bool_env, int_env
from ctools.ai.llm_exception import LLMException

logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("mcp.client.sse").setLevel(logging.WARNING)

log = sys_log.flog
shared_client = None

def process_SSE(line):
  if not line: return None
  if line.startswith("data: "):
    data = line[6:]
    if data == "[DONE]":
      return "[DONE]"
    return data

@call.once
def init_shared_client():
  global shared_client
  shared_client = httpx.AsyncClient(
    base_url=os.getenv("LLM_BASE_URL", "https://api.siliconflow.cn/v1/"),
    timeout=httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=5.0),
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
  )
  return shared_client

class LLMClient:
  """Manages communication with the LLM provider."""

  def __init__(self,
     api_key: str = "",
     model_name: str = "",
     temperature: float = None,
     stream: bool = None,
     thinking: bool = None,
     thinking_budget: int = None,
     max_tokens: int = None,
     top_p: float = None,
     top_k: int = None,
     frequency_penalty: float = None
   ) -> None:
    self.api_key = api_key or os.getenv("LLM_API_KEY")
    self.model_name = model_name or os.getenv("LLM_MODEL_NAME", "Qwen/Qwen3-235B-A22B")
    self.temperature = temperature or float_env("LLM_TEMPERATURE", 0.8)
    self.stream = stream or bool_env("LLM_STREAM", True)
    self.thinking = thinking or bool_env("LLM_THINKING", True)
    self.thinking_budget = thinking_budget or int_env("LLM_THINKING_BUDGET", 4096)
    self.max_tokens = max_tokens or int_env("LLM_MAX_TOKENS", 4096)
    self.top_p = top_p or float_env("LLM_TOP_P", 0.5)
    self.top_k = top_k or int_env("LLM_TOP_K", 50)
    self.frequency_penalty = frequency_penalty or float_env("LLM_FREQUENCY_PENALTY", 0)
    init_shared_client()

  async def model_completion(self, messages: list[dict[str, str]]):
    self.no_think_compatible(messages)
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {self.api_key}",
    }
    payload = {
      "messages": messages,
      "model": self.model_name,
      "temperature": self.temperature,
      "max_tokens": self.max_tokens,
      "top_p": self.top_p,
      "top_k": self.top_k,
      "frequency_penalty": self.frequency_penalty,
      "stream": self.stream,
      "enable_thinking": self.thinking,
      "thinking_budget": self.thinking_budget
    }
    try:
      req_url = "chat/completions"
      if self.stream:
        async with shared_client.stream("POST", req_url, headers=headers, json=payload) as response:
          response.raise_for_status()
          start_think = False
          end_think = False
          async for line in response.aiter_lines():
            data = process_SSE(line)
            if not data or data == "[DONE]":
              continue
            choice = cjson.loads(data)["choices"][0]
            if "message" in choice:
              content = choice["message"]["content"]
            else:
              content = choice["delta"].get("content", "")
              reasoning_content = choice["delta"].get("reasoning_content", "")
              if not start_think and not content and reasoning_content:
                content = f"<think>{reasoning_content}"
                start_think = True
              if not end_think and start_think and not reasoning_content:
                content = f"</think>{content}"
                end_think = True
              if not content:
                content = reasoning_content
            if content:
              yield content
      else:
        response = await shared_client.post(req_url, headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        yield content
    except Exception as e:
      error_message = f"Error getting LLM response: {str(e)}"
      log.error(error_message)
      if isinstance(e, httpx.ReadTimeout):
        raise LLMException(code=500, message="模型访问超时")
      if isinstance(e, httpx.HTTPStatusError):
        log.error(f"Status code: {e.response.status_code}")
        log.error(f"Response details: {e.response.text}")
        raise LLMException(e.response.status_code, e.response.text)
      raise LLMException(code=500, message=error_message)

  def no_think_compatible(self, messages):
    if not self.thinking and "qwen3" in self.model_name.lower():
      for msg in messages:
        if msg and msg.get("role") in ("user", "system") and "/no_think" not in msg.get("content", ""):
          msg["content"] += " /no_think"

  async def voice_2_text(self, file: bytes = None, file_path: str = None):
    try:
      if file_path:
        with open(file_path, "rb") as f:
          file = f.read()
      req_url = "/audio/transcriptions"
      headers = {
        "Authorization": f"Bearer {self.api_key}",
      }
      files = {
        "model": (None, self.model_name),
        "file": ("audio.wav", file, "audio/wav"),
      }
      response = await shared_client.post(req_url, headers=headers, files=files)
      response.raise_for_status()
      return response.json()["text"]
    except Exception as e:
      error_message = f"Error getting LLM response: {str(e)}"
      log.error(error_message)
      if isinstance(e, httpx.HTTPStatusError):
        log.error(f"Status code: {e.response.status_code}")
        log.error(f"Response details: {e.response.text}")
        raise LLMException(e.response.status_code, e.response.text)
      raise LLMException(code=500, message=error_message)

# from env_config import Configuration
# config = Configuration("/Users/haoyang/work/pycharmWorkspace/gomyck-py-plugins/ai/klmy-entry_get/.env")
#
# async def run():
#   llm = LLMClient(config.get_llm_api_key(), model_name="FunAudioLLM/SenseVoiceSmall")
#   res = await llm.voice_2_text(file_path="/Users/haoyang/Downloads/audio.wav")
#   print(res)
#
# if __name__ == '__main__':
#   asyncio.run(run())
