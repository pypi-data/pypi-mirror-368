#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    日志
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2024/5/12     xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import os
import sys
import inspect
import logging
from logging.handlers import BaseRotatingHandler
from xtn_tools_pro.utils.file_utils import mkdirs_dir
from xtn_tools_pro.utils.time_utils import get_time_timestamp_to_datestr


class RotatingFileHandler(BaseRotatingHandler):
    def __init__(
            self, filename, mode="a", max_bytes=0, backup_count=0, encoding=None, delay=0
    ):
        BaseRotatingHandler.__init__(self, filename, mode, encoding, delay)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.placeholder = str(len(str(backup_count)))

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backup_count > 0:
            for i in range(self.backup_count - 1, 0, -1):
                sfn = ("%0" + self.placeholder + "d.") % i  # '%2d.'%i -> 02
                sfn = sfn.join(self.baseFilename.split("."))
                # sfn = "%d_%s" % (i, self.baseFilename)
                # dfn = "%d_%s" % (i + 1, self.baseFilename)
                dfn = ("%0" + self.placeholder + "d.") % (i + 1)
                dfn = dfn.join(self.baseFilename.split("."))
                if os.path.exists(sfn):
                    # print "%s -> %s" % (sfn, dfn)
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = (("%0" + self.placeholder + "d.") % 1).join(
                self.baseFilename.split(".")
            )
            if os.path.exists(dfn):
                os.remove(dfn)
            # Issue 18940: A file may not have been created if delay is True.
            if os.path.exists(self.baseFilename):
                os.rename(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()

    def shouldRollover(self, record):

        if self.stream is None:  # delay was set...
            self.stream = self._open()
        if self.max_bytes > 0:  # are we rolling over?
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  # due to non-posix-compliant Windows feature
            if self.stream.tell() + len(msg) >= self.max_bytes:
                return 1
        return 0


class BoldFormatter(logging.Formatter):
    def format(self, record):
        result = super().format(record)
        return "\033[1m" + result + "\033[0m"


def get_caller_script_path():
    # 获取调用栈列表
    stack = inspect.stack()
    # 遍历调用栈，找到第一个非本模块的调用者
    for frame_info in stack:
        filename = frame_info.filename
        if filename != __file__:  # 排除日志模块自身的路径
            return os.path.abspath(filename)
    return os.path.abspath(__file__)  # 默认返回当前模块路径（理论上不会执行到这里）


class Log:
    def __init__(self, name, path=None, log_level='DEBUG',
                 is_write_to_console=True,
                 is_write_to_file=False,
                 color=True,
                 mode='a',
                 max_bytes=1024000000,  # 1 * 1024 * 1024 * 1024
                 backup_count=0,
                 encoding="utf-8",
                 save_time_log_path=None):
        """
        :param name: log名
        :param path: log文件存储路径 如 D://xxx.log
        :param log_level: log等级 CRITICAL/ERROR/WARNING/INFO/DEBUG
        :param is_write_to_console: 是否输出到控制台
        :param is_write_to_file: 是否写入到文件 默认否
        :param color: 是否有颜色
        :param mode: 写文件模式
        :param max_bytes: 每个日志文件的最大字节数
        :param backup_count: 日志文件保留数量
        :param encoding: 日志文件编码
        :param save_time_log_path: 保存时间日志的路径 './logs'

        """
        # 创建logger对象
        self.logger = logging.getLogger(name)
        # 设置日志等级
        self.logger.setLevel(log_level.upper())
        self.save_time_log_path = save_time_log_path
        if save_time_log_path:
            # 获取调用文件的所在文件夹路径
            run_py_path = os.path.dirname(get_caller_script_path())
            # 记录当前的日期，用于之后检查日期是否已经改变
            self.current_date = get_time_timestamp_to_datestr(format="%Y_%m_%d")
            # 记录日志文件的路径模板，用于之后创建新的日志文件
            self.path_template = f"{path}/logs/{{date}}/{name}.log"
            path = self.path_template.format(date=self.current_date)
            # print(path)
            if is_write_to_file:
                mkdirs_dir_log_dirname = os.path.join(run_py_path, os.path.dirname(path))
                self.mkdirs_dir_log_path = os.path.join(run_py_path, path)
                # print(mkdirs_dir_log_dirname)
                # print(mkdirs_dir_log_path)
                mkdirs_dir(self.mkdirs_dir_log_path)

        # 创建日志格式化器
        # formatter = logging.Formatter('[%(now_datestr)s] [%(levelname)s] [%(func_name)s] - %(message)s') # 原
        # formatter = logging.Formatter('\033[1m%(now_datestr)s] [%(levelname)s] [%(func_name)s] - %(message)s\033[0m') #加粗
        formatter = logging.Formatter(
            '[%(now_datestr)s] | %(levelname)-8s | [%(func_name)s] - %(message)s')  # 加粗对齐

        # formatter = BoldFormatter('[%(now_datestr)s] [%(levelname)s] [%(func_name)s] - %(message)s') # 加粗

        # 判断是否要输出到控制台
        if is_write_to_console:
            # 创建控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            # 设置控制台处理器的格式化器
            console_handler.setFormatter(formatter)
            # 将控制台处理器添加到logger中
            self.logger.addHandler(console_handler)

        # 判断是否要写入文件
        if is_write_to_file:
            # 创建文件处理器
            file_handler = RotatingFileHandler(self.mkdirs_dir_log_path, mode=mode, max_bytes=max_bytes,
                                               backup_count=backup_count, encoding=encoding)
            # 设置文件处理器的格式化器
            file_handler.setFormatter(formatter)
            # 将文件处理器添加到logger中
            self.logger.addHandler(file_handler)

        # 判断是否要带颜色
        if color:
            try:
                from colorlog import ColoredFormatter
                # 创建带颜色的日志格式化器
                # color_formatter = ColoredFormatter('%(log_color)s[%(now_datestr)s] [%(levelname)s] [%(func_name)s] - %(message)s') # 原
                # color_formatter = ColoredFormatter('\033[1m%(log_color)s[%(now_datestr)s] [%(levelname)s] [%(func_name)s] - %(message)s\033[0m') # 加粗
                # 创建颜色映射
                log_colors = {
                    'DEBUG': 'bold_blue',
                    'INFO': 'bold_cyan',
                    'WARNING': 'bold_yellow',
                    'ERROR': 'bold_red',
                    'CRITICAL': 'bold_red',
                }
                color_formatter = ColoredFormatter(
                    # '\033[1m%(log_color)s[%(now_datestr)s] | %(levelname)-8s | [%(func_name)s] - %(message)s\033[0m',
                    '%(log_color)s[%(now_datestr)s] | %(levelname)-8s | [%(func_name)s] - %(message)s',
                    # '%(log_color)s[%(now_datestr)s] | %(levelname)-8s | [%(func_name)-20s] | - %(message)s',
                    log_colors=log_colors)  # 加粗对齐
                # 设置控制台处理器的格式化器为带颜色的格式化器
                console_handler.setFormatter(color_formatter)
            except ImportError:
                pass

    def _get_log_file_path(self):
        """获取日志文件的路径，如果日期已经改变就创建一个新的日志文件"""
        if not self.save_time_log_path: return
        date = get_time_timestamp_to_datestr(format="%Y_%m_%d")
        if date != self.current_date:
            # 日期已经改变，更新当前的日期
            self.current_date = date
            # 更新文件处理器的文件路径
            path = self.path_template.format(date=date)
            mkdirs_dir(path)
            for handler in self.logger.handlers:
                if isinstance(handler, RotatingFileHandler):
                    handler.baseFilename = path
                    handler.doRollover()
                    break

    def debug(self, message):
        # 记录DEBUG级别的日志
        self._get_log_file_path()
        self.logger.debug(message, extra=self._get_caller_name_extra())

    def info(self, message):
        # 记录INFO级别的日志
        self._get_log_file_path()
        self.logger.info(message, extra=self._get_caller_name_extra())

    def warning(self, message):
        # 记录WARNING级别的日志
        self._get_log_file_path()
        self.logger.warning(message, extra=self._get_caller_name_extra())

    def error(self, message):
        # 记录ERROR级别的日志
        self._get_log_file_path()
        self.logger.error(message, extra=self._get_caller_name_extra())

    def critical(self, message):
        # 记录CRITICAL级别的日志
        self._get_log_file_path()
        self.logger.critical(message, extra=self._get_caller_name_extra())

    def _get_caller_name_extra(self):
        """
            获取调用日志函数的函数名称
        """
        # 获取当前栈帧
        frame = inspect.currentframe()
        # 获取调用者的栈帧
        caller_frame = frame.f_back.f_back
        # 从栈帧中获取代码对象
        code_obj = caller_frame.f_code
        # 获取调用者的名字
        caller_name = code_obj.co_name
        return {"func_name": caller_name,
                "now_datestr": get_time_timestamp_to_datestr()}


if __name__ == '__main__':
    pass
    logger = Log('mylogger', './xxx.log', log_level='DEBUG', is_write_to_console=True, is_write_to_file=True,
                 color=True, mode='a', save_time_log_path='./logs')
    # import time
    # while True:
    logger.debug("debug message")
    logger.info("info level message")
    logger.warning("warning level message")
    logger.critical("critical level message 你好")
    # time.sleep(1)
