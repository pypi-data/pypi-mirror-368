#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    音频、视频 处理
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2025/5/1    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
from moviepy.editor import VideoFileClip
from xtn_tools_pro.utils.file_utils import get_filename, get_parent_dir, path_join


def mp4_extracting_mp3(mp4_path, save_path=""):
    """
        从mp4视频中提取音频
    :param mp4_path:mp4文件路径
    :param save_path:保存位置,默认在mp4文件目录下和mp4同名
    :return:
    """
    video = VideoFileClip(mp4_path)
    audio = video.audio
    if save_path:
        audio.write_audiofile(save_path)
        return

    dir_path = get_parent_dir(mp4_path, 1)
    mp3_path = path_join(dir_path, f"{get_filename(mp4_path, suffix=False)}.mp3")
    audio.write_audiofile(mp3_path)


if __name__ == '__main__':
    pass
