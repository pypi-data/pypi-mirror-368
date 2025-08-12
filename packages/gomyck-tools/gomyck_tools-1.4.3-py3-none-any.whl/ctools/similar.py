from fuzzywuzzy import fuzz, process


def best_match(query: str, choices: list[str], score_cutoff: int = 70):
  """
  获取最接近 query 的匹配项
  :return: (匹配项, 相似度得分) 或 None
  """
  return process.extractOne(query, choices, scorer=fuzz.ratio, score_cutoff=score_cutoff)


def all_matches(query: str, choices: list[str], limit: int = 5):
  """
  获取多个相似匹配项
  :return: [(匹配项, 相似度得分), ...]
  """
  return process.extract(query, choices, scorer=fuzz.ratio, limit=limit)


def is_similar(s1: str, s2: str, threshold: int = 85):
  """
  判断两个字符串是否相似
  :return: True / False
  """
  return fuzz.ratio(s1, s2) >= threshold
