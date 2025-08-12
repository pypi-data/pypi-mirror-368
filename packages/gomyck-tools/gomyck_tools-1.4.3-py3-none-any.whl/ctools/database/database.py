import contextlib
import datetime
import math
import threading

from sqlalchemy import create_engine, BigInteger, Column, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text

from ctools import call
from ctools import cid
from ctools.pools.thread_pool import thread_local
from ctools.web.bottle_web_base import PageInfo

"""
class XXXX(BaseMixin):
  __tablename__ = 't_xxx_info'
  __table_args__ = {'comment': 'xxx信息表'}
  server_content: Column = Column(String(50), nullable=True, default='', comment='123123')
  server_ip: Column = Column(String(30), index=True)
  user_id: Column = Column(BigInteger)

database.init_db('postgresql://postgres:123456@192.168.3.107:32566/abc', default_schema='public', db_key='source', pool_size=100)
with database.get_session('source') as s:
  s.execute(text('insert into xxx (name) values (:name)'), {'name': string_tools.get_random_str(5)})
  s.commit()
"""

Base = None
inited_db = {}
engines = {}
sessionMakers = {}


def getEngine(db_key: str = 'default'):
  return engines[db_key]


@call.init
def _init():
  global Base
  Base = declarative_base()


"""
The string form of the URL is
dialect[+driver]://user:password@host/dbname[?key=value..]
where ``dialect`` is a database name such as ``mysql``, ``oracle``, ``postgresql``, etc.
and ``driver`` the name of a DBAPI such as ``psycopg2``, ``pyodbc``, ``cx_oracle``, etc.  Alternatively
"""


# 密码里的@  要替换成 %40

# sqlite connect_args={"check_same_thread": False}  db_url=sqlite:///{}.format(db_url)
# sqlite 数据库, 初始化之后, 优化一下配置
# $ sqlite3 app.db
# > PRAGMA journal_mode=WAL; 设置事务的模式, wal 允许读写并发, 但是会额外创建俩文件
# > PRAGMA synchronous=NORMAL; 设置写盘策略, 默认是 FULL, 日志,数据都落, 设置成 NORMAL, 日志写完就算事务完成

def init_db(db_url: str, db_key: str = 'default', connect_args: dict = {}, default_schema: str = None, pool_size: int = 5, max_overflow: int = 25, echo: bool = False, auto_gen_table: bool = False):
  if db_url.startswith('mysql'):
    import pymysql
    pymysql.install_as_MySQLdb()
  if inited_db.get(db_key): raise Exception('db {} already init!!!'.format(db_key))
  global engines, sessionMakers
  if default_schema: connect_args.update({'options': '-csearch_path={}'.format(default_schema)})
  engine, sessionMaker = _create_connection(db_url=db_url, connect_args=connect_args, pool_size=pool_size, max_overflow=max_overflow, echo=echo)
  engines[db_key] = engine
  sessionMakers[db_key] = sessionMaker
  inited_db[db_key] = True
  # 这个有并发问题, 高并发会导致卡顿, 可以考虑去做一些别的事儿
  #if default_schema: event.listen(engine, 'connect', lambda dbapi_connection, connection_record: _set_search_path(dbapi_connection, default_schema))
  if auto_gen_table: Base.metadata.create_all(engine)


def _set_search_path(dbapi_connection, default_schema):
  with dbapi_connection.cursor() as cursor:
    cursor.execute(f'SET search_path TO {default_schema}')


def _create_connection(db_url: str, pool_size: int = 5, max_overflow: int = 25, connect_args={}, echo: bool = False):
  engine = create_engine('{}'.format(db_url),
                         echo=echo,
                         future=True,
                         pool_size=pool_size,
                         max_overflow=max_overflow,
                         pool_pre_ping=True,
                         pool_recycle=3600,
                         connect_args=connect_args)
  sm = sessionmaker(bind=engine, expire_on_commit=False)
  return engine, sm


def generate_custom_id():
  return str(cid.get_snowflake_id())


class BaseMixin(Base):
  __abstract__ = True
  obj_id = Column(BigInteger, primary_key=True, default=generate_custom_id)

  # ext1 = Column(String)
  # ext2 = Column(String)
  # ext3 = Column(String)
  # create_time = Column(DateTime, nullable=False, default=datetime.datetime.now)
  # update_time = Column(DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now, index=True)

  def to_dict(self):
    return self.__getstate__()

  def from_dict(self, v):
    self.__dict__.update(v)

  def __getstate__(self):
    ret_state = {}
    state = self.__dict__.copy()
    for key in state.keys():
      if not key.startswith("_"):
        if type(state[key]) == datetime.datetime:
          ret_state[key] = state[key].strftime("%Y-%m-%d %H:%M:%S")
        else:
          ret_state[key] = state[key]
    return ret_state

  @classmethod
  def init(cls, data: dict):
    valid_keys = cls.__table__.columns.keys()
    filtered = {k: v for k, v in data.items() if k in valid_keys}
    return cls(**filtered)

@contextlib.contextmanager
def get_session(db_key: str = 'default') -> Session:
  thread_local.db_key = db_key
  if sm := sessionMakers.get(db_key):
    s = sm()
  else:
    raise ValueError("Invalid db_key: {}".format(db_key))
  try:
    yield s
  except Exception as e:
    s.rollback()
    raise e
  finally:
    s.close()


class PageInfoBuilder:

  def __init__(self, pageInfo: PageInfo, total_count, records):
    self.page_size = pageInfo.page_size
    self.page_index = pageInfo.page_index
    self.total_count = total_count
    self.total_page = math.ceil(total_count / int(pageInfo.page_size))
    self.records = records


def query_by_page(query, pageInfo) -> PageInfoBuilder:
  """
  使用方法:
    with database.get_session() as s:
      query = s.query(AppInfoEntity).filter(AppInfoEntity.app_name.contains(params.app_name))
      result = database.query_by_page(query, params.page_info)
      return R.ok(result)
  """
  records = query.offset((pageInfo.page_index - 1) * pageInfo.page_size).limit(pageInfo.page_size).all()
  rs = []
  for r in records:
    rs.append(r)
  return PageInfoBuilder(pageInfo, query.count(), rs)


def query4_crd_sql(session, sql: str, params: dict) -> []:
  records = session.execute(text(sql), params).fetchall()
  rs = []
  for record in records:
    data = {}
    for index, key in enumerate(record._mapping):
      data[key] = record[index]
    rs.append(data)
  return rs


sqlite_and_pg_page_sql = """
 limit :limit offset :offset
"""
mysql_page_sql = """
 limit :offset, :limit
"""


def query_by_page4_crd_sql(session, sql: str, params: dict, pageInfo: PageInfo) -> []:
  db_name = engines[thread_local.db_key].name
  if db_name == 'postgresql' or db_name == 'sqlite':
    page_sql = sqlite_and_pg_page_sql
  elif db_name == 'mysql':
    page_sql = mysql_page_sql
  else:
    raise Exception('not support db: {}'.format(db_name))
  wrapper_sql = """
    select * from ({}) as t {}
  """.format(sql, page_sql)
  count_sql = """
    select count(1) from ({}) as t
  """.format(sql)
  params["limit"] = pageInfo.page_size
  params["offset"] = (pageInfo.page_index - 1) * pageInfo.page_size
  records = session.execute(text(wrapper_sql), params).fetchall()
  rs = []
  for record in records:
    data = {}
    for index, key in enumerate(record._mapping):
      data[key] = record[index]
    rs.append(data)
  return PageInfoBuilder(pageInfo, session.execute(text(count_sql), params).first()[0], rs)
