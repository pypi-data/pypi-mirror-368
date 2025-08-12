import base64

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from ctools import cjson, path_info

ENCRYPT_CHUNK_SIZE = 245
decrypt_CHUNK_SIZE = 512


def generate_rsa_keypair(bits=2048):
  key = RSA.generate(bits)
  private_key = key.export_key()  # 导出私钥
  public_key = key.publickey().export_key()  # 导出公钥
  with open("private_key.pem", "wb") as f:
    f.write(private_key)
  with open("public_key.pem", "wb") as f:
    f.write(public_key)


def loadLicenseInfo(auth_code):
  with open(path_info.get_app_path() + '/keys/license.key', 'r') as pri:
    decrypt_message = decrypt(auth_code.strip(), pri.read())
    return cjson.loads(decrypt_message)


# 加密函数
def encrypt(msg, public_key):
  parts = b''
  public_key = RSA.import_key(public_key)
  cipher = PKCS1_OAEP.new(public_key)
  for i in range(0, len(msg), ENCRYPT_CHUNK_SIZE):
    parts += cipher.encrypt(msg[i:i + ENCRYPT_CHUNK_SIZE].encode())
  encrypted_base64 = base64.b64encode(parts)
  return encrypted_base64.decode()


# 解密函数
def decrypt(msg, private_key):
  parts = b''
  public_key = RSA.import_key(private_key)
  cipher = PKCS1_OAEP.new(public_key)
  encrypted_bytes = base64.b64decode(msg)
  for i in range(0, len(encrypted_bytes), decrypt_CHUNK_SIZE):
    parts += cipher.decrypt(encrypted_bytes[i:i + decrypt_CHUNK_SIZE])
  return parts.decode()


# 验签
def verify_sign(msg, public_key, sign):
  public_key = RSA.import_key(public_key)
  hash_message = SHA256.new(msg.encode())
  try:
    pkcs1_15.new(public_key).verify(hash_message, base64.b64decode(sign.encode()))
    return True
  except Exception as e:
    print('签名验证失败: {}'.format(e))
    return False


# 签名
def sign_msg(msg, private_key):
  private_key = RSA.import_key(private_key)
  hash_message = SHA256.new(msg.encode())
  signature = pkcs1_15.new(private_key).sign(hash_message)
  return base64.b64encode(signature).decode()

# with open(work_path.get_current_path() + '/private_key.pem', 'r') as key:
#   key = key.read()
#   sign = sign_msg(key, key)
#   with open(work_path.get_current_path() + '/public_key.pem', 'r') as pub:
#     print(verify_sign(key, pub.read(), sign+'123'))
