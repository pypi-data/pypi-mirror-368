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
from xtn_tools_pro.utils.time_utils import get_time_now_timestamp


class GoFunTaskV3:
    def __init__(self, ini_dict, logger, go_task_function):
        self.logger = logger

        # 读取配置信息
        host = ini_dict.get('host', '')  # 域名
        port = ini_dict.get('port', 0)  # 端口
        task = ini_dict.get('task', '')  # 任务
        auto = ini_dict.get('auto', '')  # token
        proxies_dict = ini_dict.get('proxies_dict', {})  # 自定义代理
        processes_num = ini_dict.get('processes_num', 0)  # 进程数
        thread_num = ini_dict.get('thread_num', 0)  # 线程数
        restart_time = ini_dict.get('restart_time', 0)  # 间隔x秒强制重启
        restart_time = 60 * 60 if restart_time <= 0 else restart_time  # 间隔x秒强制重启时间不传默认60分钟
        update_proxies_time = ini_dict.get('update_proxies_time', 0)  # 间隔x秒更新代理
        upload_task_time = ini_dict.get('upload_task_time', 0)  # 回写间隔
        download_not_task_time = ini_dict.get('download_not_task_time', 0)  # 当遇到下载任务接口返回空任务时,间隔x秒再继续请求
        download_task_qsize = ini_dict.get('download_task_qsize', 10)  # 触发下载任务队列的最低阈值(当下载队列小于等于x时就立刻请求下载任务接口获取任务),默认10个
        download_task_qsize = 10 if download_task_qsize < 0 else download_task_qsize  # 触发下载任务队列的最低阈值(当下载队列小于等于x时就立刻请求下载任务接口获取任务),默认10个

        # 默认进程数和线程数
        processes_num = 1 if processes_num <= 0 else processes_num
        thread_num = 1 if thread_num <= 0 else thread_num

        # 拼接地址
        if port:
            task_host = f"http://{host}:{port}"
        else:
            task_host = f"http://{host}"
        download_url = task_host + "/filter_server/phone/get"
        upload_url = task_host + "/filter_server/phone/update"
        update_proxy_url = task_host + f"/filter_server/proxy/random/get?taskType={task}&limit=1"

        # 获取网络ip
        external_ip = self.__get_external_ip()

        # 全部配置信息
        self.__ini_info = {
            "host": host,
            "port": int(port),
            "task": task,
            "auto": auto,
            "proxies_dict": proxies_dict,
            "processes_num": int(processes_num),
            "thread_num": int(thread_num),
            "restart_time": int(restart_time),
            "update_proxies_time": int(update_proxies_time),
            "upload_task_time": int(upload_task_time),
            "download_url": download_url,  # 获取任务地址
            "upload_url": upload_url,  # 回写任务地址
            "update_proxy_url": update_proxy_url,  # 更新代理地址
            "external_ip": external_ip,
            "download_not_task_time": download_not_task_time,
            "download_task_qsize": download_task_qsize,
        }

        logger.debug(
            f"\n无敌框架来咯~~~当前设置配置如下:"
            f"\n\t功能函数重启间隔:{restart_time};进程数:{processes_num};线程数:{thread_num}"
            f"\n\t代理更新间隔:{update_proxies_time};回写间隔{upload_task_time};\n"
        )

        # 共享任务队列
        self.download_queue = multiprocessing.Queue()
        self.upload_queue = multiprocessing.Queue()
        manager = multiprocessing.Manager()  # 进程1
        self.manager_info = manager.dict()
        self.proxies_dict = proxies_dict if proxies_dict else manager.dict()

        # 获取任务
        thread_download_task = threading.Thread(target=self.__download_task,
                                                args=(self.download_queue, self.manager_info, self.__ini_info, logger))
        thread_download_task.start()

        # 回写任务
        thread_upload_task = threading.Thread(target=self.__upload_task,
                                              args=(self.upload_queue, self.__ini_info, logger))
        thread_upload_task.start()

        if not self.proxies_dict:
            # 维护代理
            thread_update_proxy = threading.Thread(target=self.__update_proxy,
                                                   args=(self.proxies_dict, self.manager_info, self.__ini_info, logger))
            thread_update_proxy.start()

        # go_task_fun_cnt = 0
        # go_task_fun_task_process = None
        self.manager_info["gofun_kill_status"] = False  # 进程kill状态，True需要kill/False无需kill
        self.manager_info["gofun_kill_status_qz"] = False  # 进程 强制 kill状态，True需要kill/False无需kill
        self.manager_info["gofun_run_status_time"] = get_time_now_timestamp(is_time_10=True)

        go_process_list = []
        go_task_fun_cnt = 0
        go_task_status_error = 0

        while True:
            qsize = self.download_queue.qsize()
            if not go_process_list and self.manager_info["gofun_kill_status"] and qsize:
                # 状态错误
                go_task_status_error += 1
                if go_task_status_error >= 10:
                    self.manager_info["gofun_kill_status"] = False
                logger.critical(
                    f"状态错误 次数{go_task_status_error}进程{len(go_process_list)}状态{self.manager_info['gofun_kill_status']}队列{qsize}")
                time.sleep(5)

            if not go_process_list and not self.manager_info["gofun_kill_status"]:
                # 未启动gofun 且 无需kill 则启动多进程多线程
                for i in range(processes_num):
                    p = Process(target=self._run_with_timeout,
                                args=(self.download_queue, self.upload_queue, self.proxies_dict, thread_num, logger,
                                      go_task_function))
                    go_process_list.append(p)
                    p.start()

                self.manager_info["gofun_run_status_time"] = get_time_now_timestamp(is_time_10=True)
                go_task_fun_cnt += 1
                logger.info(f"第{go_task_fun_cnt}次,进程数:{processes_num},线程数:{thread_num},等待{restart_time}秒强制下一次")

            elif self.manager_info["gofun_kill_status"] and go_process_list or self.manager_info[
                "gofun_kill_status_qz"]:
                # 需kill
                logger.info("检测到关闭指令，正在关闭gofun进程...")
                for p in go_process_list:
                    # p.terminate()
                    p.join()
                go_process_list = []
                go_task_status_error = 0
                self.manager_info["gofun_kill_status_qz"] = False
                logger.info("检测到关闭指令，关闭gofun成功!!!")

            elif not self.manager_info["gofun_kill_status"] and go_process_list:
                # 无需kill 且 任务进程启动 用于定时重启
                if self.manager_info["gofun_run_status_time"] + restart_time <= get_time_now_timestamp(is_time_10=True):
                    logger.info("检测到已达强制重启间隔，正在重启...")
                    self.manager_info["gofun_kill_status"] = True

            logger.info(
                f"主线程正常...进程数:{len(go_process_list)}...gofun(True不存在|False正常):{self.manager_info['gofun_kill_status']}...qz:{self.manager_info['gofun_kill_status_qz']}")
            time.sleep(10)

    def __get_external_ip(self, retry_cnt=10):
        """
            获取当前网络ip
        :return:
        """
        for _ in range(retry_cnt):
            try:
                rp = requests.get('https://httpbin.org/ip')
                rp_json = rp.json()
                self.logger.warning(f"当前网络ip --> {rp_json}")
                return rp_json['origin']
            except Exception as e:
                self.logger.critical(f"[重试{_ + 1}/{retry_cnt}]获取当前网络ip报错:{e}")
        return "0.0.0.0"

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
        now_qsize_v = None
        now_qsize_v_time = None
        while True:
            try:
                qsize = download_queue.qsize()
                logger.info(f"当前队列剩余任务数:{qsize}")
                if qsize > download_task_qsize:
                    if not now_qsize_v or qsize != now_qsize_v:
                        now_qsize_v = qsize
                        now_qsize_v_time = get_time_now_timestamp(is_time_10=True)

                    if now_qsize_v_time + (60 * 5) < get_time_now_timestamp(is_time_10=True):
                        now_qsize_v = None
                        now_qsize_v_time = None
                        manager_info["gofun_kill_status_qz"] = True

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

    def __update_proxy(self, proxies_dict, manager_info, ini_info, logger):
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
                if not manager_info.get("status"):
                    resp = requests.get(update_proxy_url, headers=headers, timeout=5)
                    json_data = resp.json()
                    status_code = resp.status_code
                    result_list = json_data.get("result", [])
                    if not result_list or status_code != 200:
                        logger.critical(f"获取代理响应异常:{status_code} {json_data}")
                        time.sleep(2)
                        continue

                    proxies_dict['http'] = 'http://' + random.choice(result_list)
                    proxies_dict['https'] = 'http://' + random.choice(result_list)
                    manager_info['status'] = True
                    logger.warning(f"成功获取代理:{proxies_dict}")

                if not update_proxies_time:
                    # 一直执行 不退出
                    time.sleep(2)
                    continue

                time.sleep(update_proxies_time)
                manager_info['status'] = False
            except Exception as e:
                logger.critical(f"获取代理请求异常:{e}")
                time.sleep(2)

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

    def get_download_task_list(self, block=False, timeout=1, get_cnt=1):
        """
            获取下载任务
        :param block: 是否阻塞等待 True阻塞/False不阻塞
        :param timeout:
        :param get_cnt: 获取任务的个数
        :return:
        error_code:1001 队列为空;
        """
        task_item_list = []
        for _ in range(get_cnt):
            try:
                task_item = self.download_queue.get(block=block, timeout=timeout)
                task_item["success"] = True
                task_item_list.append(task_item)
            except queue.Empty as e:
                # 捕获队列为空的异常
                # self.logger.info(f"get_download_task 获取下载任务 {download_queue, block, timeout} 报错 队列为空: {e}")
                # return {"error": "队列为空", "error_code": 1001}
                break
            except Exception as e:
                self.logger.critical(f"get_download_task 获取下载任务 {self.download_queue, block, timeout} 报错 {e}")
                # return False
                break

        return task_item_list

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

    def retry_download_task(self, task_item):
        """
            更新重试任务
        :param task_item:
        :return:
        """
        try:
            task_item = self.download_queue.put(task_item)
            return task_item
        except Exception as e:
            self.logger.critical(f"download_queue 更新重试任务 {self.upload_queue, task_item} 报错 {e}")
            return False

    def get_download_queue_size(self):
        """
            获取 下载队列 大小
        :return:
        """
        qsize = self.download_queue.qsize()
        return qsize

    def get_upload_queue_size(self):
        """
            获取 回写队列 大小
        :return:
        """
        qsize = self.upload_queue.qsize()
        return qsize

    def help(self):
        help_txt = """
        参数说明:
        host:必填,域名
        port:选填,端口
        task:必填,任务类型
        auto:必填,token
        proxies_dict:选填,默认为空,为空时会启动获取代理接口获取代理,不为空时则不启动该接口而是一直使用用户传递过来的代理
        update_proxies_time:选填,默认为0,间隔x秒更新代理,0则每次启动时获取一次之后就不在请求代理接口
        processes_num:选填,进程数,默认1
        thread_num:选填,线程数,默认1
        restart_time:选填,间隔x秒强制重启,默认60分钟
        upload_task_time:选填,回写间隔,默认0
        download_not_task_time:选填,默认0,当遇到下载任务接口返回空任务时,间隔x秒再继续请求
        download_task_qsize:选填,默认10,触发下载任务队列的最低阈值(当下载队列小于等于x时就立刻请求下载任务接口获取任务),默认10个
        """
        self.logger.info(help_txt)
