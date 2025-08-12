import asyncio
import importlib.util

banner = """

 ██████╗████████╗ ██████╗  ██████╗ ██╗     ███████╗
██╔════╝╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
██║        ██║   ██║   ██║██║   ██║██║     ███████╗
██║        ██║   ██║   ██║██║   ██║██║     ╚════██║
╚██████╗   ██║   ╚██████╔╝╚██████╔╝███████╗███████║
 ╚═════╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝   --by gomyck 2025
"""

print(banner)

if importlib.util.find_spec("uvloop"):
  import uvloop
  asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
  print("uvloop version:", uvloop.__version__)
else:
  print("uvloop not installed, using default asyncio loop")
