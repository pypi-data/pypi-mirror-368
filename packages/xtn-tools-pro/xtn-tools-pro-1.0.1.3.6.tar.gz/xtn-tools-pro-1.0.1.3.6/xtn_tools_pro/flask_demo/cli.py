#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    程序说明xxxxxxxxxxxxxxxxxxx
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2025/3/13    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import os
import shutil
import argparse


def replace_placeholders(file_path, project_name):
    """
    替换文件中的占位符 {{ project_name }} 为实际的项目名称
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 替换占位符
    content = content.replace("{{ project_name }}", project_name)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def create_project(args):
    """
    创建 flask 常用项目结构
    """
    # 获取当前目录
    project_name = args.obj_name
    current_dir = os.getcwd()
    project_dir = os.path.join(current_dir, project_name)

    # 创建项目目录
    os.makedirs(project_dir, exist_ok=True)

    # 复制模板文件到项目目录
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    # print("template_dir", template_dir)
    # print("project_dir", project_dir)
    for item in os.listdir(template_dir):
        src = os.path.join(template_dir, item)
        dst = os.path.join(project_dir, item)
        # print("item", item)
        # print("src", src)
        # print("dst", dst)
        # print("==========================")

        if os.path.isdir(src):
            shutil.copytree(src, dst)  # 判断是否为目录,递归地复制整个目录树
        else:
            shutil.copy2(src, dst)

        # 如果是文件，替换占位符
        if os.path.isfile(dst):
            replace_placeholders(dst, project_name)


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # 自定义错误消息
        # self.print_help()
        print("错误：缺少必需的参数！")
        print("请使用以下格式运行：xtn_tools_pro startobj <项目名称>")
        self.exit(2)  # 退出程序，返回状态码 2


def main():
    """
    命令行入口
    """
    parser = CustomArgumentParser(description="创建一个常用的flask项目结构")  # 创建 ArgumentParser 对象
    subparsers = parser.add_subparsers(title="命令", dest="command")

    parser_startobj = subparsers.add_parser('startobj', help="项目名称")  # 添加位置参数
    parser_startobj.add_argument("obj_name", type=str, help="项目的名称")
    parser_startobj.set_defaults(func=create_project)  # 绑定处理函数

    args = parser.parse_args()

    # 如果没有提供子命令，显示帮助信息
    if not hasattr(args, "func"):
        parser.print_help()
        return

    # 调用子命令对应的处理函数
    args.func(args)


if __name__ == "__main__":
    main()
