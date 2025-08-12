import inspect
import threading
from functools import wraps

import bottle
from bottle import response, Bottle, request

from ctools import call
from ctools.dict_wrapper import DictWrapper
from ctools.sys_log import flog as log
from ctools.util.cklock import try_lock
from ctools.web import ctoken
from ctools.web.api_result import R

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 * 50
func_has_params = {}
app_cache = {}

class GlobalState:
  lock = threading.Lock()
  withOutLoginURI = {
    '/',
    '/index',
    '/login',
    '/favicon.ico',
  }
  allowRemoteCallURI = set()
  auth_ignore_func = set()
  token = {}
  interceptors = []

def join_path(*parts):
  """拼接 url"""
  cleaned_parts = [p.strip('/') for p in parts if p and p.strip('/')]
  return '/' + '/'.join(cleaned_parts)

@call.once
def cache_white_list(app):
  """缓存白名单"""
  for route in app.routes:
    real_func = route.config.get('mountpoint.target')
    if not real_func: continue
    for method, routes in real_func.router.static.items():
      for path, tuples in routes.items():
        req_func = inspect.getmodule(tuples[0].callback).__name__ + "." + tuples[0].callback.__name__
        if req_func in GlobalState.auth_ignore_func:
          print("add white list: {}".format(join_path(app.context_path, real_func.context_path, path)))
          GlobalState.withOutLoginURI.add(join_path(app.context_path, real_func.context_path, path))

def init_app(context_path="/", main_app=False):
  with try_lock(block=True):
    cache_app = app_cache.get(context_path)
    if cache_app: return cache_app
    app = Bottle()
    app_cache[context_path] = app
    app.context_path = context_path if context_path else "/"

  def init_main_app():
    @app.hook('before_request')
    def before_request():
      if request.path.startswith('/static') or request.path in GlobalState.withOutLoginURI: return
      for interceptor in GlobalState.interceptors:
        res: R = interceptor['func']()
        if res.code != 200: bottle.abort(res.code, res.message)

    @app.error(401)
    def unauthorized(error):
      response.status = 401
      log.error("系统未授权: {} {} {}".format(error.body, request.method, request.fullpath))
      return R.error(resp=R.Code.cus_code(401, "系统未授权! {}".format(error.body)))

    @app.error(403)
    def unauthorized(error):
      response.status = 403
      log.error("访问受限: {} {} {}".format(error.body, request.method, request.fullpath))
      return R.error(resp=R.Code.cus_code(403, "访问受限: {}".format(error.body)))

    @app.error(404)
    def not_found(error):
      response.status = 404
      log.error("404 not found : {} {} {}".format(error.body, request.method, request.fullpath))
      return R.error(resp=R.Code.cus_code(404, "资源未找到: {}".format(error.body)))

    @app.error(405)
    def method_not_allow(error):
      response.status = 405
      log.error("请求方法错误: {} {} {}".format(error.status_line, request.method, request.fullpath))
      return R.error(resp=R.Code.cus_code(405, '请求方法错误: {}'.format(error.status_line)))

    @app.error(500)
    def internal_error(error):
      response.status = 500
      log.error("系统发生错误: {} {} {}".format(error.body, request.method, request.fullpath))
      return R.error(msg='系统发生错误: {}'.format(error.exception))

    @app.hook('after_request')
    def after_request():
      enable_cors()

  if main_app: init_main_app()
  app.install(params_resolve)
  return app


def enable_cors():
  response.headers['Access-Control-Allow-Origin'] = '*'
  response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
  request_headers = request.headers.get('Access-Control-Request-Headers')
  response.headers['Access-Control-Allow-Headers'] = request_headers if request_headers else ''
  response.headers['Access-Control-Expose-Headers'] = '*'


# annotation
def before_intercept(order=0):
  def decorator(func):
    for interceptor in GlobalState.interceptors:
      if interceptor['func'].__name__ == func.__name__:
        log.info("duplicate interceptor: {}".format(func.__name__))
        return
    log.info("add before interceptor: {}".format(func.__name__))
    GlobalState.interceptors.append({'order': order, 'func': func})
    GlobalState.interceptors = sorted(GlobalState.interceptors, key=lambda x: x['order'])

  return decorator

