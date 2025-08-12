#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    随机生成
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2025/8/12    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import random
from datetime import datetime


def g_random_port(s=49152, e=65535):
    """
        随机生成端口
    :param s:范围开始(包含)
    :param e:范围结束(包含)
    :return:
    """
    num = random.randint(s, e)
    return num


def g_random_orderId(prefix="", suffix=""):
    """
        随机生成20位订单号，前部分由年月日时分秒组成
    :param prefix: 自定义前缀
    :param suffix: 自定义后缀
    :return:
    """
    current_time = datetime.now()
    date_time_str = current_time.strftime("%y%m%d%H%M%S")
    # 生成随机部分
    random_number = ''.join(random.choices('0123456789', k=8))
    # 组合成完整的数字
    combined_number = int(date_time_str + random_number)
    return f"{prefix}{combined_number}{suffix}"
