from typing import List


class Alignment:
  def __init__(self, horizontal=None, vertical=None):
    self.horizontal = horizontal
    self.vertical = vertical


class Font:
  def __init__(self, name=None, size: int = None, bold: bool = False, italic: bool = False, underline=None):
    self.name = name
    self.size = size
    self.color = None
    self.bold = bold
    self.italic = italic
    self.underline = underline

  def set_color(self, color):
    if color and color.type == 'rgb':
      self.color = color.rgb[2:]


class Style:

  def __init__(self):
    self.font = None
    self.bg_color = None
    self.alignment: Alignment = Alignment()

  def set_bg_color(self, color):
    if color.type == 'rgb' and color.rgb != "00000000":
      self.bg_color = color.rgb[2:]


class WordCell:
  position: list = []
  value: str = None
  style: Style = None


class WordTable:
  max_rows: int = None
  max_cols: int = None
  cells: List[WordCell] = None
  merged_cells: list = None
