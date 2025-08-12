import tkinter as tk

"""
规划区域工具类, 按回车获取区域坐标
image_path=screenshot_tools.screenshot()
"""


class PlanAreaTools:
  def __init__(self):
    self.root = tk.Tk()
    self.root.overrideredirect(True)
    self.root.attributes("-alpha", 0.1)
    self.root.attributes('-topmost', 'true')
    self.root.geometry("{0}x{1}+0+0".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
    self.root.configure(bg="black")

    self.canvas = tk.Canvas(self.root)

    self.x, self.y = 0, 0
    self.xstart, self.ystart = 0, 0
    self.xend, self.yend = 0, 0
    self.xcenter, self.ycenter = 0, 0

    self.select_area = self.canvas.create_rectangle(0, 0, 0, 0, outline='red', width=0, dash=(4, 4))
    self.center_offset = (0, 0)

    self.pos_div = tk.Toplevel(self.root)
    self.pos_div.overrideredirect(True)
    self.pos_div.attributes('-topmost', 'true')
    self.pos_div.configure(bg="grey")
    self.pos_div.geometry("270x25")

    self.pos_div_text = "POS: (%s, %s), Enter键-获取区域, Esc键-退出"
    self.pos_label = tk.Label(self.pos_div, text=self.pos_div_text % (0, 0), bg="black", fg="white")
    self.pos_label.pack(fill="both", expand=True)

    self.root.bind('<Escape>', self.sys_out)  # 键盘Esc键->退出
    self.root.bind('<Motion>', self.print_pos)
    self.root.bind("<Button-1>", self.mouse_left_down)  # 鼠标左键点击->显示子窗口
    self.root.bind("<B1-Motion>", self.mouse_left_move)  # 鼠标左键移动->改变子窗口大小
    self.root.bind("<ButtonRelease-1>", self.mouse_left_up)  # 鼠标左键释放->记录最后光标的位置
    self.root.bind("<Return>", self.save_area)  # 回车键->获取区域信息
    self.root.focus()

    self.area = [0, 0, 0, 0]

  def start(self):
    self.root.mainloop()

  def print_pos(self, event):
    self.x, self.y = event.widget.winfo_pointerxy()
    self.pos_label.config(text=self.pos_div_text % (self.x, self.y))
    self.pos_div.geometry(f"+{self.x + 10}+{self.y + 10}")

  def mouse_left_down(self, event):
    self.x, self.y = event.x, event.y
    self.xstart, self.ystart = event.x, event.y
    self.canvas.configure(height=1)
    self.canvas.configure(width=1)
    self.canvas.config(highlightthickness=0)
    self.canvas.place(x=event.x, y=event.y)

  def mouse_left_move(self, event):
    self.x, self.y = event.x, event.y
    self.xcenter = self.xstart + int((self.x - self.xstart) / 2) - 2
    self.ycenter = self.ystart + int((self.y - self.ystart) / 2) - 2

    self.pos_label.config(text=self.pos_div_text % (self.x, self.y))
    self.pos_div.geometry(f"+{self.x + 10}+{self.y + 10}")

    self.canvas.configure(height=event.y - self.ystart)
    self.canvas.configure(width=event.x - self.xstart)
    self.canvas.coords(self.select_area, 0, 0, event.x - self.xstart, event.y - self.ystart)

  def mouse_left_up(self, event):
    self.xend, self.yend = event.x, event.y

  def save_area(self, event):
    try:
      self.area = [self.xstart, self.ystart, self.xend, self.yend]
      self.canvas.delete(self.select_area)
      self.canvas.place_forget()
      self.sys_out()

    except Exception:
      pass

  def sys_out(self, event=None):
    self.pos_div.destroy()
    self.root.destroy()


def get_area():
  pat = PlanAreaTools()
  pat.start()
  return tuple(pat.area)

# if __name__ == '__main__':
#     get_area()
