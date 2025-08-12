#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/5/16 16:49'

import asyncio
import json
import os
import shutil
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import CallToolResult, TextContent, ImageContent

from ctools import sys_log, cdate
from ctools.ai.tools.tool_use_xml_parse import parse_tool_use

log = sys_log.flog

sys_prompt_4_mcp = """
1. In this environment you have access to a set of tools you can use to answer the user's question.
2. You can use one tool per message, and will receive the result of that tool use in the user's response.
3. You use tools step-by-step to accomplish a given task, with each tool use informed by the result of the previous tool use.
4. Before solving the task, break it down into clear, logical steps. List and number the steps first. Then, execute them one by one, There is no need to explain each step as you go. Do not skip any steps. Wait for confirmation before proceeding to the next step, if needed.

## Tool Use Formatting

Tool use is formatted using XML-style tags. The tool name is enclosed in opening and closing tags, and each parameter is similarly enclosed within its own set of tags. Here's the structure:
<tool_use>
<name>{{tool_name}}</name>
<arguments>{{json_arguments}}</arguments>
</tool_use>

The tool name should be the exact name of the tool you are using, and the arguments should be a JSON object containing the parameters required by that tool. For example:

<tool_use>
  <name>say_hello</name>
  <arguments>
    {{
      "content": "你好"
    }}
  </arguments>
</tool_use>

The result should be a string, which can represent a file or any other output type. You can use this result as input for the next action.

Always adhere to this format for the tool use to ensure proper parsing and execution.

## Tool Use Available Tools
Above example were using notional tools that might not exist for you. You only have access to these tools:
{tools_description}

## Tool Use Rules
Here are the rules you should always follow to solve your task:
1. Always use the right arguments for the tools. Never use variable names as the action arguments, use the value instead.
2. Call a tool only when needed: do not call the search agent if you do not need information, try to solve the task yourself.
3. If no tool call is needed, just answer the question directly.
4. Never re-do a tool call that you previously did with the exact same parameters.
5. For tool use, MARK SURE use XML tag format as shown in the examples above. Do not use any other format.
6. Parameter passing should never escape unicode, and this is done by default, do not convert Chinese to Unicode escape characters

# User Instructions
{user_system_prompt}

# Current time
{current_time}

Now Begin! If you solve the task correctly, you will receive a reward of $1,000,000.
"""

tools_use_example = """
Here are a few examples using notional tools:

---
User: "What is the result of the following operation: 5 + 3 + 1294.678?"

Assistant: I can use the python_interpreter tool to calculate the result of the operation.
<tool_use>
  <name>python_interpreter</name>
  <arguments>{"code": "5 + 3 + 1294.678"}</arguments>
</tool_use>

User: {
  "tool_name": "python_interpreter",
  "result": ["1302.678"]
}

Assistant: The result of the operation is 1302.678.

---
User: "Which city has the highest population , Guangzhou or Shanghai?"

Assistant: I can use the search tool to find the population of Guangzhou.
<tool_use>
  <name>search</name>
  <arguments>{"query": "Population Guangzhou"}</arguments>
</tool_use>

User: {
  "tool_name": "search",
  "result": ["Guangzhou has a population of 15 million inhabitants as of 2021."]
}

Assistant: I can use the search tool to find the population of Shanghai.
<tool_use>
  <name>search</name>
  <arguments>{"query": "Population Shanghai"}</arguments>
</tool_use>

User: {
  "tool_name": "search",
  "result": ["26 million (2019)"]
}
Assistant: The population of Shanghai is 26 million, while Guangzhou has a population of 15 million. Therefore, Shanghai has the highest population.
"""


async def get_tools_prompt(mcp_clients, user_system_prompt) -> str:
  all_tools = []
  for client in mcp_clients:
    tools = await client.list_server_tools()
    all_tools.extend(tools)
  return sys_prompt_4_mcp.format(tools_description="\n".join([tool.format_for_llm() for tool in all_tools]), user_system_prompt=user_system_prompt, current_time=cdate.get_date())


class Tool:

  def __init__(self, name: str, description: str, input_schema: dict[str, Any]) -> None:
    self.name: str = name
    self.description: str = description
    self.input_schema: dict[str, Any] = input_schema

  def format_for_llm(self) -> str:
    args_desc = []
    if "properties" in self.input_schema:
      for param_name, param_info in self.input_schema["properties"].items():
        arg_desc = f"- {param_name}({param_info.get('type', 'Any')}):  {param_info.get('description', '')}"
        if param_name in self.input_schema.get("required", []):
          arg_desc += " (required)"
        args_desc.append(arg_desc)
    return f"""
Tool: {self.name}
Description: {self.description}
Args_Info:
{chr(10).join(args_desc)}
"""


