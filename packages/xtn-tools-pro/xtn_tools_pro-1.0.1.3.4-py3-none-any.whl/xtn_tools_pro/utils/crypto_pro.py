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
import time
import json
import pyotp
import base64
import hashlib
import secrets
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


class XtnDeEnAir:
    BLOCK_SIZE = AES.block_size

    @staticmethod
    def encrypt_dict(key: bytes, raw: dict) -> str:
        """
            加密
        """
        cipher = AES.new(key, AES.MODE_ECB)
        raw["time"] = int(time.time())
        raw_s = json.dumps(raw)
        padded_data = pad(raw_s.encode('utf-8'), XtnDeEnAir.BLOCK_SIZE)
        enc = cipher.encrypt(padded_data)
        result = base64.b64encode(enc).decode('utf-8')
        return result

    @staticmethod
    def decrypt_dict(key: bytes, raw: str) -> dict:
        """
            解密
        """
        try:
            cipher = AES.new(key, AES.MODE_ECB)
            enc = base64.b64decode(raw)
            decrypted = cipher.decrypt(enc)
            result = unpad(decrypted, XtnDeEnAir.BLOCK_SIZE).decode('utf-8')
            return json.loads(result)
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            # raise ValueError(f"解密失败: {e}")
            return {}


class XtnDeEnPro:
    BLOCK_SIZE = AES.block_size

    @staticmethod
    def encrypt_dict(key: bytes, raw: dict) -> str:
        """
            加密
        """
        raw["encrypt_time"] = int(time.time())
        raw_json = json.dumps(data).encode('utf-8')
        padded_data = pad(raw_json, XtnDeEnPro.BLOCK_SIZE)
        iv = get_random_bytes(XtnDeEnPro.BLOCK_SIZE)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(padded_data)
        combined = iv + encrypted
        result = base64.b64encode(combined).decode('utf-8')
        # result = combined.hex() # hex
        return result

    @staticmethod
    def decrypt_dict(key: bytes, raw: str) -> dict:
        """
            解密
        """
        try:
            combined = base64.b64decode(raw)
            # combined = bytes.fromhex("") # hex
            iv = combined[:XtnDeEnPro.BLOCK_SIZE]
            encrypted = combined[XtnDeEnPro.BLOCK_SIZE:]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(encrypted), XtnDeEnPro.BLOCK_SIZE)
            result = decrypted.decode('utf-8')
            return json.loads(result)
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            # raise ValueError(f"解密失败: {e}")
            return {}


class XtnDeEnProMax:
    BLOCK_SIZE = AES.block_size

    @staticmethod
    def encrypt_dict(key: bytes, raw: dict) -> str:
        """
            加密
        """
        session_key = get_random_bytes(16)

        rsa_key = RSA.import_key(key)
        rsa_cipher = PKCS1_OAEP.new(rsa_key)
        encrypted_session_key = rsa_cipher.encrypt(session_key)

        iv = get_random_bytes(16)
        aes_cipher = AES.new(session_key, AES.MODE_CBC, iv)
        raw["encrypt_time"] = int(time.time())
        raw_data = json.dumps(raw).encode('utf-8')
        encrypted_data = aes_cipher.encrypt(pad(raw_data, XtnDeEnProMax.BLOCK_SIZE))

        combined = (
                len(encrypted_session_key).to_bytes(2, 'big') +
                encrypted_session_key +
                iv +
                encrypted_data
        )

        result_base64 = base64.b64encode(combined).decode()
        # result_hex = combined.hex()  # hex
        return result_base64

    @staticmethod
    def decrypt_dict(key: bytes, raw: str) -> dict:
        """
            解密
        """
        try:
            combined = base64.b64decode(raw)
            key_len = int.from_bytes(combined[:2], 'big')
            encrypted_session_key = combined[2:2 + key_len]
            iv = combined[2 + key_len:2 + key_len + 16]
            encrypted_data = combined[2 + key_len + 16:]

            rsa_key = RSA.import_key(key)
            rsa_cipher = PKCS1_OAEP.new(rsa_key)
            session_key = rsa_cipher.decrypt(encrypted_session_key)

            aes_cipher = AES.new(session_key, AES.MODE_CBC, iv)
            decrypted = unpad(aes_cipher.decrypt(encrypted_data), XtnDeEnProMax.BLOCK_SIZE)
            result = decrypted.decode('utf-8')
            return json.loads(result)
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            # raise ValueError(f"解密失败: {e}")
            return {}


if __name__ == '__main__':
    key = b"d9fe4b29dc7decc8360e72e7dd15a5c8"
    data = {
        "task_type": "update_name",
        "task_client": "tiktok",
    }
    sss = XtnDeEnAir.encrypt_dict(key, data)
    print(sss)
    print(XtnDeEnAir.decrypt_dict(key, sss))

    # key_pair = RSA.generate(2048)
    # private_key = key_pair.export_key()
    # public_key = key_pair.publickey().export_key()
    # print(private_key)
    # print(public_key)
    # sss = XtnDeEnProMax.encrypt_dict(public_key, data)
    # print(sss)
    # print(XtnDeEnProMax.decrypt_dict(private_key, sss))
