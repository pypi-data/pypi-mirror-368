#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    加解密、编解码
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2024/5/13    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import jwt
import pyotp
import base64
import hashlib
import secrets
from Crypto.Cipher import AES


def get_md5_32(s: str, is_upper=False):
    """
        获取文本的md5值 32位
    :param s: 文本
    :param is_upper: 是否转大写 默认False
    :return:
    """
    # s.encode()#变成bytes类型才能加密
    m = hashlib.md5(s.encode())  # 长度是32
    if is_upper:
        return m.hexdigest().upper()
    return m.hexdigest()


def get_md5_16(s: str, is_upper=False):
    """
        获取文本的md5值 16位
    :param s: 文本
    :param is_upper: 是否转大写 默认False
    :return:
    """
    result = get_md5_32(s, is_upper)
    return result[8:24]


def get_binary_content_md5_32(content, is_upper=False):
    """
        二进制内容md5 例如图片
    :param content: 二进制内容
    :param is_upper: 是否转大写 默认False
    :return:
    """
    md5_hash = hashlib.md5(content)
    md5_hexdigest = md5_hash.hexdigest()
    if is_upper:
        return md5_hexdigest.upper()
    return md5_hexdigest


def get_binary_content_md5_16(content, is_upper=False):
    """
        二进制内容md5 例如图片
    :param content: 二进制内容
    :param is_upper: 是否转大写 默认False
    :return:
    """
    result = get_binary_content_md5_32(content, is_upper)
    return result[8:24]


def get_file_md5_32(file_path, is_upper=False):
    """
        获取文件md5值
    :param file_path: 文件路径
    :param is_upper: 是否转大写 默认False
    :return:
    """
    with open(file_path, 'rb') as file:
        data = file.read()
        md5_hash = hashlib.md5(data).hexdigest()
    if is_upper:
        return md5_hash.upper()
    return md5_hash


def get_file_md5_16(file_path, is_upper=False):
    """
        获取文件md5值
    :param file_path: 文件路径
    :param is_upper: 是否转大写 默认False
    :return:
    """
    result = get_file_md5_32(file_path, is_upper)
    return result[8:24]


def get_sha1(s: str, is_upper=False):
    """
        sha1
    :param s: 文本
    :param is_upper: 是否转大写 默认False
    :return:
    """
    # 使用sha1算法进行哈希
    sha1_hash = hashlib.sha1(s.encode()).hexdigest()
    if is_upper:
        return sha1_hash.upper()
    return sha1_hash


def get_base64_encode(s: str):
    """
        base64 编码
    :param s: 文本
    :return:
    """
    # 将字符串编码为 bytes
    data_bytes = s.encode('utf-8')
    # 使用 base64 进行编码
    encoded_bytes = base64.b64encode(data_bytes)
    # 将编码后的 bytes 转换为字符串
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string


def generate_bearer_token(secret_key, expiration=0, algorithm='HS256', **kwargs):
    """
    生成 Bearer Token
    :param secret_key: 用于加密的密钥
    :param expiration: 过期时间戳,0则表示不过期
    :param algorithm: 使用的加密算法（默认是 HS256）HS256、HS384、HS512
    :param kwargs: 其他自定义的 Token 数据
    :return: 生成的 Bearer Token
    """
    payload = {
        **kwargs  # 将其他参数添加到 payload
    }
    if expiration:
        payload['exp'] = expiration

    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


def generate_secret_key(length=32):
    """
    生成一个随机的 secret key
    :param length: key 的长度，默认为 32
    :return: 生成的 secret key
    """
    return secrets.token_hex(length)


def img_bytes_to_str(img_data: bytes):
    """
        图片数据 bytes_to_str
    :param img_data:
    :return:
    """
    return img_data.decode('latin1')


def img_str_to_bytes(img_data: str):
    """
        图片数据 str_to_bytes
    :param img_data:
    :return:
    """
    return img_data.encode('latin1')


def get_2FA(secret, interval=30):
    """
        计算 2FA
    :param secret:
    :param interval:有效期 单位秒
    :return:
    """
    base32_secret = base64.b32encode(secret.encode()).decode()
    totp = pyotp.TOTP(base32_secret, interval=interval)
    return str(totp.now())


class A8:
    def __init__(self, AES_key):
        self.__AES_cipher = AES.new(AES_key, AES.MODE_ECB)

    def data_en_pro(self, raw):
        enc = self.__AES_cipher.encrypt(raw.encode('utf-8'))
        result = base64.b64encode(enc).decode('utf-8')
        return result

    def data_de_pro(self, enc):
        enc = base64.b64decode(enc)
        result = self.__AES_cipher.decrypt(enc).decode('utf-8')
        return result


if __name__ == '__main__':
    print(get_2FA('mzhiahagaghsafsdgfrhfaghfkmzh123456',3600))