class MCPClient:

  def __init__(self, name: str, config: dict[str, Any]) -> None:
    self.name: str = name
    self.config: dict[str, Any] = config
    self.stdio_context: Any | None = None
    self.session: ClientSession | None = None
    self.exit_stack: AsyncExitStack = AsyncExitStack()
    self.tools = []

  async def initialize(self) -> None:
    if self.config.get('server_type') is None or self.config.get('server_type') == 'stdio':
      command = (shutil.which("npx") if self.config["command"] == "npx" else self.config["command"])
      if command is None: raise ValueError("The command must be a valid string and cannot be None.")
      env = os.environ.copy()
      custom_env = self.config.get("env", {})
      env.update(custom_env)
      server_params = StdioServerParameters(
        command=command,
        args=self.config["args"],
        env=env,
      )
      stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
      read, write = stdio_transport
      self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
      await self.session.initialize()
    elif self.config['server_type'] == 'SSE':
      sse_transport = await self.exit_stack.enter_async_context(sse_client(
        url=self.config["url"],
        headers=self.config["headers"],
        timeout=self.config["timeout"],
        sse_read_timeout=self.config["sse_read_timeout"]))
      read, write = sse_transport
      self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
      await self.session.initialize()
    elif self.config['server_type'] == 'Streamable HTTP':
      stream_transport = await self.exit_stack.enter_async_context(streamablehttp_client(
        url=self.config["url"],
        headers=self.config["headers"],
        timeout=self.config["timeout"],
        sse_read_timeout=self.config["sse_read_timeout"]))
      read, write, session_id = stream_transport
      self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
      await self.session.initialize()

  async def list_server_tools(self) -> list[Any]:
    if not self.session: raise RuntimeError(f"Server {self.name} not initialized")
    if self.tools: return self.tools
    tools_response = await self.session.list_tools()
    for item in tools_response:
      if isinstance(item, tuple) and item[0] == "tools":
        self.tools.extend(Tool(tool.name, tool.description, tool.inputSchema) for tool in item[1])
    return self.tools

  async def execute_tool(
    self,
    tool_name: str,
    arguments: dict[str, Any],
    retries: int = 3,
    delay: float = 1.0,
  ) -> Any:
    if not self.session: raise RuntimeError(f"Server {self.name} not initialized")
    attempt = 0
    args = arguments
    while attempt < retries:
      try:
        log.info(f"Executing {tool_name}...")
        result = await self.session.call_tool(tool_name, args)
        return result
      except Exception as e:
        attempt += 1
        log.warning(f"Error executing tool: {e}. Attempt {attempt} of {retries}.")
        if attempt < retries:
          log.info(f"Retrying in {delay} seconds...")
          await asyncio.sleep(delay)
        else:
          log.error("Max retries reached. Failing.")
          raise

  async def cleanup(self) -> None:
    await self.exit_stack.aclose()
    self.session = None
    self.stdio_context = None
    self.exit_stack = None


async def mcp_tool_call(mcp_clients: MCPClient, xml_info: str) -> str:
  if not mcp_clients: return xml_info
  final_result = {
    "tool_name": "",
    "result": []
  }
  try:
    tool_call = parse_tool_use(xml_info)
    if "tool" in tool_call and "arguments" in tool_call:
      log.info(f"Executing tool: {tool_call['tool']} With arguments: {tool_call['arguments']}")
      for client in mcp_clients:
        tools = await client.list_server_tools()
        if any(tool.name == tool_call["tool"] for tool in tools):
          final_result["tool_name"] = tool_call["tool"]
          try:
            result: CallToolResult = await client.execute_tool(tool_call["tool"], tool_call["arguments"])
            text_result = []
            image_result = []
            tools_call_content = result.content
            for content in tools_call_content:
              if type(content) == TextContent:
                try:
                  text_result.append(json.loads(content.text))
                except Exception as e:
                  text_result.append(content.text)
              elif type(content) == ImageContent:
                image_result.append({"mime_type": content.mimeType, "data": content.data})
            text_result.extend(image_result)
            final_result["result"] = text_result
            return final_result
          except Exception as e:
            log.exception(e)
            error_msg = f"Error executing tool: {str(e)}"
            final_result["result"] = [error_msg]
            return final_result
      return f"No server found with tool: {tool_call['tool']}"
    return xml_info
  except Exception as e:
    log.exception(e)
    error_msg = f"Error executing tool: {str(e)}"
    final_result["result"] = [error_msg]
    return final_result


def res_has_img(llm_response) -> bool:
  if type(llm_response) == str: return False
  response: [] = llm_response.get("result")
  for rep in response:
    if is_image_content(rep):
      return True
  return False


def is_image_content(content: dict) -> bool:
  try:
    if content.get("mime_type") and content.get("data"):
      return True
    return False
  except Exception:
    return False


from contextlib import asynccontextmanager

@asynccontextmanager
async def init_mcp_clients(mcp_server_config: dict[str, Any]) -> list[MCPClient]:
  mcp_clients = []
  if not mcp_server_config["mcpServers"]:
    yield mcp_clients
    return  # 这句必须有，避免进入 finally
  try:
    for name, sc in mcp_server_config["mcpServers"].items():
      try:
        mc = MCPClient(name, sc)
        await mc.initialize()
        mcp_clients.append(mc)
      except Exception as e:
        log.exception(f"Error initializing MCP server [{name}]: {e}")
    yield mcp_clients  # 只允许有一个 yield
  finally:
    for client in mcp_clients:
      try:
        print(client.name)
        await client.cleanup()
      except* Exception as eg:
        #log.warning(f"ExceptionGroup unloading MCP server [{client.name}]: {eg}")
        pass

