#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    文件相关的工具
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2024/4/19    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import os, re


def get_file_extension(file_name):
    """
        根据文件名获取文件扩展名/后缀名
    :param file_name: 文件名称
    :return:
    """
    _, file_extension = os.path.splitext(file_name)
    return file_extension


def get_file_check_filename(file_name):
    """
        传入文件名返回一个合法的文件名 会替换掉一些特殊符号 常用于爬虫写文件时文件名中带有特殊符号的情况...
    :param filename: 文件名
    :return:
    """
    file_extension = get_file_extension(file_name)
    # 删除非法字符
    sanitized_filename = re.sub(r'[\/:*?"<>|]', '', file_name)
    max_length = 255  # 操作系统限制文件名的最大长度为255个
    sanitized_filename = sanitized_filename[:max_length]
    return sanitized_filename


if __name__ == '__main__':
    pass
    print(get_file_extension('file/2024-04-19/BOSCH GEX 125-1A/125-1AE砂磨机操作说明书:[1]_jingyan.txt'))
    print(get_file_check_filename('file/2024-04-19/BOSCH GEX 125-1A/125-1AE砂磨机操作说明书:[1]_jingyan.txt'))
