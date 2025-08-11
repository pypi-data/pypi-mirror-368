#!/usr/bin/env python
# -*- coding: utf-8 -*-
import jwt
from flask import current_app, g
from app.models.base import logger
from app.models.user import UserDB
from flask_httpauth import HTTPBasicAuth
from app.libs.error_code import TokenException

user_auth = HTTPBasicAuth()


@user_auth.verify_password
def user_verify_password(token, password):
    user_info = verify_user_auth_token(token)
    # print(user_info)
    if not user_info:
        # token验证不通过
        raise TokenException()
    # token验证通过
    g.user = user_info
    return True


def verify_user_auth_token(token):
    secret_key = current_app.config['SECRET_KEY']
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        # print("payload",payload)
        if not payload:
            logger.critical(f"验证身份失败")
            return
        logger.debug(f"验证身份成功,{payload},{token}")
        return payload
    except Exception as e:
        logger.critical(f"验证身份失败,{e}")
    return
