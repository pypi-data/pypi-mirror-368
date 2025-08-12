import time
from datetime import datetime, timedelta

def get_month(date: str=None):
  if date: return time.strftime('%Y-%m', time.strptime(date, '%Y-%m-%d'))
  return time.strftime('%Y-%m', time.localtime(time.time()))

def get_date():
  return time.strftime('%Y-%m-%d', time.localtime(time.time()))


def get_time():
  return time.strftime('%H-%M-%S', time.localtime(time.time()))


def get_date_time(fmt="%Y-%m-%d %H:%M:%S"):
  return time.strftime(fmt, time.localtime(time.time()))


def str_to_datetime(val: str, fmt="%Y-%m-%d %H:%M:%S"):
  return time.strptime(val, fmt)


def str_to_timestamp(val: str, fmt="%Y-%m-%d %H:%M:%S"):
  return time.mktime(time.strptime(val, fmt))


def timestamp_to_str(timestamp: int = time.time(), fmt="%Y-%m-%d %H:%M:%S"):
  return time.strftime(fmt, time.localtime(timestamp))


def get_today_start_end(now: datetime.now()):
  start = datetime(now.year, now.month, now.day, 0, 0, 0)
  end = datetime(now.year, now.month, now.day, 23, 59, 59)
  return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")


def get_week_start_end(now: datetime.now()):
  start = now - timedelta(days=now.weekday())  # 本周一
  end = start + timedelta(days=6)  # 本周日
  return start.strftime("%Y-%m-%d 00:00:00"), end.strftime("%Y-%m-%d 23:59:59")


def time_diff_in_seconds(sub_head: str = get_date_time(), sub_end: str = get_date_time()):
  start_ts = str_to_timestamp(sub_head)
  end_ts = str_to_timestamp(sub_end)
  return int(start_ts - end_ts)


def opt_time(base_time=None, days=0, hours=0, minutes=0, seconds=0, weeks=0, fmt="%Y-%m-%d %H:%M:%S"):
  if base_time is None:
    base_time = datetime.now()
  elif isinstance(base_time, str):
    base_time = datetime.strptime(base_time, fmt)
  new_time = base_time + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds, weeks=weeks)
  return new_time.strftime(fmt)

def get_years_range(start_year: str, end_year: str=datetime.now().strftime("%Y")) -> set[int]:
  if int(start_year) > int(end_year):
    raise ValueError("起始年份不能大于结束年份")
  return list(range(int(start_year), int(end_year) + 1))

def get_month_range(start: str, end: str=datetime.now().strftime("%Y-%m")) -> set[str]:
  start_date = datetime.strptime(start, "%Y-%m")
  end_date = datetime.strptime(end, "%Y-%m")
  if start_date > end_date:
    raise ValueError("起始月份不能晚于结束月份")
  result = []
  current = start_date
  while current <= end_date:
    result.append(current.strftime("%Y-%m"))
    if current.month == 12:
      current = current.replace(year=current.year + 1, month=1)
    else:
      current = current.replace(month=current.month + 1)
  return result

def get_day_range(start: str, end: str=datetime.now().strftime("%Y-%m-%d")) -> set[str]:
  start_date = datetime.strptime(start, "%Y-%m-%d")
  end_date = datetime.strptime(end, "%Y-%m-%d")
  if start_date > end_date:
    raise ValueError("起始日期不能晚于结束日期")
  delta = end_date - start_date
  return [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)]
