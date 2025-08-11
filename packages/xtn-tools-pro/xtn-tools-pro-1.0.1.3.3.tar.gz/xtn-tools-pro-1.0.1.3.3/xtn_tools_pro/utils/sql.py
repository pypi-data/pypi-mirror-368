#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    sql相关
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2024/5/12    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import datetime
from xtn_tools_pro.utils.helpers import list_to_strtuple, dumps_json


def format_sql_value(value):
    if isinstance(value, str):
        value = value.strip()

    elif isinstance(value, (list, dict)):
        value = dumps_json(value, indent=None)

    elif isinstance(value, (datetime.date, datetime.time)):
        value = str(value)

    elif isinstance(value, bool):
        value = int(value)

    return value


def get_insert_sql(table, data, auto_update=False, update_columns=(), insert_ignore=False):
    """
        生成 insert sql
    :param table: 表
    :param data: 表数据 json格式
    :param auto_update: 使用的是replace into， 为完全覆盖已存在的数据
    :param update_columns: 需要更新的列 默认全部，当指定值时，auto_update设置无效，当duplicate key冲突时更新指定的列
    :param insert_ignore: 数据存在忽略，True则会忽略该插入操作，不会产生冲突错误
    :return:
    """
    keys = ["`{}`".format(key) for key in data.keys()]
    keys = list_to_strtuple(keys).replace("'", "")
    values = [format_sql_value(value) for value in data.values()]
    values = list_to_strtuple(values)
    if update_columns:
        if not isinstance(update_columns, (tuple, list)):
            update_columns = [update_columns]
        update_columns_ = ", ".join(
            ["{key}=values({key})".format(key=key) for key in update_columns]
        )
        sql = (
                "insert%s into `{table}` {keys} values {values} on duplicate key update %s"
                % (" ignore" if insert_ignore else "", update_columns_)
        )

    elif auto_update:
        sql = "replace into `{table}` {keys} values {values}"
    else:
        sql = "insert%s into `{table}` {keys} values {values}" % (
            " ignore" if insert_ignore else ""
        )

    sql = sql.format(table=table, keys=keys, values=values).replace("None", "null")
    return sql

def get_insert_batch_sql(table, datas, auto_update=False, update_columns=(), update_columns_value=()):
    """
        生成 批量 insert sql
    :param table: 表
    :param datas: 表数据 [{...}]
    :param auto_update: 使用的是replace into， 为完全覆盖已存在的数据
    :param update_columns: 需要更新的列 默认全部，当指定值时，auto_update设置无效，当duplicate key冲突时更新指定的列
    :param update_columns_value: 需要更新的列的值 默认为datas里边对应的值, 注意 如果值为字符串类型 需要主动加单引号， 如 update_columns_value=("'test'",)
    :return:
    """
    if not datas:
        return
    keys = list(set([key for data in datas for key in data]))
    values_placeholder = ["%s"] * len(keys)

    values = []
    for data in datas:
        value = []
        for key in keys:
            current_data = data.get(key)
            current_data = format_sql_value(current_data)

            value.append(current_data)

        values.append(value)

    keys = ["`{}`".format(key) for key in keys]
    keys = list_to_strtuple(keys).replace("'", "")

    values_placeholder = list_to_strtuple(values_placeholder).replace("'", "")

    if update_columns:
        if not isinstance(update_columns, (tuple, list)):
            update_columns = [update_columns]
        if update_columns_value:
            update_columns_ = ", ".join(
                [
                    "`{key}`={value}".format(key=key, value=value)
                    for key, value in zip(update_columns, update_columns_value)
                ]
            )
        else:
            update_columns_ = ", ".join(
                ["`{key}`=values(`{key}`)".format(key=key) for key in update_columns]
            )
        sql = "insert into `{table}` {keys} values {values_placeholder} on duplicate key update {update_columns}".format(
            table=table,
            keys=keys,
            values_placeholder=values_placeholder,
            update_columns=update_columns_,
        )
    elif auto_update:
        sql = "replace into `{table}` {keys} values {values_placeholder}".format(
            table=table, keys=keys, values_placeholder=values_placeholder
        )
    else:
        sql = "insert ignore into `{table}` {keys} values {values_placeholder}".format(
            table=table, keys=keys, values_placeholder=values_placeholder
        )

    return sql, values

def get_update_sql(table, data, condition):
    """
        生成更新sql
    :param table: 表
    :param data: 表数据 json格式
    :param condition: where 条件
    :return:
    """
    key_values = []

    for key, value in data.items():
        value = format_sql_value(value)
        if isinstance(value, str):
            key_values.append("`{}`={}".format(key, repr(value)))
        elif value is None:
            key_values.append("`{}`={}".format(key, "null"))
        else:
            key_values.append("`{}`={}".format(key, value))

    key_values = ", ".join(key_values)

    sql = "update `{table}` set {key_values} where {condition}"
    sql = sql.format(table=table, key_values=key_values, condition=condition)
    return sql

if __name__ == '__main__':
    print(get_insert_sql("user_copy1", {"id": 5, "nickname": "1212", "email": "121212", "auth": 2},insert_ignore=True))
    print(get_insert_batch_sql("user_copy1", [{"id": 5, "nickname": "555", "email": "555", "auth": 1},
                                              {"id": 6, "nickname": "666", "email": "666", "auth": 2},
                                              {"id": 7, "nickname": "777", "email": "777", "auth": 1}],
                               ))
    print(get_update_sql("user_copy1",{"email":"123","status":4},"id=2"))