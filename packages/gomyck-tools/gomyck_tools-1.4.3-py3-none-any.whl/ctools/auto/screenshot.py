import os
import time
import tkinter as tk

import pyautogui

from ctools import application
from ctools import cid

"""
截屏工具类, 按回车截图
image_path=screenshot_tools.screenshot()
"""


class ScreenshotTools:
  def __init__(self):
    self.root = tk.Tk()
    self.root.overrideredirect(True)
    self.root.attributes("-alpha", 0.1)
    self.root.attributes('-topmost', 'true')
    self.root.geometry("{0}x{1}+0+0".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
    self.root.configure(bg="black")

    self.canvas = tk.Canvas(self.root)
    self.canvas.bind("<Button-3>", self.change_center_point)

    self.x, self.y = 0, 0
    self.xstart, self.ystart = 0, 0
    self.xend, self.yend = 0, 0
    self.xcenter, self.ycenter = 0, 0

    self.select_area = self.canvas.create_rectangle(0, 0, 0, 0, outline='red', width=0, dash=(4, 4))
    self.screenshot_path = None
    self.center_offset = (0, 0)

    self.pos_div = tk.Toplevel(self.root)
    self.pos_div.overrideredirect(True)
    self.pos_div.attributes('-topmost', 'true')
    self.pos_div.configure(bg="grey")
    self.pos_div.geometry("360x25")

    self.pos_div_text = "POS: (%s, %s), Enter键-截图, Esc键-退出, 右键设置点击位置"
    self.pos_label = tk.Label(self.pos_div, text=self.pos_div_text % (0, 0), bg="black", fg="white")
    self.pos_label.pack(fill="both", expand=True)

    self.center_div = None

    self.root.bind('<Escape>', self.sys_out)  # 键盘Esc键->退出
    self.root.bind('<Motion>', self.print_pos)
    self.root.bind("<Button-1>", self.mouse_left_down)  # 鼠标左键点击->显示子窗口
    self.root.bind("<B1-Motion>", self.mouse_left_move)  # 鼠标左键移动->改变子窗口大小
    self.root.bind("<ButtonRelease-1>", self.mouse_left_up)  # 鼠标左键释放->记录最后光标的位置
    self.root.bind("<Return>", self.save_image)  # 回车键->截屏并保存图片
    self.root.focus()

  def start(self):
    self.root.mainloop()

  def print_pos(self, event):
    self.x, self.y = event.widget.winfo_pointerxy()
    self.pos_label.config(text=self.pos_div_text % (self.x, self.y))
    self.pos_div.geometry(f"+{self.x + 10}+{self.y + 10}")

  def change_center_point(self, event):
    offset_x = event.x + self.xstart - self.xcenter - 2
    offset_y = event.y + self.ystart - self.ycenter - 2
    self.center_div.geometry(f"+{self.xstart + event.x - 2}+{self.ystart + event.y - 2}")
    self.center_offset = (offset_x, offset_y)

  def mouse_left_down(self, event):
    if self.center_div is None:
      self.center_div = tk.Toplevel(self.root)
      self.center_div.overrideredirect(True)
      self.center_div.attributes('-topmost', 'true')
      self.center_div.configure(bg="red")
      self.center_div.geometry("4x4")

    self.x, self.y = event.x, event.y
    self.xstart, self.ystart = event.x, event.y
    self.canvas.configure(height=1)
    self.canvas.configure(width=1)
    self.canvas.config(highlightthickness=0)  # 无边框
    self.canvas.place(x=event.x, y=event.y)
    self.center_div.geometry(f"+{self.xstart}+{self.ystart}")

  def mouse_left_move(self, event):
    self.x, self.y = event.x, event.y
    self.xcenter = self.xstart + int((self.x - self.xstart) / 2) - 2
    self.ycenter = self.ystart + int((self.y - self.ystart) / 2) - 2

    self.pos_label.config(text=self.pos_div_text % (self.x, self.y))
    self.pos_div.geometry(f"+{self.x + 10}+{self.y + 10}")
    self.center_div.geometry(f"+{self.xcenter}+{self.ycenter}")

    self.canvas.configure(height=event.y - self.ystart)
    self.canvas.configure(width=event.x - self.xstart)
    self.canvas.coords(self.select_area, 0, 0, event.x - self.xstart, event.y - self.ystart)

  def mouse_left_up(self, event):
    self.xend, self.yend = event.x, event.y

  def save_image(self, event):
    try:
      self.canvas.delete(self.select_area)
      self.canvas.place_forget()
      self.sys_out()

      time.sleep(0.3)
      img = pyautogui.screenshot(region=[self.xstart, self.ystart, self.xend - self.xstart, self.yend - self.ystart])
      self.screenshot_path = os.path.join(application.Server.screenshotPath,
                                          "screenshot-%s.png" % cid.get_snowflake_id())
      img.save(self.screenshot_path)
    except Exception:
      pass

  def sys_out(self, event=None):
    if self.center_div:
      self.center_div.destroy()
    self.pos_div.destroy()
    self.root.destroy()


def screenshot():
  st = ScreenshotTools()
  st.start()
  return st.screenshot_path, st.center_offset
