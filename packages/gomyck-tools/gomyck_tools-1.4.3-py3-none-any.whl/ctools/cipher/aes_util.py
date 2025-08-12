from cryptography.fernet import Fernet


def generate_key():
  """
  生成 AES key
  Returns 32 bytes key
  -------
  """
  key = Fernet.generate_key()
  return key.decode()


def aes_encrypt(sec_key, plaintext):
  """
  aes加密
  :param sec_key: 加密 key
  :param plaintext: 明文信息
  :return: 加密后的信息
  """
  cipher = Fernet(sec_key)
  ciphertext = cipher.encrypt(plaintext.encode())
  return ciphertext.decode()


def aes_decrypt(sec_key, ciphertext):
  """
  aes解密
  :param sec_key: 加密 key
  :param ciphertext: 密文
  :return: 解密后的明文信息
  """
  cipher = Fernet(sec_key)
  decrypted_data = cipher.decrypt(ciphertext)
  return decrypted_data.decode()
