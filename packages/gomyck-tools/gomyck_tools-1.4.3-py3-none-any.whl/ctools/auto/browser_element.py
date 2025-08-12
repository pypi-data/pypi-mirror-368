import os
import time

from business.common.constant import Scheduler
from lxml import etree
from lxml import html
from pynput import keyboard
from selenium import webdriver
from selenium.common import NoSuchElementException, WebDriverException, NoSuchWindowException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from urllib3.exceptions import MaxRetryError

from ctools import application
from ctools.util import cid

keyboard_listener = None
ctrl_pressed = None
g_driver = None
g_callback = None
g_result = []
g_quite_flag = False
picture_path = ""


def get_hovered_element_html(url, explore, callback):
  global g_driver, g_callback, g_result
  g_callback = callback
  g_driver = explore.init()
  driver = g_driver
  driver.maximize_window()
  driver.get(url)
  start_keyboard_listener()
  handle_arr = [driver.current_window_handle]
  close_page_flag = False
  while g_driver and not g_quite_flag:
    try:
      try:
        if len(driver.window_handles) == 0:
          break_func()
          break
      except WebDriverException:
        break_func()
        break
      except MaxRetryError:
        break_func()
        break
      try:
        driver.find_element(value="ck-overlay")
      except NoSuchElementException as e:
        driver.execute_script(explore.listen_script)
      except Exception:
        pass
      for handle in driver.window_handles:
        if handle in handle_arr: continue
        if not close_page_flag: driver.execute_script(overlay_script)
        handle_arr.append(handle)
        driver.switch_to.window(handle)
        try:
          driver.execute_script(explore.listen_script)
        except Exception:
          continue
      close_page_flag = False
      time.sleep(0.5)
      cursor_html = driver.execute_script(explore.return_script)
      if cursor_html:
        g_result.clear()
        cursor_dom = html.fragment_fromstring(cursor_html)
        cursor_dom.set("ck-flag", "ck")
        enhance_cursor_html = etree.tostring(cursor_dom, method="html", encoding="unicode")
        page_html = driver.page_source.replace(cursor_html, enhance_cursor_html)
        page_dom_tree = etree.ElementTree(etree.HTML(page_html))
        match_dom = page_dom_tree.xpath('//*[@ck-flag="ck"]')
        for ck_element in match_dom:
          ck_xpath = page_dom_tree.getpath(ck_element)
          # print('XPATH IS {}'.format(ck_xpath))
          try:
            ele = driver.find_element(By.XPATH, ck_xpath)
            # print('XPATH_HTML: {}'.format(ele.get_attribute('outerHTML')))
          except Exception:
            pass
          g_result.append(ck_xpath)
    except NoSuchWindowException as e:
      close_page_flag = True
      handle_arr = []
      try:
        driver.switch_to.window(driver.window_handles[-1])
        driver.execute_script(hide_shade)
      except Exception:
        print('切换HANDLE失败:', e)
        break_func()
        break
    except Exception as e:
      print('全局错误:', e)
      break_func()
      break
  try:
    g_driver.quit()
  except Exception as e:
    pass


def break_func():
  keyboard_listener.stop()
  g_callback(None)


def on_press(key):
  global keyboard_listener, ctrl_pressed, g_driver, g_quite_flag, picture_path
  if key == keyboard.Key.ctrl_l and not ctrl_pressed:
    ctrl_pressed = True
  elif key == keyboard.Key.esc:
    g_result.clear()
    keyboard_listener.stop()
    g_quite_flag = True
    g_callback(None)
  elif hasattr(key, 'vk') and key.vk == 192 and ctrl_pressed:
    # print("g_result: %s" % g_result)
    if g_result:
      try:
        select_element = g_driver.find_element(By.XPATH, g_result[0])
        picture_path = "%s.png" % os.path.join(application.Server.screenshotPath, "element-" + cid.get_uuid())
        select_element.screenshot(picture_path)
      except Exception:
        pass

    keyboard_listener.stop()
    g_quite_flag = True
    g_callback(g_result)


def on_release(key):
  global ctrl_pressed
  if key == keyboard.Key.ctrl_l:
    ctrl_pressed = False


def start_keyboard_listener():
  global keyboard_listener
  keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
  keyboard_listener.start()


overlay_script = """
// 创建遮罩层
var shade = document.createElement('div');
shade.id = 'ck-shade-parent';
shade.style.position = 'fixed';
shade.style.top = '0';
shade.style.left = '0';
shade.style.width = '100%';
shade.style.height = '100%';
shade.style.backgroundColor = '#000'; // 使用纯色背景
shade.style.filter = 'alpha(opacity=60)'; // 设置透明度，IE8-IE9
shade.style.opacity = '0.8'; // 设置透明度，现代浏览器
shade.style.zIndex = '9999';
document.body.appendChild(shade);

// 创建覆盖内容
var overlayContent = document.createElement('div');
overlayContent.id = 'ck-shade-oc';
overlayContent.className = 'overlay-content';
overlayContent.style.position = 'absolute';
overlayContent.style.top = '50%';
overlayContent.style.left = '50%';
overlayContent.style.transform = 'translate(-50%, -50%)';
overlayContent.style.backgroundColor = 'white';
overlayContent.style.padding = '20px';
overlayContent.style.borderRadius = '8px';
overlayContent.style.textAlign = 'center';
shade.appendChild(overlayContent);

// 创建消息内容
var message = document.createElement('p');
message.id = 'ck-shade-msg';
message.innerText = '当前页面未激活，请关闭激活状态的录制页面';
message.style.color = '#000'; // 设置文本颜色为黑色
message.style.fontSize = '16px'; // 设置文本大小
overlayContent.appendChild(message);

"""

