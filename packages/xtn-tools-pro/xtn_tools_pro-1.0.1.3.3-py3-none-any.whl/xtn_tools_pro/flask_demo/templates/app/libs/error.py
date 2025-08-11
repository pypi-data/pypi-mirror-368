#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request, json
from werkzeug.exceptions import HTTPException
from xtn_tools_pro.utils.time_utils import get_time_now_timestamp

class APIException(HTTPException):
    code = 500
    msg = 'sorry, we made a mistake'
    error_code = 5000
    data = {}
    data_type = "dict"

    def __init__(self, msg=None, code=None, error_code=None, headers=None, data=None, data_type=None):
        if code:
            self.code = code
        if error_code:
            self.error_code = error_code
        if msg:
            self.msg = msg
        if data:
            self.data = data
        if data_type == "list" and not data:
            self.data = []
        super(APIException, self).__init__(msg, None)

    def get_body(self, environ=None, scope=None):
        # 重写 父类的get_body
        body = dict(
            msg=self.msg,
            error_code=self.error_code,
            code=self.code,
            request=request.method + ' ' + self.get_url_no_param(),
            data=self.data,
            timestamp=get_time_now_timestamp(is_time_13=True)
        )
        text = json.dumps(body)
        return text

    def get_headers(self, environ=None, scope=None):
        """Get a list of headers."""
        return [('Content-Type', 'application/json')]

    @staticmethod
    def get_url_no_param():
        full_path = str(request.full_path)
        main_path = full_path.split('?')
        return main_path[0]
