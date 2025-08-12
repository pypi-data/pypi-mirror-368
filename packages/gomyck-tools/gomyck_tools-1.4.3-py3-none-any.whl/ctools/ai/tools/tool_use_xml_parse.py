import html
import json
import xml.etree.ElementTree as ET


def parse_tool_use(xml_string):
  tool_name = ''
  try:
    root = ET.fromstring(xml_string.strip())
    if root.tag != "tool_use": raise ValueError("根标签必须是 <tool_use>")
    tool_name = root.find("name").text.strip()
    args = root.find("arguments").text
    if args:
      arguments_text = args.strip()
      arguments_text = html.unescape(arguments_text)
      arguments = json.loads(arguments_text)
      return {
        "tool": tool_name,
        "arguments": arguments
      }
    else:
      return {
        "tool": tool_name,
        "arguments": {}
      }
  except Exception as e:
    raise ValueError(f"tool_use_{tool_name} 解析失败: {e}")


# 测试
if __name__ == '__main__':
  xml_input = """
<tool_use>
<name>set</name>
<arguments>{"key": "weather_harbin", "value": "{\\"city\\":\\"哈尔滨市\\",\\"forecasts\\":[{\\"date\\":\\"2025-05-27\\",\\"week\\":\\"2\\",\\"dayweather\\":\\"晴\\",\\"nightweather\\":\\"晴\\",\\"daytemp\\":29,\\"nighttemp\\":15,\\"daywind\\":\\"南\\",\\"nightwind\\":\\"南\\",\\"daypower\\":1,\\"nightpower\\":3},{\\"date\\":\\"2025-05-28\\",\\"week\\":"3", \\"dayweather\\":"晴", \\"nightweather\\":"晴", \\"daytemp\\":"30", \\"nighttemp\\":"17"}]}"}</arguments>
</tool_use>
    """
  result = parse_tool_use(xml_input)
  print("\n【结果】")
  print(json.dumps(result, ensure_ascii=False, indent=2))
