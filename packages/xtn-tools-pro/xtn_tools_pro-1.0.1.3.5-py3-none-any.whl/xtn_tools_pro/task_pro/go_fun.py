#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    程序说明xxxxxxxxxxxxxxxxxxx
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2025/1/14    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import time
import random
import inspect
import requests
import threading
import multiprocessing
import concurrent.futures
from multiprocessing import Process
from xtn_tools_pro.utils.time_utils import get_time_now_timestamp


class GoFun:
    def __init__(self, ini_dict, logger, go_task_function=None):
        # 读取配置信息
        host = ini_dict.get('host', '')
        port = ini_dict.get('port', 0)
        task = ini_dict.get('task', '')
        auto = ini_dict.get('auto', '')
        processes_num = ini_dict.get('processes_num', 0)
        thread_num = ini_dict.get('thread_num', 0)
        restart_time = ini_dict.get('restart_time', 0)
        update_proxies_time = ini_dict.get('update_proxies_time', 0)
        upload_task_tine = ini_dict.get('upload_task_tine', 0)

        self.logger = logger

        self.__ini_info = {
            "host": host,
            "port": int(port),
            "task": task,
            "auto": auto,
            "processes_num": int(processes_num),
            "thread_num": int(thread_num),
            "restart_time": int(restart_time),
            "update_proxies_time": int(update_proxies_time),
            "upload_task_tine": int(upload_task_tine),
        }

        for server_k, server_v in self.__ini_info.items():
            if not server_v and server_k not in ["port", "processes_num", "thread_num", "restart_time",
                                                 "update_proxies_time", "upload_task_tine"]:
                raise Exception(f"ini_dict 配置 {server_k} 不存在")

        logger.debug(
            f"\n无敌框架来咯~~~当前设置配置如下:\n\t功能函数重启间隔:{restart_time};进程数:{processes_num};线程数:{thread_num}\n\t代理更新间隔:{update_proxies_time};回写间隔{upload_task_tine}\n")

        if port:
            task_host = f"http://{host}:{port}"
        else:
            task_host = f"http://{host}"

        download_url = task_host + "/filter_server/phone/get"
        upload_url = task_host + "/filter_server/phone/update"
        update_proxy_url = task_host + f"/filter_server/proxy/random/get?taskType={task}&limit=1"

        external_ip = self.__get_external_ip(self.logger)

        self.__ini_info["download_url"] = download_url
        self.__ini_info["upload_url"] = upload_url
        self.__ini_info["update_proxy_url"] = update_proxy_url
        self.__ini_info["external_ip"] = external_ip

        if not go_task_function:
            return

        self.__go_task_function = go_task_function
        self.__create_process()

    def __create_process(self):
        # 共享任务队列
        manager = multiprocessing.Manager()
        download_queue = multiprocessing.Queue()
        upload_queue = multiprocessing.Queue()
        proxies_dict = manager.dict()

        self.download_queue = download_queue
        self.upload_queue = upload_queue
        self.proxies_dict = proxies_dict

        restart_time = int(self.__ini_info["restart_time"])
        self.__processes_item_info = {
            "_download_and_upload_task": {
                "target": self._download_and_upload_task,
                "name": "_download_and_upload_task",
                "args": (download_queue, upload_queue, proxies_dict, self.__ini_info, self.logger),
                "start_time": 0,
                "restart_time": restart_time,
            },
            "_go_task_fun_task": {
                "target": self._go_task_fun_task,
                "name": "_go_task_fun_task",
                "args": (
                    download_queue, upload_queue, proxies_dict, self.__ini_info, self.__go_task_function, self.logger),
                "start_time": 0,
                "restart_time": int(restart_time),
            },
        }

        for p_item in self.__processes_item_info.values():
            task_process = multiprocessing.Process(target=p_item["target"], name=p_item["name"], args=p_item["args"])
            self.__processes_item_info[p_item["name"]]["task_process"] = task_process
            self.__processes_item_info[p_item["name"]]["start_time"] = get_time_now_timestamp(is_time_10=True)
            task_process.start()
            self.logger.warning(f"进程已启动,{task_process.is_alive()},{task_process.name},{task_process.pid}")

        while True:
            time.sleep(10)
            for p_item_info in self.__processes_item_info.values():
                task_process = p_item_info["task_process"]
                task_process_start_time = p_item_info["start_time"]
                task_process_restart_time = p_item_info.get("restart_time", 0)
                # 检查子进程是否存活
                task_process_pid = task_process.pid
                task_process_name = task_process.name
                task_process_is_alive = task_process.is_alive()
                if not task_process_is_alive:
                    self.logger.critical(f"进程不存在,{task_process_is_alive},{task_process_name},{task_process_pid}")
                    p_item = self.__processes_item_info[task_process_name]
                    task_process = multiprocessing.Process(target=p_item["target"], name=p_item["name"],
                                                           args=p_item["args"])

                    self.__processes_item_info[task_process_name]["task_process"] = task_process
                    self.__processes_item_info[task_process_name]["start_time"] = get_time_now_timestamp(
                        is_time_10=True)
                    task_process.start()
                    self.logger.warning(f"进程已重启,{task_process.is_alive()},{task_process.name},{task_process.pid}")
                else:
                    if not task_process_restart_time:
                        continue
                    if task_process_start_time + task_process_restart_time <= get_time_now_timestamp(is_time_10=True):
                        self.logger.critical(
                            f"进程已超过设置时间，正在强制关闭进程,{task_process_restart_time},{task_process_is_alive},{task_process_name},{task_process_pid}")
                        task_process.terminate()
                        task_process.join()  # 等待进程确实结束
                        p_item = self.__processes_item_info[task_process_name]
                        task_process = multiprocessing.Process(target=p_item["target"], name=p_item["name"],
                                                               args=p_item["args"])

                        self.__processes_item_info[task_process_name]["task_process"] = task_process
                        self.__processes_item_info[task_process_name]["start_time"] = get_time_now_timestamp(
                            is_time_10=True)
                        task_process.start()
                        self.logger.warning(f"进程已重启,{task_process.is_alive()},{task_process.name},{task_process.pid}")

    def __get_external_ip(self, logger):
        """
            获取当前网络ip
        :return:
        """
        while True:
            try:
                rp = requests.get('https://httpbin.org/ip')
                rp_json = rp.json()
                logger.warning(f"当前网络ip --> {rp_json}")
                return rp_json['origin']
            except Exception as e:
                logger.critical(f"获取当前网络ip{e}")

    def _download_and_upload_task(self, download_queue, upload_queue, proxies_dict, ini_info, logger):
        """
            使用两个线程 打开 获取任务、回写任务
        :param queue:
        :return:
        """
        caller = inspect.stack()[1]  # 获取调用者的调用栈信息
        caller_name = caller.function  # 获取调用者的函数名
        caller_class = caller.frame.f_locals.get('self', None)  # 获取调用者的类实例
        if caller_name != "run" or caller_class is None:
            raise Exception("错误调用")
        # 获取任务
        thread_download_task = threading.Thread(target=self.__download_task,
                                                args=(download_queue, ini_info, logger))
        thread_download_task.start()
        # 回写任务
        thread_upload_task = threading.Thread(target=self.__upload_task,
                                              args=(upload_queue, ini_info, logger))
        thread_upload_task.start()
        # 维护代理
        thread_update_proxy = threading.Thread(target=self.__update_proxy,
                                               args=(proxies_dict, ini_info, logger))
        thread_update_proxy.start()

    def __download_task(self, download_queue, ini_info, logger):
        """
            获取任务
        :param queue:
        :return:
        """
        download_url = ini_info["download_url"]
        external_ip = ini_info["external_ip"]
        auto = ini_info["auto"]
        task = ini_info["task"]
        headers = {"Authorization": auto}
        params = {"taskType": task}
        while True:
            try:
                qsize = download_queue.qsize()
                logger.info(f"当前队列剩余任务数:{qsize}")
                if qsize >= 10:
                    time.sleep(2)
                    continue
                resp = requests.get(download_url, headers=headers, params=params, timeout=5)
                json_data = resp.json()
                result_list = json_data.get("result", [])

                if len(result_list) <= 0:
                    # 判断任务响应是否为空
                    time.sleep(2)
                    continue
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
        upload_task_tine = ini_info["upload_task_tine"]
        headers = {"Authorization": auto}
        params = {"taskType": task}
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
                logger.critical(f"循环全部获取队列的任务{e}")

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

            if not upload_task_tine:
                # 一直执行 不退出
                continue
            time.sleep(upload_task_tine)

    def __update_proxy(self, proxies_dict, ini_info, logger):
        """
            更新代理
        :return:
        """
        update_proxy_url = ini_info["update_proxy_url"]
        auto = ini_info["auto"]
        update_proxies_time = ini_info["update_proxies_time"]
        headers = {"Authorization": auto}

        while True:
            try:
                if not proxies_dict.get("status"):
                    resp = requests.get(update_proxy_url, headers=headers, timeout=5)
                    json_data = resp.json()
                    status_code = resp.status_code
                    result_list = json_data.get("result", [])
                    if not result_list or status_code != 200:
                        logger.critical(f"获取代理响应异常:{status_code} {len(result_list)} {json_data}")
                        time.sleep(2)

                    proxies_dict['http'] = 'http://' + random.choice(result_list)
                    proxies_dict['https'] = 'http://' + random.choice(result_list)
                    proxies_dict['status'] = True
                    logger.warning(f"成功获取代理:{proxies_dict}")

                if not update_proxies_time:
                    # 一直执行 不退出
                    continue

                time.sleep(update_proxies_time)
                proxies_dict['status'] = False
            except Exception as e:
                logger.critical(f"获取代理请求异常:{e}")
                time.sleep(2)

    def _go_task_fun_task(self, download_queue, upload_queue, proxies_dict, ini_info, go_task_function, logger):
        """
            单函数，根据配置启动程序
        :param queue:
        :return:
        """
        caller = inspect.stack()[1]  # 获取调用者的调用栈信息
        caller_name = caller.function  # 获取调用者的函数名
        caller_class = caller.frame.f_locals.get('self', None)  # 获取调用者的类实例
        if caller_name != "run" or caller_class is None:
            raise Exception("错误调用")

        processes_num = ini_info["processes_num"]
        thread_num = ini_info["thread_num"]
        restart_time = ini_info["restart_time"]

        processes_num = 1 if processes_num <= 0 else processes_num
        thread_num = 1 if thread_num <= 0 else thread_num

        go_task_fun_cnt = 0
        processes_start_list = []
        while True:
            try:
                if not processes_start_list:
                    go_task_fun_cnt += 1
                    logger.info(
                        f"第{go_task_fun_cnt}次,进程数:{processes_num},线程数:{thread_num},等待{restart_time}秒强制下一次")
                    for i in range(processes_num):
                        p = Process(target=self._run_with_timeout,
                                    args=(
                                        download_queue, upload_queue, proxies_dict, thread_num, logger,
                                        go_task_function))
                        processes_start_list.append(p)
                        p.start()

                if not restart_time:
                    # 一直执行 不退出
                    continue

                time.sleep(restart_time)
                # 关闭所有进程
                for p in processes_start_list:
                    p.terminate()
                    p.join()  # 等待进程确实结束
                processes_start_list = []

            except Exception as e:
                logger.critical(f"_go_task_fun_task-{e}")

    def _run_with_timeout(self, download_queue, upload_queue, proxies_dict, thread_num, logger, go_task_function):
        caller = inspect.stack()[1]  # 获取调用者的调用栈信息
        caller_name = caller.function  # 获取调用者的函数名
        caller_class = caller.frame.f_locals.get('self', None)  # 获取调用者的类实例
        if caller_name != "run" or caller_class is None:
            raise Exception("错误调用")

        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_num) as executor:
            # 提交10个函数到线程池中执行
            futures = [executor.submit(go_task_function, self, download_queue, upload_queue, proxies_dict, logger)
                       for _ in range(thread_num)]

            # 等待所有线程完成
            for future in concurrent.futures.as_completed(futures):
                future.result()

    def get_ini_dict(self):
        """
            配置解释
        :return:
        """
        ini_dict = {
            "host": "域名",
            "port": "端口",
            "task": "任务",
            "auto": "token",
            "processes_num": "进程数",
            "thread_num": "线程数",
            "restart_time": "间隔x秒强制重启",
            "update_proxies_time": "间隔x秒更新代理",
            "upload_task_tine": "回写间隔",
        }
        return ini_dict

    def get_download_task(self, download_queue, block, timeout):
        """
            获取下载任务
        :param download_queue:下载队列
        :param block: 是否阻塞等待 True阻塞/False不阻塞
        :param timeout:
        :return:
        """
        try:
            task_item = download_queue.get(block=block, timeout=timeout)
            return task_item
        except Exception as e:
            self.logger.critical(f"get_download_task 获取下载任务 报错 {e}")
            return False

    def update_upload_task(self, upload_queue, task_item):
        """
            更新任务
        :param upload_queue:
        :param task_item:
        :return:
        """
        try:
            task_item = upload_queue.put(task_item)
            return task_item
        except Exception as e:
            self.logger.critical(f"update_upload_task 更新任务 报错 {e}")
            return False

    def reboot_process(self):
        print(self.__processes_item_info)