hide_shade = """
var shade = document.getElementById('ck-shade-parent');
if (shade) {
    shade.parentNode.removeChild(shade);
}
"""


class IE:

  @staticmethod
  def init():
    ie_options = webdriver.IeOptions()
    ie_options.ignore_protected_mode_settings = True
    ie_options.ignore_zoom_level = True
    ie_options.require_window_focus = True
    return webdriver.Ie(options=ie_options)

  listen_script = """
    var overlay = document.createElement('div');
    overlay.id = 'ck-overlay';
    overlay.style.position = 'absolute';
    overlay.style.border = '2px solid red';
    overlay.style.pointerEvents = 'none';
    overlay.style.zIndex = '9999';
    document.body.appendChild(overlay);
    var addEvent = function(elem, type, eventHandle) {
      if (elem == null || typeof(elem) == 'undefined') return;
      if (elem.addEventListener) {
        elem.addEventListener(type, eventHandle, false);
      } else if (elem.attachEvent) {
        elem.attachEvent('on' + type, eventHandle);
      } else {
        elem['on' + type] = eventHandle;
      }
    };

    addEvent(document, 'mousemove', function(e) {
      e = e || window.event;
      var element = document.elementFromPoint(e.clientX, e.clientY);
      window.hoveredElement = element;
      if (element === overlay) return;
      var rect = element.getBoundingClientRect();
      overlay.style.left = (rect.left + (window.pageXOffset || document.documentElement.scrollLeft || document.body.scrollLeft) - 5) + 'px';
      overlay.style.top = (rect.top + (window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop) - 5) + 'px';
      overlay.style.width = (element.offsetWidth + 10)  + 'px';
      overlay.style.height = (element.offsetHeight + 10) + 'px';
    });
    """

  return_script = """
    return window.hoveredElement ? window.hoveredElement.outerHTML : null;
  """

  overlay_script = overlay_script


class Chrome:

  @staticmethod
  def init():
    option = Options()
    option.binary_location = Scheduler.CHROME_PATH
    service = Service(Scheduler.CHROME_DRIVER_PATH)
    return webdriver.Chrome(options=option, service=service)

  listen_script = """
    var overlay = document.createElement('div');
    overlay.id = 'ck-overlay';
    overlay.style.position = 'absolute';
    overlay.style.border = '2px solid red';
    overlay.style.pointerEvents = 'none';
    overlay.style.zIndex = '9998';
    document.body.appendChild(overlay);

    function throttle(func, limit) {
      let inThrottle;
      return function() {
        const args = arguments,
          context = this;
        if (!inThrottle) {
          func.apply(context, args);
          inThrottle = true;
          setTimeout(() => inThrottle = false, limit);
        }
      };
    }

    document.addEventListener('mousemove', throttle(function(e) {
      var element = document.elementFromPoint(e.clientX, e.clientY);
      window.hoveredElement = element;
      if(element.id.indexOf('ck-shade') !== -1) return;
      if (window.hoveredElement) {
        var rect = element.getBoundingClientRect();
        overlay.style.left = (rect.left + window.pageXOffset - 5) + 'px';
        overlay.style.top = (rect.top + window.pageYOffset - 5) + 'px';
        overlay.style.width = (element.offsetWidth + 10) + 'px';
        overlay.style.height = (element.offsetHeight + 10) + 'px';
      }
    }, 50));
    """

  return_script = """
    return window.hoveredElement ? window.hoveredElement.outerHTML : null;
  """

  overlay_script = overlay_script


def callback(xpath):
  print("Hovered Element XPATH IS :", xpath)


def get_element(url: str = None, explore: str = "chrome"):
  global keyboard_listener, ctrl_pressed, g_driver, g_callback, g_result, g_quite_flag, picture_path
  keyboard_listener = None
  ctrl_pressed = None
  g_driver = None
  g_callback = None
  g_result = []
  g_quite_flag = False
  picture_path = ""

  if explore == "chrome":
    explore = Chrome
  else:
    explore = IE

  if "http" not in url[:5]:
    url = "http://%s" % url

  get_hovered_element_html(url, explore, callback)

  return g_result, picture_path


if __name__ == "__main__":
  # from explore_record_core import get_hovered_element_html, Chrome
  g_result, picture_path = get_element("weibo.com")
  print(g_result, picture_path)
