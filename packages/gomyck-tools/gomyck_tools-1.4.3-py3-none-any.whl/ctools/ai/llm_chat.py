from ctools import sys_log
from ctools.ai.llm_client import LLMClient
from ctools.ai.llm_exception import LLMException
from ctools.ai.mcp.mcp_client import MCPClient, res_has_img, is_image_content, get_tools_prompt, mcp_tool_call
from ctools.ai.tools.quick_tools import build_message, ROLE
from ctools.ai.tools.think_process import remove_think_blocks
from ctools.ai.tools.xml_extract import extract_all_xml_blocks

log = sys_log.flog

continue_prompt_default = """
1.请继续处理尚未完成的内容,跳过所有已处理完成的部分.
2.工具调用时,请参考上一次工具调用的参数,仅对偏移量相关的参数进行调整,以接续上一次处理的进度.
3.如果你认为所有数据都处理完毕, 请输出标记：{end_flag}.
"""


class ChatSession:

  def __init__(self, prompts: str, llm_client: LLMClient, max_tools_call: int = 10, mcp_clients: list[MCPClient] = None,
               auto_complete: bool = False, end_flag: str = "EOF", continue_prompt: str = continue_prompt_default) -> None:
    """
    初始化聊天
    :param prompts: 提示词
    :param llm_client: llm 客户端
    :param max_tools_call: 最大单次工具调用次数
    :param mcp_clients: mcp_clients
    :param auto_complete: 是否自动完成
    :param end_flag: 结束标记
    :param continue_prompt: 自动完成时的继续提示
    """
    self.mcp_clients: list[MCPClient] = mcp_clients
    self.llm_client: LLMClient = llm_client
    self.prompts: str = prompts
    self.max_tools_call = max_tools_call
    self.auto_complete = auto_complete
    self.end_flag = end_flag
    self.continue_prompt = continue_prompt.format(end_flag=self.end_flag)

    self.current_message = {}
    self.full_messages = []
    self.res_code = 200

  async def init_prompts(self, user_system_prompt):
    if self.mcp_clients:
      if user_system_prompt:
        mcp_tools_prompt = await get_tools_prompt(self.mcp_clients, user_system_prompt)
      elif self.prompts:
        mcp_tools_prompt = await get_tools_prompt(self.mcp_clients, self.prompts)
      else:
        mcp_tools_prompt = await get_tools_prompt(self.mcp_clients, "")
      self.full_messages.append(build_message(ROLE.SYSTEM, mcp_tools_prompt))
      # log.info(mcp_tools_prompt)
    else:
      if user_system_prompt:
        self.full_messages.append(build_message(ROLE.SYSTEM, user_system_prompt))
      elif self.prompts:
        self.full_messages.append(build_message(ROLE.SYSTEM, self.prompts))

  async def chat(self, user_input: [str], get_call_id: callable(str) = lambda: "None", get_event_msg_func: callable(str) = None, get_full_msg_func: callable(str) = None):
    """
    对话
    Parameters
    ----------
    user_input 用户输入  [{"role": "user", "content": "hello"}]
    get_call_id 本次对话 ID func
    get_event_msg_func(get_call_id(), role, msg)    获取实时回复(流式回答)
    get_full_msg_func(get_call_id(), is_final, msg) 获取完整的回答列表
    -------
    """
    # 获取 prompt
    if type(user_input) == dict: user_input = [user_input]
    user_system_prompt = user_input[0]["content"] if user_input[0]["role"] == "system" else ""
    user_input = user_input[1:] if user_input[0]["role"] == "system" else user_input
    await self.init_prompts(user_system_prompt)
    try:
      self.full_messages.extend(user_input)
      last_user_input = next((item["content"] for item in reversed(user_input) if item.get("role") == "user"), None)
      current_process_index = 0
      max_tools_call = self.max_tools_call
      final_resp = False
      while (current_process_index < max_tools_call and not final_resp) or (self.auto_complete and current_process_index < 100):
        log.info("\n正在生成回答: %s", self.full_messages)
        res = []
        async for chunk in self.llm_client.model_completion(self.full_messages):
          res.append(chunk)
          await self.process_chunk_message(chunk, get_call_id, get_event_msg_func)
        llm_response = "".join(res)
        log.info("\n收到回答: %s", llm_response)
        no_think_llm_response = remove_think_blocks(llm_response)  # 处理掉 think, 然后再判断 EOF, 避免 think 里出现 EOF
        if self.end_flag in no_think_llm_response:
          self.full_messages.append(build_message(ROLE.ASSISTANT, llm_response.replace(self.end_flag, "")))  # 去掉 EOF
          current_process_index = 999
          final_resp = True
          await self.process_full_message(final_resp, get_call_id, get_full_msg_func)
        else:
          xml_blocks = extract_all_xml_blocks(llm_response)
          if xml_blocks:
            for xml_block in xml_blocks:
              tool_call_result = await mcp_tool_call(self.mcp_clients, xml_block)
              log.info("\nMCP调用结果: %s", tool_call_result)
              current_process_index += 1
              if tool_call_result == xml_block:
                self.full_messages.append(build_message(ROLE.USER, "工具调用出现错误, 请重试."))
              elif current_process_index == max_tools_call - 1:
                await self.add_tool_call_res_2_message(last_user_input, tool_call_result)
                self.full_messages.append(build_message(ROLE.USER, "调用次数已达上限, 请直接回答."))  # 不能调换顺序
              else:
                self.full_messages.append(build_message(ROLE.ASSISTANT, llm_response))  # 不能调换顺序
                await self.add_tool_call_res_2_message(last_user_input, tool_call_result)
              await self.process_tool_call_message(get_call_id, get_event_msg_func, tool_call_result)
            final_resp = False
          else:
            self.full_messages.append(build_message(ROLE.ASSISTANT, llm_response))
            if self.auto_complete: self.full_messages.append(build_message(ROLE.USER, self.continue_prompt))
            final_resp = True
          await self.process_full_message(final_resp, get_call_id, get_full_msg_func)
    except Exception as e:
      log.exception(e)
      if isinstance(e, LLMException):
        error_code = e.code
        error_msg = '系统出现错误, 请重试: {}-{}'.format(e.code, e.message)
      else:
        error_code = 500
        error_msg = '系统出现错误, 请重试: {}'.format(e)
      self.full_messages.append(build_message(ROLE.ASSISTANT, error_msg))
      await self.process_error_message(error_code, error_msg, get_call_id, get_event_msg_func, get_full_msg_func)
    finally:
      return self.current_message

  async def process_error_message(self, code, error_msg, get_call_id, get_event_msg_func, get_full_msg_func):
    # 最终结果通知前端+实时通知都要有
    self.res_code = code
    self.current_message = error_msg
    if get_event_msg_func: await get_event_msg_func(get_call_id(), ROLE.ASSISTANT, self.current_message)
    if get_full_msg_func: await get_full_msg_func(get_call_id(), True, self.full_messages)

  async def process_chunk_message(self, chunk, get_call_id, get_event_msg_func):
    # 实时通知前端
    self.current_message = chunk
    if get_event_msg_func: await get_event_msg_func(get_call_id(), ROLE.ASSISTANT, self.current_message)

  async def process_tool_call_message(self, get_call_id, get_event_msg_func, tool_call_result):
    # 实时通知前端(工具调用特殊通知一次) 如果是图片结果, 就是 user 消息(必须是 user, 否则 api 报错), 否则是 system(现在统一都改成 user 了, 看看后面有没有改回 system 的必要)
    self.current_message = tool_call_result["result"] if res_has_img(tool_call_result) else tool_call_result
    if get_event_msg_func: await get_event_msg_func(get_call_id(), ROLE.USER, self.current_message)

  async def process_full_message(self, final_resp, get_call_id, get_full_msg_func):
    self.current_message = self.full_messages[-1]["content"]
    if get_full_msg_func: await get_full_msg_func(get_call_id(), final_resp, self.full_messages)

  async def add_tool_call_res_2_message(self, last_user_input, tool_call_result: dict):
    if type(tool_call_result) != dict: return
    response: [] = tool_call_result.get("result")
    image_content = []
    for rep in response:
      if not is_image_content(rep):
        self.full_messages.append(build_message(ROLE.USER, str(rep)))
      else:
        image_content.append({
          "type": "image_url",
          "image_url": {
            "url": f'data:{rep["mime_type"]};base64,{rep["data"]}'
          }
        })
    if image_content:
      image_content.append({
        "type": "text",
        "text": last_user_input
      })
      self.full_messages.append(build_message(ROLE.USER, image_content))
