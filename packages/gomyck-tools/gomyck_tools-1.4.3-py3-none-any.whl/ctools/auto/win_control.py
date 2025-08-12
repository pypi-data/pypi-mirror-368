import os
import time

import pyautogui
import uiautomation as auto
from pynput import keyboard

from ctools import application
from ctools import cid
from ctools.auto import win_canvas
from ctools.pools import thread_pool

current_control = None
ctrl_pressed = False
keyboard_listener = None
control_json = {}
screenshot_path = ""


class ControlInfo:
  def __init__(self, ControlType, ClassName, AutomationId, Name, Depth):
    self.ControlType = ControlType
    self.ClassName = ClassName
    self.AutomationId = AutomationId
    self.Name = Name
    # self.Depth = Depth


def get_control_from_cursor():
  global control_json, screenshot_path
  with auto.UIAutomationInitializerInThread():
    win_canvas.data_queue.put(win_canvas.CanvasInfo(msg_type=win_canvas.MSGType.BOTTOM))
    time.sleep(0.2)
    try:
      control = auto.ControlFromCursor()
    except Exception as e:
      print("No control found {}".format(e))
      return
    if control:
      # 当前控件信息
      global current_control
      current_control = control
      # 绘制矩形
      canvas_info = win_canvas.CanvasInfo(control.Name, [
        (control.BoundingRectangle.left, control.BoundingRectangle.top),
        (control.BoundingRectangle.right, control.BoundingRectangle.top),
        (control.BoundingRectangle.right, control.BoundingRectangle.bottom),
        (control.BoundingRectangle.left, control.BoundingRectangle.bottom)
      ])
      win_canvas.data_queue.put(canvas_info)
      control_json = {}
      c_info = ControlInfo(ControlType=current_control.ControlType, ClassName=current_control.ClassName, AutomationId=current_control.AutomationId, Name=current_control.Name, Depth=0)
      _depth = 0
      while current_control:
        current_control = current_control.GetParentControl()
        if current_control: _depth += 1
      c_info.Depth = _depth
      control_json.update(c_info.__dict__)

      img = pyautogui.screenshot(region=[control.BoundingRectangle.left, control.BoundingRectangle.top,
                                         control.BoundingRectangle.width(), control.BoundingRectangle.height()])
      screenshot_path = os.path.join(application.Server.screenshotPath, "screenshot-%s.png" % cid.get_snowflake_id())
      img.save(screenshot_path)
      # xx = auto.Control(**control_json)
      # print(control_json)
      # time.sleep(2)
      # xx.Click()


def on_press(key):
  global ctrl_pressed, keyboard_listener
  if key == keyboard.Key.ctrl_l and not ctrl_pressed:
    ctrl_pressed = True
    thread_pool.submit(get_control_from_cursor)
  elif key == keyboard.Key.esc:
    win_canvas.stop()
    keyboard_listener.stop()
  elif hasattr(key, 'vk') and key.vk == 192 and ctrl_pressed:
    win_canvas.stop()
    keyboard_listener.stop()
    # pg.alert('采集成功!')


def on_release(key):
  global ctrl_pressed
  if key == keyboard.Key.ctrl_l:
    ctrl_pressed = False
    win_canvas.data_queue.put(win_canvas.CanvasInfo(msg_type=win_canvas.MSGType.BOTTOM))


def start():
  global keyboard_listener
  win_canvas.start()
  keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
  keyboard_listener.start()
  keyboard_listener.join()


def get_control_json():
  global current_control, ctrl_pressed, keyboard_listener, control_json
  current_control = None
  ctrl_pressed = False
  keyboard_listener = None
  control_json = {}
  start()
  if len(control_json) == 0:
    time.sleep(0.5)
  return control_json, screenshot_path


if __name__ == '__main__':
  a = get_control_json()
  print(a)
