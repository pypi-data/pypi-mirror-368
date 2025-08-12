#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    程序说明xxxxxxxxxxxxxxxxxxx
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2025/1/22    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import time
import queue
import random
import inspect
import requests
import threading
import multiprocessing
import concurrent.futures
from multiprocessing import Process
from xtn_tools_pro.utils.crypto import get_base64_encode
from xtn_tools_pro.utils.time_utils import get_time_now_timestamp


class GoFunTaskAirV1:
    def __init__(self, ini_dict, logger, go_task_function):
        self.logger = logger

        # 读取配置信息
        host = ini_dict.get('host', '')  # 域名
        port = ini_dict.get('port', 0)  # 端口
        task = ini_dict.get('task', '')  # 任务
        auto = ini_dict.get('auto', '')  # token

        thread_num = ini_dict.get('thread_num', 0)  # 线程数
        restart_time = ini_dict.get('restart_time', 0)  # 间隔x秒强制重启
        restart_time = 60 * 60 if restart_time <= 0 else restart_time  # 间隔x秒强制重启时间不传默认60分钟
        update_proxies_time = ini_dict.get('update_proxies_time', 0)  # 间隔x秒更新代理
        upload_task_time = ini_dict.get('upload_task_time', 0)  # 回写间隔
        download_not_task_time = ini_dict.get('download_not_task_time', 0)  # 当遇到下载任务接口返回空任务时,间隔x秒再继续请求
        download_task_qsize = ini_dict.get('download_task_qsize', 10)  # 触发下载任务队列的最低阈值(当下载队列小于等于x时就立刻请求下载任务接口获取任务),默认10个
        download_task_qsize = 10 if download_task_qsize < 0 else download_task_qsize  # 触发下载任务队列的最低阈值(当下载队列小于等于x时就立刻请求下载任务接口获取任务),默认10个

        thread_num = 1 if thread_num <= 0 else thread_num

        # 拼接地址
        if port:
            task_host = f"http://{host}:{port}"
        else:
            task_host = f"http://{host}"

        headers = {
            'Authorization': f"Basic {get_base64_encode(f'{auto}:')}"
        }

        download_url = task_host + "/filter_server/phone/get"
        upload_url = task_host + "/filter_server/phone/update"
        update_proxy_url = task_host + f"/filter_server/proxy/random/get?taskType={task}&limit=1"

        # 全部配置信息
        self.__ini_info = {
            "host": host,
            "port": int(port),
            "task": task,
            "auto": auto,
            "thread_num": int(thread_num),
            "restart_time": int(restart_time),
            "update_proxies_time": int(update_proxies_time),
            "upload_task_time": int(upload_task_time),
            "download_url": download_url,  # 获取任务地址
            "upload_url": upload_url,  # 回写任务地址
            "update_proxy_url": update_proxy_url,  # 更新代理地址
            "download_not_task_time": download_not_task_time,
            "download_task_qsize": download_task_qsize,
        }

        # 共享任务队列
        self.download_queue = multiprocessing.Queue()
        self.upload_queue = multiprocessing.Queue()
        manager = multiprocessing.Manager()  # 进程1
        self.manager_info = manager.dict()

        # 获取任务
        thread_download_task = threading.Thread(target=self.__download_task,
                                                args=(self.download_queue, self.manager_info, self.__ini_info, logger))
        thread_download_task.start()

        # 回写任务
        thread_upload_task = threading.Thread(target=self.__upload_task,
                                              args=(self.upload_queue, self.__ini_info, logger))
        thread_upload_task.start()

    def __download_task(self, download_queue, manager_info, ini_info, logger):
        """
            获取任务
        :param queue:
        :return:
        """
        download_url = ini_info["download_url"]
        auto = ini_info["auto"]
        task = ini_info["task"]
        download_not_task_time = ini_info["download_not_task_time"]
        download_task_qsize = ini_info["download_task_qsize"]
        headers = {"Authorization": auto}
        params = {"taskType": task}
        logger.warning("下载队列启动成功...")
        download_queue_exist_cnt = 3
        while True:
            try:
                qsize = download_queue.qsize()
                logger.info(f"当前队列剩余任务数:{qsize}")
                if qsize > download_task_qsize:
                    time.sleep(download_not_task_time)
                    continue
                resp = requests.get(download_url, headers=headers, params=params, timeout=5)
                json_data = resp.json()
                result_list = json_data.get("result", [])
                if not result_list or len(result_list) <= 0:
                    # 判断任务响应是否为空
                    download_queue_exist_cnt -= 1
                    if download_queue_exist_cnt <= 0 and not manager_info["gofun_kill_status"]:
                        manager_info["gofun_kill_status"] = True
                        logger.warning("获取任务个数为0已超设置值,判断为无任务将关闭相关进程")
                    time.sleep(10)
                    continue

                download_queue_exist_cnt = 10
                manager_info["gofun_kill_status"] = False

                for task_item in result_list:
                    phone_item = task_item["phone"]
                    if not phone_item.isdigit():  # 判断是否全是整数(不包括小数点或负号)
                        continue
                    download_queue.put(task_item)
                logger.warning(f"成功获取任务个数:{len(result_list)}")
            except Exception as e:
                logger.critical(f"获取任务请求异常:{e}")
                time.sleep(2)

    def __upload_task(self, upload_queue, ini_info, logger):
        """
            回写任务
        :return:
        """
        upload_url = ini_info["upload_url"]
        external_ip = ini_info["external_ip"]
        auto = ini_info["auto"]
        task = ini_info["task"]
        upload_task_time = ini_info["upload_task_time"]
        headers = {"Authorization": auto}
        params = {"taskType": task}
        logger.warning("回写队列启动成功...")
        while True:
            # 判断队列是否有值
            empty = upload_queue.empty()
            if empty:
                time.sleep(2)
                continue

            # 循环全部获取队列的任务
            result_list = []
            try:
                while True:
                    task_item = upload_queue.get_nowait()
                    taskNo = task_item["taskNo"]
                    phone = task_item["phone"]
                    isRegistered = task_item["isRegistered"]
                    country_region = task_item["country_region"]
                    full_phone = f"{country_region}{phone}"
                    task_item = {
                        'taskNo': taskNo,
                        'phone': full_phone,
                        'isRegistered': isRegistered
                    }
                    result_list.append(task_item)
            except Exception as e:
                pass
                # logger.critical(f"循环全部获取队列的任务{e}")

            # 回写任务
            data = {"result": result_list, "remoteAddr": external_ip}
            while True:
                try:
                    resp = requests.post(upload_url, json=data, headers=headers, params=params, timeout=5)
                    json_data = resp.json()
                    # logger.warning(f"成功回写任务个数:{len(result_list)},{json_data},{data}")
                    logger.warning(f"成功回写任务个数:{len(result_list)},{json_data}")
                    break
                except Exception as e:
                    logger.critical(f"回写异常,{len(result_list)},{e}")
                    time.sleep(2)

            if not upload_task_time:
                # 一直执行 不退出
                continue
            time.sleep(upload_task_time)

    def _run_with_timeout(self, download_queue, upload_queue, proxies_dict, thread_num, logger, go_task_function):
        caller = inspect.stack()[1]  # 获取调用者的调用栈信息
        caller_name = caller.function  # 获取调用者的函数名
        caller_class = caller.frame.f_locals.get('self', None)  # 获取调用者的类实例
        if caller_name != "run" or caller_class is None:
            raise Exception("错误调用")

        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_num) as executor:
            # 提交10个函数到线程池中执行
            futures = [executor.submit(go_task_function, self, proxies_dict, logger)
                       for _ in range(thread_num)]

            # 等待所有线程完成
            for future in concurrent.futures.as_completed(futures):
                future.result()

    def get_gofun_task_status(self):
        status = not self.manager_info["gofun_kill_status"]
        # self.logger.debug(f"get_gofun_task_status {status}")
        return status

    def get_download_task(self, block, timeout):
        """
            获取下载任务
        :param block: 是否阻塞等待 True阻塞/False不阻塞
        :param timeout:
        :return:
        error_code:1001 队列为空;
        """
        try:
            task_item = self.download_queue.get(block=block, timeout=timeout)
            task_item["success"] = True
            return task_item
        except queue.Empty as e:
            # 捕获队列为空的异常
            # self.logger.info(f"get_download_task 获取下载任务 {download_queue, block, timeout} 报错 队列为空: {e}")
            return {"error": "队列为空", "error_code": 1001}
        except Exception as e:
            self.logger.critical(f"get_download_task 获取下载任务 {self.download_queue, block, timeout} 报错 {e}")
            return False

    def update_upload_task(self, task_item):
        """
            更新任务
        :param task_item:
        :return:
        """
        try:
            task_item = self.upload_queue.put(task_item)
            return task_item
        except Exception as e:
            self.logger.critical(f"update_upload_task 更新任务 {self.upload_queue, task_item} 报错 {e}")
            return False
