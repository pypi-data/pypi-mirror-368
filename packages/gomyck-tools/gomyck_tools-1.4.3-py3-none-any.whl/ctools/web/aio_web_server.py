#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""A lightweight async HTTP server based on aiohttp."""

__author__ = 'haoyang'
__date__ = '2025/5/30 09:54'

import asyncio
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from aiohttp import web
from ctools import sys_info, cjson
from ctools.sys_log import flog as log
from ctools.web.api_result import R

DEFAULT_PORT = 8888

@web.middleware
async def response_wrapper_middleware(request, handler):
  try:
    result = await handler(request)
    if isinstance(result, web.Response):
      return result
    elif isinstance(result, str):
      return web.Response(text=result, content_type='application/json')
    elif isinstance(result, dict):
      return web.Response(text=cjson.dumps(result), content_type='application/json')
    else:
      return result
  except web.HTTPException as http_exc:
    raise http_exc
  except Exception as e:
    log.error(f"Error in response_wrapper_middleware: {e}", exc_info=True)
    return web.json_response(text=R.error(str(e)), status=500, content_type='application/json')


class AioHttpServer:
  def __init__(self, port: int = DEFAULT_PORT, app: Optional[web.Application] = None, routes: Optional[web.RouteTableDef] = None, async_func=None):
    """
    Initialize the HTTP server.

    Args:
        port: Port number to listen on
        app: Optional existing aiohttp Application instance
    """
    self.app = app or web.Application(middlewares=[response_wrapper_middleware])
    self.port = port
    self.index_root = Path('./')
    self.index_filename = 'index.html'
    self.is_tpl = False
    self.template_args: Dict[str, Any] = {}
    self.redirect_url: Optional[str] = None
    self.static_root = Path('./static')
    self.download_root = Path('./download')
    self.routes = routes
    self.async_func = async_func

    # Register routes
    self.app.add_routes([
      web.get('/', self.handle_index),
      web.get('/index', self.handle_index),
      web.get('/static/{filepath:.*}', self.handle_static),
      web.get('/download/{filepath:.*}', self.handle_download)
    ])
    if self.routes:
      self.app.add_routes(self.routes)

  async def handle_index(self, request: web.Request) -> web.StreamResponse:
    """Handle requests to the index page."""
    if self.redirect_url:
      return web.HTTPFound(self.redirect_url)

    index_path = self.index_root / self.index_filename

    if not index_path.exists():
      return web.HTTPNotFound()

    if self.is_tpl:
      return web.FileResponse(
        index_path,
        headers={'Content-Type': 'text/html'}
      )
    return web.FileResponse(index_path)

  async def handle_static(self, request: web.Request) -> web.StreamResponse:
    """Handle static file requests."""
    filepath = Path(request.match_info['filepath'])
    full_path = self.static_root / filepath

    if not full_path.exists():
      return web.HTTPNotFound()

    return web.FileResponse(full_path)

  async def handle_download(self, request: web.Request) -> web.StreamResponse:
    """Handle file download requests."""
    filepath = Path(request.match_info['filepath'])
    full_path = self.download_root / filepath

    if not full_path.exists():
      return web.HTTPNotFound()

    return web.FileResponse(
      full_path,
      headers={'Content-Disposition': f'attachment; filename="{filepath.name}"'}
    )

  def set_index(
    self,
    filename: str = 'index.html',
    root: str = './',
    is_tpl: bool = False,
    redirect_url: Optional[str] = None,
    **kwargs: Any
  ) -> None:
    """
    Configure index page settings.

    Args:
        filename: Name of the index file
        root: Root directory for index file
        is_tpl: Whether the file is a template
        redirect_url: URL to redirect to instead of serving index
        kwargs: Additional template arguments
    """
    self.index_root = Path(root)
    self.index_filename = filename
    self.is_tpl = is_tpl
    self.redirect_url = redirect_url
    self.template_args = kwargs

  def set_static(self, root: str = './static') -> None:
    """Set the root directory for static files."""
    self.static_root = Path(root)

  def set_download(self, root: str = './download') -> None:
    """Set the root directory for downloadable files."""
    self.download_root = Path(root)

  async def run(self) -> None:
    """Run the server."""
    if self.async_func:
      await self.async_func()

    print(
      'Server running at:\n'
      f'\tLocal: http://localhost:{self.port}\n'
      f'\tNetwork: http://{sys_info.get_local_ipv4()}:{self.port}',
      file=sys.stderr
    )
    runner = None
    try:
      runner = web.AppRunner(self.app)
      await runner.setup()
      site = web.TCPSite(runner, host='0.0.0.0', port=self.port)
      await site.start()
      while True: await asyncio.sleep(3600)
    except Exception as e:
      print(f"Server failed to start: {e}", file=sys.stderr)
    finally:
      await runner.cleanup()


def init_routes() -> web.RouteTableDef:
  return web.RouteTableDef()


def init_server(routes: Optional[web.RouteTableDef] = None, app: Optional[web.Application] = None, port: int = DEFAULT_PORT, async_func=None) -> AioHttpServer:
  """Initialize and return a new AioHttpServer instance."""
  return AioHttpServer(port=port, app=app, routes=routes, async_func=async_func)


async def get_stream_resp(request, content_type: str = 'text/event-stream') -> web.StreamResponse:
  resp = web.StreamResponse(
    status=200,
    reason='OK',
    headers={
      'Content-Type': content_type,
      'Cache-Control': 'no-cache',
      'X-Accel-Buffering': 'no',
    }
  )
  await resp.prepare(request)
  return resp
