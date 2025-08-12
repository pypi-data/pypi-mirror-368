import base64
from io import BytesIO

from PIL import Image


def get_size(image_path):
  return Image.open(image_path).size


def change_color(image_path, area=None, rgb_color=None):
  """
  修改图片指定区域颜色
  :param image_path: 图片路径
  :param area: 修改区域： (x1, y1, x2, y2)
  :param rgb_color: 入盘颜色 (255, 0, 0)
  :return:
  """
  with Image.open(image_path) as img:
    if area:
      pixels = img.load()
      for x in range(area[0], area[2]):
        for y in range(area[1], area[3]):
          pixels[x, y] = rgb_color
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_binary = img_bytes.getvalue()
  return img_binary


def img2b64(img: Image, fmt="PNG"):
  buf = BytesIO()
  img.save(buf, format=fmt.upper())
  return base64.b64encode(buf.getvalue()).decode("utf-8")

