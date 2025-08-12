#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import random
from wtforms import Form
from flask import request
from app.libs.error_code import ValidatorsErrorException


class BaseForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', data=None, meta=None, **kwargs):
        # 合并请求中的数据
        request_data = request.get_json(silent=True) or {}
        values = request.values.to_dict()
        args = request.args.to_dict()
        file_args = request.files.to_dict()

        combined_data = {}
        combined_data.update(self.validate_data_type(request_data))
        combined_data.update(self.validate_data_type(values))
        combined_data.update(self.validate_data_type(args))
        combined_data.update(self.validate_data_type(file_args))

        # 合并传入的 data 参数（如果有）
        if data is not None:
            combined_data.update(data)

        # 调用父类构造函数，传递所有参数
        super(BaseForm, self).__init__(
            formdata=formdata,
            obj=obj,
            prefix=prefix,
            data=combined_data,
            meta=meta,
            **kwargs
        )

    def validate_for_api(self):
        valid = super(BaseForm, self).validate()
        if not valid:
            # 只返回一个错误
            error_msg = ""
            for error_k, error_v in self.errors.items():
                # print(error_k, error_v)
                if not error_v: continue
                error_v_item = error_v[0]
                if not error_v_item: continue
                if type(error_v_item) == str:
                    error_msg = error_v_item
                    break
                if type(error_v_item) == dict:
                    first_key = next(iter(error_v_item))
                    first_value = error_v_item[first_key]
                    if not first_value: continue
                    error_msg = first_value[0]
                    break

            raise ValidatorsErrorException(msg=error_msg)

        return self

    def validate_data_type(self, data):
        if type(data) == str:
            data = json.loads(data)
        return data
