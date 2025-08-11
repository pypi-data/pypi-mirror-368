#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .app import Flask, JSONEncoder


def register_blueprint(app):
    # 注册蓝图
    from app.api.v1 import create_blueprint_v1
    # url_prefix 前缀
    app.register_blueprint(create_blueprint_v1(), url_prefix="/v1")


def register_mongodb(app):
    return
    from app.models.base import mongo_db_01
    mongo_db_01.init_app(app, uri=app.config['MONGO_URI_01'])


def register_redisdb(app):
    return
    from app.models.base import redis_db_01,redis_db_02
    redis_db.init_app(app)


def create_app():
    app = Flask(__name__)
    app.json_encoder = JSONEncoder
    app.config.from_object('app.config.secure')
    app.config.from_object('app.config.setting')

    # 注册蓝图
    register_blueprint(app)
    # 注册 mongodb
    register_mongodb(app)
    # 注册 redis
    register_redisdb(app)
    return app
