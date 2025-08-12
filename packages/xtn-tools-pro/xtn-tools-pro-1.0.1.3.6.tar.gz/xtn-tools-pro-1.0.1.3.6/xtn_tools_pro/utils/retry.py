#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    重试
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2024/5/12    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import time
from xtn_tools_pro.utils.log import Log

log = Log(name="retry", color=True)


def retry(max_attempts=3, delay=0, exception_callfunc=None, *args_callfunc, **kwargs_callfunc):
    """
        重试
    :param max_attempts: 最多重试次数
    :param delay: 每次重试间隔时间
    :param exception_callfunc: 失败的回调函数
    :return:
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    log.debug(f"重试第 {attempts + 1} 次,failed: {e}")
                    if exception_callfunc:
                        exception_callfunc(*args_callfunc, **kwargs_callfunc)
                    attempts += 1
                    time.sleep(delay)

        return wrapper

    return decorator


if __name__ == '__main__':

    def test1(*args, **kwargs):
        print("test1", args, kwargs)


    @retry(3, 5)
    def test(a, b):
        import random
        if random.random() < 0.5:
            raise ValueError("Random value too small")
        print("Success!")

    test(1, 1)
