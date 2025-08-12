#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    时间相关的工具
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2024/4/18    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import time, datetime


def get_time_now_timestamp(is_time_10=False, is_time_13=False):
    """
        获取当前时间戳
    :param is_time_10: 是否需要处理为10位的时间戳，默认不处理
    :param is_time_13: 是否需要处理为13位的时间戳，默认不处理
    :return:
    """

    if is_time_10:
        val = int(time.time())
    elif is_time_13:
        val = int(time.time() * 1000)
    else:
        val = time.time()
    return val


def get_time_now_day0_timestamp(is_time_13=False):
    """
        获取当天0点时间戳
    :param is_time_13: 是否需要处理为13位的时间戳，默认不处理并且返回10位时间戳
    :return:
    """
    val = time.mktime(datetime.date.today().timetuple())
    if is_time_13:
        return int(val * 1000)
    else:
        return int(val)


def get_time_now_day59_timestamp(is_time_13=False):
    """
        获取当天23:59:59点时间戳
    :param is_time_13: 是否需要处理为13位的时间戳，默认不处理并且返回10位时间戳
    :return:
    """
    # 获取当前日期时间
    now = datetime.datetime.now()
    # 设置小时、分钟、秒为 23:59:59
    last_second = now.replace(hour=23, minute=59, second=59)
    # 转换为时间戳
    timestamp = time.mktime(last_second.timetuple())
    # 转换为整数类型
    if is_time_13:
        return get_time_10_to_13_timestamp(timestamp)
    else:
        return int(timestamp)


def get_time_x_day_timestamp(x, is_time_13=False):
    """
        获取x天的0点的时间戳
    :param x: 0:当天; 1:1天后; -1:一天前
    :param is_time_13: 是否需要处理为13位的时间戳，默认不处理并且返回10位时间戳
    :return:
    """
    if x == 0:
        date_string = datetime.datetime.now().strftime("%Y-%m-%d")  # 当天日期
    elif x > 0:
        future_date = datetime.datetime.now() + datetime.timedelta(days=x)
        date_string = future_date.strftime("%Y-%m-%d")  # x天后的日期
    else:
        past_date = datetime.datetime.now() - datetime.timedelta(days=abs(x))
        date_string = past_date.strftime("%Y-%m-%d")  # x天前的日期

    timestamp = get_time_datestr_to_timestamp(date_string=date_string, is_time_13=is_time_13)
    return timestamp


def get_time_datestr_to_timestamp(date_string, date_format="%Y-%m-%d", is_time_13=False):
    """
        根据日期格式转换为时间戳，date_string和date_format需要配合，自行传参修改，这里是以%Y-%m-%d为格式也就是2024-04-18
    :param date_string: 字符串类型的日期格式 例如：2024-04-18
    :param date_format: 时间格式
    :param is_time_13: 是否需要处理为13位的时间戳，默认不处理并且返回10位时间戳
    :return:
    """
    date_obj = datetime.datetime.strptime(date_string, date_format)
    timestamp = date_obj.timestamp()
    if is_time_13:
        return get_time_10_to_13_timestamp(timestamp)
    else:
        return int(timestamp)


def get_time_10_to_13_timestamp(timestamp):
    """
        10位时间戳转13位时间戳
    :param timestamp:
    :return:
    """
    val = int(timestamp)
    if len(str(val)) == 10:
        return int(val * 1000)
    return val


def get_time_13_to_10_timestamp(timestamp):
    """
        13位时间戳转10位时间戳
    :param timestamp:
    :return:
    """
    val = int(timestamp)
    if len(str(val)) == 13:
        return int(val // 1000)
    return val


def get_time_timestamp_to_datestr(format='%Y-%m-%d %H:%M:%S', now_time=0):
    """
        根据时间戳转换为日期格式，兼容10位时间戳和13位时间戳
    :param format: 日期格式，常用：%Y-%m-%d %H:%M:%S、%Y-%m-%d、%Y/%m/%d、%H:%M:%S ...
    :param now_time: 时间戳，默认0表示当前时间戳
    :return:
    """
    # 根据格式获取当前转换好的时间
    if not now_time:
        now_time = get_time_now_timestamp()
    now_time = get_time_13_to_10_timestamp(now_time)
    val = time.strftime(format, time.localtime(now_time))
    return val


if __name__ == '__main__':
    pass
    print(get_time_timestamp_to_datestr())
    print(get_time_timestamp_to_datestr(format="%H:%M:%S", now_time=get_time_now_timestamp(is_time_10=True)))
    print(get_time_timestamp_to_datestr(now_time=get_time_now_timestamp(is_time_13=True)))
