import re


def extract_all_xml_blocks(text):
  return re.findall(r"<tool_use>.*?</tool_use>", text, re.DOTALL)


text = """
一些内容...
123
"""

results = extract_all_xml_blocks(text)
for xml_block in results:
  print(xml_block)
