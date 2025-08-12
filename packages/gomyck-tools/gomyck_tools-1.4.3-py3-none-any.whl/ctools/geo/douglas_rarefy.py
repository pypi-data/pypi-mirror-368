#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2024/9/19 14:02'

import math

from jsonpath_ng import parser

from ctools import cjson
from ctools.sys_log import flog as log

"""
douglas_rarefy.DouglasRarefy(res, level=3).sparse_points()
"""


class THIN_LEVEL:
  L1 = 0.00001
  L2 = 0.00003
  L3 = 0.00009
  L4 = 0.0002
  L5 = 0.0004
  L6 = 0.0007
  L7 = 0.0011
  L8 = 0.0017
  L9 = 0.0022


class Point:
  def __init__(self, lng, lat, origin_data):
    self.lng = lng
    self.lat = lat
    self.origin_data = origin_data


def _get_line_by_point(xy1, xy2):
  """
  根据两个点求直线方程 ax + by + c = 0
  :param xy1: 点1, 例如 {'lat': 1, 'lng': 1}
  :param xy2: 点2, 例如 {'lat': 2, 'lng': 2}
  :return: 直线方程的三个参数 [a, b, c]
  """
  x1 = xy1.lng
  y1 = xy1.lat
  x2 = xy2.lng
  y2 = xy2.lat
  a = y2 - y1
  b = x1 - x2
  c = (y1 - y2) * x1 - y1 * (x1 - x2)
  return [a, b, c]


def _get_distance_from_point_to_line(a, b, c, xy):
  """
  点到直线的距离，直线方程为 ax + by + c = 0
  :param a: 直线参数a
  :param b: 直线参数b
  :param c: 直线参数c
  :param xy: 点坐标，例如 {'lat': 2, 'lng': 2}
  :return: 距离
  """
  x = xy.lng
  y = xy.lat
  return abs((a * x + b * y + c) / math.sqrt(a * a + b * b))


class DouglasRarefy:
  """
  DouglasRarefy Use Guide:
    points must be arrays, element can be dict or arrays, when element is arrays, index 0 must be lng, index 1 must be lat, and element can be use max column num is 2 (lng, lat) in ret_tpl
    level default is L2, this level can be hold most of the points detail
    ret_tpl is the result tpl, can be arrays and json or some can be json loads, exp: [{lng}, {lat}] OR {{"lng": {lng}, "lat": {lat}}}
  """

  def __init__(self, points: [], level=THIN_LEVEL.L2, ret_tpl=None, get_lng=None, get_lat=None):
    if not isinstance(points, list): raise Exception('points must be list obj !!')
    if len(points) < 3: raise Exception('points length must be gt 2 !!')
    self.points = points
    self.threshold = THIN_LEVEL.L2 if level is None else (getattr(THIN_LEVEL, "L{}".format(int(level))) if int(level) >= 1 else level)
    log.debug("threshold is: {}".format(self.threshold))
    self.is_json = isinstance(points[0], dict)
    self.get_lng = get_lng
    self.get_lat = get_lat
    if self.is_json:
      if not self.get_lng: self.get_lng = '$.lng'
      if not self.get_lat: self.get_lat = '$.lat'
    else:
      if not self.get_lng: self.get_lng = '$.[0]'
      if not self.get_lat: self.get_lat = '$.[1]'
    log.debug("get_lng is: {}, get_lat is: {}".format(self.get_lng, self.get_lat))
    self.lng_parser = parser.parse(self.get_lng)
    self.lat_parser = parser.parse(self.get_lat)
    log.debug("is_json is: {}".format(self.is_json))
    self.ret_tpl = ret_tpl
    log.debug("ret_tpl is: {}".format(self.ret_tpl))
    self.data = [Point(self.lng_parser.find(p)[0].value, self.lat_parser.find(p)[0].value, p) for p in self.points]

  def _sparse_points(self, points):
    """
    点位压缩
    :return: 稀疏后的点集
    """
    if len(points) < 3:
      if not self.ret_tpl:
        return [points[0].origin_data, points[-1].origin_data]
      else:
        if self.is_json:
          return [cjson.loads(self.ret_tpl.format(**points[0].origin_data)), cjson.loads(self.ret_tpl.format(**points[-1].origin_data))]
        else:
          return [cjson.loads(self.ret_tpl.format(lng=points[0].lng, lat=points[0].lat)), cjson.loads(self.ret_tpl.format(lng=points[-1].lng, lat=points[-1].lat))]

    xy_first = points[0]  # 第一个点
    xy_end = points[-1]  # 最后一个点
    a, b, c = _get_line_by_point(xy_first, xy_end)  # 获取直线方程的 a, b, c 值
    d_max = 0  # 记录点到直线的最大距离
    split = 0  # 分割位置
    for i in range(1, len(points) - 1):
      d = _get_distance_from_point_to_line(a, b, c, points[i])
      if d > d_max:
        split = i
        d_max = d
    if d_max > self.threshold:
      # 如果存在点到首位点连成直线的距离大于 max_distance 的, 即需要再次划分
      child_left = self._sparse_points(points[:split + 1])  # 递归处理左边部分
      child_right = self._sparse_points(points[split:])  # 递归处理右边部分
      # 合并结果，避免重复
      return child_left + child_right[1:]
    else:
      if not self.ret_tpl:
        return [points[0].origin_data, points[-1].origin_data]
      else:
        if self.is_json:
          return [cjson.loads(self.ret_tpl.format(**points[0].origin_data)), cjson.loads(self.ret_tpl.format(**points[-1].origin_data))]
        else:
          return [cjson.loads(self.ret_tpl.format(lng=points[0].lng, lat=points[0].lat)), cjson.loads(self.ret_tpl.format(lng=points[-1].lng, lat=points[-1].lat))]

  def sparse_points(self):
    return self._sparse_points(self.data)
