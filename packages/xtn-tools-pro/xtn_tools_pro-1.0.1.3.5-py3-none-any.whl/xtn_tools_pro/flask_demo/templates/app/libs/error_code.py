#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app.libs.error import APIException


class ServerError500(APIException):
    code = 500
    error_code = 5000
    msg = 'sorry, we made a mistake (*￣︶￣)!'


class Success200(APIException):
    # 成功
    code = 200
    error_code = 2000
    msg = "成功"


class NotFound400(APIException):
    code = 400
    error_code = 4000
    msg = '资源未找到'


class ParameterException(NotFound400):
    msg = '无效的参数'
    error_code = 4001


class MethodException(NotFound400):
    msg = '请求的URL不允许使用该方法'
    error_code = 4002


class TokenException(NotFound400):
    msg = 'token认证不通过'
    error_code = 4003


class Error600(APIException):
    code = 600
    error_code = 6000
    msg = '未知错误'




