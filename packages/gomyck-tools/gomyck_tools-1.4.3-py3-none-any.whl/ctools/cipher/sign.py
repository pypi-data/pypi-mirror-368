import hashlib
import hmac

global_key = 'gomyck2014'


def generate_signature(file_path, key: str = global_key):
  try:
    with open(file_path, 'rb') as f:
      file_contents = f.read()
      file_hash = hashlib.sha256(file_contents).digest()
    sign_val = hmac.new(key.encode(), file_hash, hashlib.sha256).digest()
    return sign_val.hex()
  except:
    return ''


def digest(value: str, key: str = global_key):
  val_hash = hashlib.sha256(value.encode()).digest()
  sign_val = hmac.new(key.encode(), val_hash, hashlib.sha256).digest()
  return sign_val.hex()
