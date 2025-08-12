#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/5/19 16:45'

import re

from ctools import cjson


def extract_json_from_text(text):
  """
  从混杂文本中提取第一个完整的 JSON 对象
  """
  import json

  # 方法1：尝试直接解析
  try:
    return json.loads(text)
  except json.JSONDecodeError:
    pass

  # 方法2：字符级括号匹配提取 JSON
  start = None
  brace_count = 0
  for i, char in enumerate(text):
    if char == '{':
      if start is None:
        start = i
      brace_count += 1
    elif char == '}':
      brace_count -= 1
      if brace_count == 0 and start is not None:
        json_candidate = text[start:i + 1]
        try:
          return json.loads(json_candidate)
        except json.JSONDecodeError:
          start = None  # 重置继续寻找下一个可能的 JSON

  # 方法3：尝试 JSONP 格式
  match = re.search(r'\((\{[\s\S]*\})\)', text)
  if match:
    try:
      return json.loads(match.group(1))
    except json.JSONDecodeError:
      pass

  return None


if __name__ == '__main__':
  xx = """
    <think>

</think>

{
  "sjbs": {
    "xsbt": "东都公园业主集体信访事件",
    "sjbh": "202406031234",
    "jjcd": ["黄"]
  },
  "skys": {
    "zxsj": [
      {
        "jqsj": "2024-06-03 09:00",
        "sjms": "6月3日",
        "sjlx": ["计划时间"]
      }
    ],
    "zxdd": [
      {
        "bzdz": "黑龙江省哈尔滨市信访局",
        "cslx": ["政府机关"]
      }
    ]
  },
  "ssqt": {
    "qtms": ["哈尔滨市道外区东都公园业主"],
    "qtgm": ["约5人以上，可能发展至群体性事件"],
    "qtbq": ["房地产纠纷", "历史遗留问题"],
    "zztz": ["有核心组织"]
  },
  "ryqd": [
    {
      "xm": ["杨开亮"],
      "sfzh": ["2301251968101335**"],
      "js": ["组织者"],
      "hjd": ["哈尔滨市宾县满井镇永宁村崔海屯"],
      "jzd": ["团结镇东都公元一区五栋二单元603"],
      "lxdh": ["139366789**"],
      "rybq": ["重点人"],
      "wlzh": {
        "wx": [],
        "qq": []
      },
      "gjxx": [
        {
          "sj": ["2024-05-28 20:26"],
          "dd": ["网络群聊"],
          "xw": ["组织动员"]
        }
      ]
    },
    {
      "xm": ["孙凤玲"],
      "sfzh": ["2301041955121712**"],
      "js": ["积极参与者"],
      "hjd": ["哈尔滨市道外区迎新街好民居滨港水岸D15栋1单元14层4号"],
      "jzd": ["道外区陶瓷小区D15-1-1404"],
      "lxdh": ["17758887348"],
      "rybq": [],
      "wlzh": {
        "wx": [],
        "qq": []
      },
      "gjxx": [
        {
          "sj": ["2024-05-28 19:00"],
          "dd": ["网络群聊"],
          "xw": ["响应组织"]
        }
      ]
    },
    {
      "xm": ["高秀艳"],
      "sfzh": ["2323261982060762**"],
      "js": ["积极参与者"],
      "hjd": ["绥化市青冈县劳动乡北斗村丛喜云屯"],
      "jzd": ["哈尔滨市道外区团结镇森桐木业"],
      "lxdh": ["15846349146"],
      "rybq": [],
      "wlzh": {
        "wx": [],
        "qq": []
      },
      "gjxx": [
        {
          "sj": ["2024-05-28 20:00"],
          "dd": ["网络群聊"],
          "xw": ["响应组织"]
        }
      ]
    },
    {
      "xm": ["高振凤"],
      "sfzh": ["2323031974103046**"],
      "js": ["一般参与者"],
      "hjd": ["绥化市肇东市东发乡夕阳村郭家屯"],
      "jzd": ["团结镇团结镇东都公园一区七栋一单元101"],
      "lxdh": ["18004659805"],
      "rybq": [],
      "wlzh": {
        "wx": [],
        "qq": []
      },
      "gjxx": [
        {
          "sj": ["2024-05-28 19:30"],
          "dd": ["网络群聊"],
          "xw": ["响应组织"]
        }
      ]
    },
    {
      "xm": ["陈立军"],
      "sfzh": ["2301251980031907**"],
      "js": ["组织者", "群主"],
      "hjd": ["哈尔滨市宾县宾西镇一委六组"],
      "jzd": [],
      "lxdh": ["15776806667"],
      "rybq": ["重点人"],
      "wlzh": {
        "wx": [],
        "qq": []
      },
      "gjxx": [
        {
          "sj": ["2024-05-28 19:00"],
          "dd": ["网络群聊"],
          "xw": ["组织动员"]
        }
      ]
    }
  ],
  "sjtz": {
    "xwlx": ["集体信访", "网络串联"],
    "sqnr": ["要求政府解决房产证办理问题，明确责任主体并推动政策落实"],
    "dktz": [],
    "zjly": ["自筹"]
  },
  "czjy": {
    "zrdw": ["哈尔滨市公安局道外分局", "信访维稳专班"],
    "yjcs": ["提前约谈重点人员", "加强网络群组监控", "部署现场警力"]
  }
}
20250603142141-INFO-8399134464-web_log(log:214) 127.0.0.1 [03/Jun/2025:14:18:39 +0800] "POST /chat/completion HTTP/1.1" 200 3670 "-" "python-requests/2.32.3"


    """

  print((cjson.dumps(extract_json_from_text(xx))))
