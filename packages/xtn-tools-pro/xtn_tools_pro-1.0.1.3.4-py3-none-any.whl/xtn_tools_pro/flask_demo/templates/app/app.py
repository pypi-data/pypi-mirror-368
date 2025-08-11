#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask as _Flask
from app.libs.error_code import ServerError500
from flask.json import JSONEncoder as _JSONEncoder


class JSONEncoder(_JSONEncoder):
    # 改写 flask的JSONEncoder
    def default(self, o):
        if hasattr(o, 'keys') and hasattr(o, '__getitem__'):
            return dict(o)
        raise ServerError500()


class Flask(_Flask):
    # json_encoder = JSONEncoder
    pass
