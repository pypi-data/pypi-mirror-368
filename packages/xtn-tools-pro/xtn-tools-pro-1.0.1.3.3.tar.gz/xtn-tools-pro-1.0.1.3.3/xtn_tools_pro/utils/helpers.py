#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    杂七杂八
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2024/5/13    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import re
import uuid
import math
import json
import random
from uuid import UUID
from pprint import pformat
from datetime import datetime
from urllib.parse import urlencode


def get_uuid(version=4, namespace: UUID = uuid.NAMESPACE_DNS, name=""):
    """
        生成uuid
    :param version:版本号
        1:基于当前时间和 MAC 地址生成版本 1 的 UUID，具有唯一性，但可能存在一定的安全风险。
        3:基于名称和命名空间的方式生成。它通过将名称和命名空间的标识符组合起来进行哈希计算，生成一个唯一的标识符。UUID 版本 3 使用的哈希算法是 MD5。
        4:使用随机数生成版本 4 的 UUID，具有足够的随机性和唯一性。
        5:使用基于命名空间和名称生成版本 5 的 UUID，可以使用自定义的命名空间和名称。
    :param namespace:命名空间 uuid.NAMESPACE_DNS、uuid.NAMESPACE_URL、uuid.NAMESPACE_OID、uuid.NAMESPACE_X500
    :param name:名称 自定义
    :return:
    """
    if version == 1:
        result = uuid.uuid1()
    elif version == 3:
        result = uuid.uuid3(namespace, name)
    elif version == 5:
        result = uuid.uuid5(namespace, name)
    else:
        result = uuid.uuid4()

    # uuid_str = str(result)
    # uuid_hex = uuid_obj.hex
    # uuid_int = uuid_obj.int
    # uuid_bytes = uuid_obj.bytes
    return result


def get_str_to_json(str_json):
    """
        字符串类型的json格式 转 json
    :param str_json: 字符串json
    :return:
    """
    try:
        new_str_json = str_json.replace("'", '"'). \
            replace("None", "null").replace("True", "true"). \
            replace("False", "false")
        return json.loads(new_str_json)
    except Exception as e:
        return {}


def list_to_strtuple(datas):
    """
        列表转字符串元组
    :param datas: datas: [1, 2]
    :return: (1, 2) 字符串类型
    """
    data_str = str(tuple(datas))
    data_str = re.sub(",\)$", ")", data_str)
    return data_str


def dumps_json(data, indent=4, sort_keys=False):
    """
        将JSON数据格式化为可打印的字符串
    :param data:
    :param indent: 每一级嵌套都使用4个空格进行缩进
    :param sort_keys: 是否排序
    :return:
    """
    try:
        if isinstance(data, str):
            data = get_str_to_json(data)

        data = json.dumps(
            data,
            ensure_ascii=False,
            indent=indent,
            skipkeys=True,
            sort_keys=sort_keys,
            default=str,
        )

    except Exception as e:
        data = pformat(data)

    return data


def get_calculate_total_page(total, limit):
    """
        根据total和limit计算出一共有多少页
    :param total:
    :param limit:
    :return:
    """
    if limit <= 0:
        return 0
    # 根据总条数和limit计算总页数
    total_pages = math.ceil(total / limit)
    return total_pages


def get_build_url_with_params(url, params):
    """
        传入url和params拼接完整的url ->效果 https://wwww.xxxx.com/?xxx1=1&xxx2=2
    :param url:
    :param params:
    :return:
    """
    encoded_params = urlencode(params)
    full_url = url + "?" + encoded_params
    return full_url


def get_orderId_random(prefix="", suffix=""):
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







if __name__ == '__main__':
    # print(get_uuid(4))
    from faker import Faker

    print(get_orderId_random())
