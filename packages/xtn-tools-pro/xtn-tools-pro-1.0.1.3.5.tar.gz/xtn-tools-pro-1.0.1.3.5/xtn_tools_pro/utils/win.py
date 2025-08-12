#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    win 操作
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2025/8/11    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import psutil
import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)

# 回调类型：BOOL CALLBACK EnumWindowsProc(HWND hwnd, LPARAM lParam)
EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

# --- 明确声明所有用到的 WinAPI 的参数/返回类型 ---
user32.EnumWindows.argtypes = [EnumWindowsProc, wintypes.LPARAM]
user32.EnumWindows.restype = wintypes.BOOL

user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD

user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL

user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int  # 长度（TCHAR 数），可能为 0

user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int  # 实际拷贝的字符数


def enum_windows(only_visible=True):
    """
    遍历顶层窗口，返回 [{hwnd, pid, title}, ...]
    - only_visible=True 只返回可见窗口
    """
    results = []

    @EnumWindowsProc
    def callback(hwnd, lparam):
        try:
            # 可选过滤
            if only_visible and not user32.IsWindowVisible(hwnd):
                return True  # 继续枚举

            # 取 PID
            pid = wintypes.DWORD(0)
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

            # 取标题
            length = user32.GetWindowTextLengthW(hwnd)
            title = ""
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                copied = user32.GetWindowTextW(hwnd, buf, length + 1)
                if copied > 0:
                    title = buf.value

            # 结果里再把 HWND 规范化为无符号整数，避免负数显示
            results.append({
                "hwnd": ctypes.c_size_t(hwnd).value,
                "pid": pid.value,
                "title": title
            })
        except Exception:
            # 回调里不要把异常抛给 WinAPI，否则会出现 “Exception ignored on calling ctypes callback function”
            pass
        return True  # 继续

    user32.EnumWindows(callback, 0)
    return results


def kill_process_by_name(process_name, x=False):
    """
        遍历根据进程名杀死所有相关进程
    :param process_name:
    :return:
    """
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                if x:
                    print(f"Killing process: {proc.info['name']} (PID: {proc.info['pid']})")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue


if __name__ == "__main__":
    pass
    # 枚举win窗口获取句柄和pid
    # for win in enum_windows(only_visible=True):
    #     print(win)
