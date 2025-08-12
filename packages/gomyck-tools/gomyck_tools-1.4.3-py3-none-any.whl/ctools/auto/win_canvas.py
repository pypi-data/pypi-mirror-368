import tkinter as tk
from multiprocessing import Process, Queue

data_queue: Queue = None
canvas_process: Process = None


class MSGType:
  BOTTOM = 'bottom'  # 置于底部
  DRAW = 'draw'  # 绘制矩形


class CanvasInfo:
  def __init__(self, title: str = '', points: list = None, msg_type: MSGType = MSGType.DRAW):
    self.msg_type = msg_type
    # 标题
    self.title = title
    # 左上, 右上, 右下, 左下
    # [(100, 100), (200, 100), (200, 150), (100, 150)]
    self.points = points


def on_ctrl_click(event):
  print("Ctrl+Left Click detected")


class RecorderTool(tk.Tk):
  def __init__(self, data: Queue):
    super().__init__()
    self.data = data
    self.title('Recorder Tool')
    self.attributes('-topmost', True)
    self.overrideredirect(True)
    self.attributes('-transparentcolor', 'grey')
    self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))
    self.canvas = tk.Canvas(self, highlightthickness=0, bg='grey')
    self.canvas.pack(fill="both", expand=True)
    self.bind('<Control-Button-1>', on_ctrl_click)

    self.check_queue()

  def draw_red_border(self, canvas_info: CanvasInfo):
    self.clear_canvas()
    points = canvas_info.points
    x1, y1 = points[0]
    x2, y2 = points[1]
    x3, y3 = points[2]
    x4, y4 = points[3]
    self.canvas.create_line(x1, y1, x2, y2, fill="red", width=2)
    self.canvas.create_line(x2, y2, x3, y3, fill="red", width=2)
    self.canvas.create_line(x3, y3, x4, y4, fill="red", width=2)
    self.canvas.create_line(x4, y4, x1, y1, fill="red", width=2)
    text_x = (x1 + x2) / 2
    text_y = y1 - 15
    if text_y < 0: text_y = y3 + 15
    self.canvas.create_text(text_x, text_y, text=canvas_info.title, font=("Arial", 12), fill="red")

  def clear_canvas(self):
    self.canvas.delete("all")

  def check_queue(self):
    if not self.data.empty():
      canvas_info = self.data.get_nowait()
      if canvas_info.msg_type == MSGType.BOTTOM:
        self.clear_canvas()
        self.withdraw()
      elif canvas_info.msg_type == MSGType.DRAW:
        self.deiconify()
        self.draw_red_border(canvas_info)
    self.after(10, self.check_queue)


def _init_recorder(data):
  canvas_app = RecorderTool(data)
  canvas_app.mainloop()


def start():
  global data_queue, canvas_process
  data_queue = Queue()
  canvas_process = Process(target=_init_recorder, args=(data_queue,))
  canvas_process.start()
  return canvas_process


def stop():
  canvas_process.terminate()
  canvas_process.join()
  data_queue.close()