# annotation
def auth_ignore(func):
  """忽略登录验证的接口"""
  ignore_req_func = inspect.getmodule(func).__name__ + "." + func.__name__
  if ignore_req_func in GlobalState.auth_ignore_func: raise Exception("duplicate ignore func: {}".format(ignore_req_func))
  GlobalState.auth_ignore_func.add(ignore_req_func)
  @wraps(func)
  def decorated(*args, **kwargs):
    return func(*args, **kwargs)
  return decorated

# annotation
def rule(key):
  def return_func(func):
    @wraps(func)
    def decorated(*args, **kwargs):
      rules = ctoken.get_token_attr("rules") or []
      if _match_rule_by_prefix(key, rules):
        return func(*args, **kwargs)
      else:
        return R.error("权限不足, 请联系管理员: {}".format(key))
    return decorated
  return return_func

def _match_rule_by_prefix(key, rules):
  for r in rules:
    if key.startswith(r):
      return True
  return False

# annotation or plugins, has auto install, don't need to call
def params_resolve(func):
  @wraps(func)
  def decorated(*args, **kwargs):
    if func_has_params.get(request.fullpath) is not None and not func_has_params.get(request.fullpath):
      return func(*args, **kwargs)
    if func_has_params.get(request.fullpath) is None:
      sig = inspect.signature(func)
      params = sig.parameters
      if not params.get('params'):
        func_has_params[request.fullpath] = False
        return func(*args, **kwargs)
      else:
        func_has_params[request.fullpath] = True
    if request.method == 'GET' or request.method == 'DELETE':
      queryStr = request.query.decode('utf-8')
      page_info = PageInfo(
        page_size=10 if request.headers.get('page_size') is None else int(request.headers.get('page_size')),
        page_index=1 if request.headers.get('page_index') is None else int(request.headers.get('page_index'))
      )
      queryStr = auto_exchange(func, queryStr)
      queryStr.page_info = page_info
      return func(params=queryStr, *args, **kwargs)
    elif request.method == 'POST' or request.method == 'PUT':
      query_params = request.query.decode('utf-8')
      content_type = request.get_header('content-type')
      if content_type == 'application/json':
        params = request.json or {}
        dict_wrapper = DictWrapper(params)
        dict_wrapper.update(query_params.dict)
        return func(params=auto_exchange(func, dict_wrapper), *args, **kwargs)
      elif 'multipart/form-data' in content_type:
        form_data = request.forms.decode()
        form_files = request.files.decode()
        dict_wrapper = DictWrapper(form_data)
        dict_wrapper.update(query_params.dict)
        dict_wrapper.files = form_files
        return func(params=auto_exchange(func, dict_wrapper), *args, **kwargs)
      elif 'application/x-www-form-urlencoded' in content_type:
        params = request.forms.decode()
        dict_wrapper = DictWrapper(params.dict)
        dict_wrapper.update(query_params.dict)
        return func(params=auto_exchange(func, dict_wrapper), *args, **kwargs)
      elif 'text/plain' in content_type:
        params = request.body.read().decode('utf-8')
        dict_wrapper = DictWrapper({'body': params})
        dict_wrapper.update(query_params.dict)
        return func(params=auto_exchange(func, dict_wrapper), *args, **kwargs)
    else:
      return func(*args, **kwargs)

  return decorated

# 自动转换参数类型
def auto_exchange(func, dict_wrapper):
  model_class = func.__annotations__.get('params')
  if model_class:
    try:
      model_instance = model_class(**dict_wrapper)
      return model_instance
    except Exception as e:
      log.exception(e)
      return dict_wrapper
  else:
    return dict_wrapper

# 分页信息对象
class PageInfo:
  def __init__(self, page_size, page_index):
    self.page_size = page_size
    self.page_index = page_index


# 通用的鉴权方法
def common_auth_verify() -> R:
  valid = ctoken.is_valid()
  if valid: return R.ok(to_json_str=False)
  return R.error(resp=R.Code.cus_code(401, "请登录!"), to_json_str=False)
