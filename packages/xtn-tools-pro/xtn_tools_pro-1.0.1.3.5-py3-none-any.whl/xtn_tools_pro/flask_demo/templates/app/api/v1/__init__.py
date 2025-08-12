#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint
from app.api.v1 import demo


def create_blueprint_v1():
    # 将自己定义的红图注册到蓝图上
    bp_v1 = Blueprint("v1", __name__)
    ios.api.register(bp_v1)

    return bp_v1
