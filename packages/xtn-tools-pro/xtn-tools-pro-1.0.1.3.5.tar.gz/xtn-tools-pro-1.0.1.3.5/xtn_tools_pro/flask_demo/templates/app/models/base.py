#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_pymongo import PyMongo
from flask_redis import FlaskRedis


def get_init_log():
    from xtn_tools_pro.utils.log import Log
    logger = Log('{{ project_name }}', './xxx.log', log_level='DEBUG', is_write_to_console=True,
                 is_write_to_file=True,
                 color=True, mode='a', save_time_log_path='./logs')
    return logger


redis_db_01 = FlaskRedis(decode_responses=True, config_prefix="REDIS_01")  # decode_responses=True：连接redis存的数据是字符串格式
redis_db_02 = FlaskRedis(decode_responses=True, config_prefix="REDIS_02")  # decode_responses=True：连接redis存的数据是字符串格式
mongo_db_01 = PyMongo()
logger = get_init_log()
