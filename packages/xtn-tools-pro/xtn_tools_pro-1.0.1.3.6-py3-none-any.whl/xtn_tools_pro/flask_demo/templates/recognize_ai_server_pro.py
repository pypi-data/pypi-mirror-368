#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app
from app.libs.error import APIException
from werkzeug.exceptions import HTTPException
from app.libs.error_code import ServerError500, MethodException

app = create_app()


@app.errorhandler(Exception)
def framework_error(e):
    print("发生错误啦 => ", e)
    if isinstance(e, APIException):
        return e
    elif isinstance(e, HTTPException):
        if e.code == 405:
            # 请求的URL不允许使用该方法
            return MethodException()
        else:
            code = e.code
            msg = e.description
            error_code = 4999
            return APIException(msg + "HTTP Exception 4999", code, error_code)
    else:
        print(e)
        return ServerError500()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10089, debug=True)

