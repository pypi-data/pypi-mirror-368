from ctools.util.snow_id import SnowId

idWorker = SnowId(1, 2, 0)


def get_snowflake_id():
  return idWorker.get_id()


def get_snowflake_id_str():
  return str(get_snowflake_id())

def get_random_str(size: int = 10) -> str:
  import random
  return "".join(random.sample('abcdefghjklmnpqrstuvwxyz123456789', size))


def get_uuid() -> str:
  import uuid
  return str(uuid.uuid1()).replace("-", "")
