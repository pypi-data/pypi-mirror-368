import base64

from gmssl import sm2
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT

sm2_crypt: sm2.CryptSM2 = None


def init(private_key: str, public_key: str):
  global sm2_crypt
  if sm2_crypt is not None:
    print('sm2 is already init!!!')
    return
  sm2_crypt = sm2.CryptSM2(private_key=private_key, public_key=public_key, asn1=True, mode=1)


def sign_with_sm2(sign_data: str) -> str:
  if sm2_crypt is None: raise Exception('sm2 is not init!!!')
  return sm2_crypt.sign_with_sm3(sign_data.encode('UTF-8'))


def verify_with_sm2(sign_val: str, sign_data: str) -> bool:
  if sm2_crypt is None: raise Exception('sm2 is not init!!!')
  try:
    return sm2_crypt.verify_with_sm3(sign_val, sign_data.encode('UTF-8'))
  except Exception as e:
    print('签名验证失败: {}'.format(e))
    return False


def encrypt_with_sm2(encrypt_data: str) -> str:
  if sm2_crypt is None: raise Exception('sm2 is not init!!!')
  return base64.b64encode(sm2_crypt.encrypt(encrypt_data.encode('UTF-8'))).decode('UTF-8')


def decrypt_with_sm2(encrypt_data: str) -> str:
  if sm2_crypt is None: raise Exception('sm2 is not init!!!')
  return sm2_crypt.decrypt(base64.b64decode(encrypt_data.encode('UTF-8'))).decode('UTF-8')


def encrypt_with_sm4(key: bytes, encrypt_text: str):
  crypt_sm4 = CryptSM4()
  crypt_sm4.set_key(key, SM4_ENCRYPT)
  encrypt_value = base64.b64encode(crypt_sm4.crypt_ecb(encrypt_text.encode()))
  return encrypt_value.decode()


def decrypt_with_sm4(key: bytes, decrypt_text: str):
  crypt_sm4 = CryptSM4()
  crypt_sm4.set_key(key, SM4_DECRYPT)
  decrypt_value = crypt_sm4.crypt_ecb(base64.b64decode(decrypt_text))
  return decrypt_value.decode()
