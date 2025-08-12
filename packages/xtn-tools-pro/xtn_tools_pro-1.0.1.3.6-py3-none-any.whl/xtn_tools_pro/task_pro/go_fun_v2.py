#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2025/1/18    xiatn     V00.01.000    新建
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


class GoFunTaskV2:
    def __init__(self, ini_dict, logger, go_task_function):
        self.logger = logger

        # 读取配置信息
        host = ini_dict.get('host', '')  # 域名
        port = ini_dict.get('port', 0)  # 端口
        task = ini_dict.get('task', '')  # 任务
        auto = ini_dict.get('auto', '')  # token
        processes_num = ini_dict.get('processes_num', 0)  # 进程数
        thread_num = ini_dict.get('thread_num', 0)  # 线程数
        restart_time = ini_dict.get('restart_time', 0)  # 间隔x秒强制重启
        restart_time = 30 * 60 if restart_time <= 0 else restart_time  # 间隔x秒强制重启时间不传默认60分钟
        update_proxies_time = ini_dict.get('update_proxies_time', 0)  # 间隔x秒更新代理
        upload_task_tine = ini_dict.get('upload_task_tine', 0)  # 回写间隔
        download_not_task_tine = ini_dict.get('download_not_task_tine', 0)  # 当遇到下载任务接口返回空任务时,间隔x秒再继续请求,默认2秒
        download_not_task_tine = 2 if download_not_task_tine <= 0 else download_not_task_tine  # 当遇到下载任务接口返回空任务时,间隔x秒再继续请求,默认2秒

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
            "processes_num": int(processes_num),
            "thread_num": int(thread_num),
            "restart_time": int(restart_time),
            "update_proxies_time": int(update_proxies_time),
            "upload_task_tine": int(upload_task_tine),
            "download_url": download_url,  # 获取任务地址
            "upload_url": upload_url,  # 回写任务地址
            "update_proxy_url": update_proxy_url,  # 更新代理地址
            "external_ip": external_ip,
            "download_not_task_tine": download_not_task_tine,
        }

        logger.debug(
            f"\n无敌框架来咯~~~当前设置配置如下:"
            f"\n\t功能函数重启间隔:{restart_time};进程数:{processes_num};线程数:{thread_num}"
            f"\n\t代理更新间隔:{update_proxies_time};回写间隔{upload_task_tine};\n"
        )

        # 主子进程
        task_create_process_cnt = 1
        while True:
            try:
                logger.warning(f"主子进程 第{task_create_process_cnt}次打开进程;")
                task_create_process = multiprocessing.Process(target=self._create_process,
                                                              name="task_create_process",
                                                              args=(self.__ini_info, logger, go_task_function)
                                                              )
                task_create_process.start()
                time.sleep(restart_time)
                task_create_process.terminate()  # 关闭所有进程
                task_create_process.join()
                task_create_process.kill()
                logger.warning(f"主子进程 第{task_create_process_cnt}次关闭进程;")
            except Exception as e:
                logger.critical(f"主子进程 异常 - {e};")

            task_create_process_cnt += 1

    def __get_external_ip(self):
        """
            获取当前网络ip
        :return:
        """
        while True:
            try:
                rp = requests.get('https://httpbin.org/ip')
                rp_json = rp.json()
                self.logger.warning(f"当前网络ip --> {rp_json}")
                return rp_json['origin']
            except Exception as e:
                self.logger.critical(f"获取当前网络ip{e}")

    def _create_process(self, ini_info, logger, go_task_function):
        caller = inspect.stack()[1]  # 获取调用者的调用栈信息
        caller_name = caller.function  # 获取调用者的函数名
        caller_class = caller.frame.f_locals.get('self', None)  # 获取调用者的类实例
        if caller_name != "run" or caller_class is None:
            raise Exception("错误调用")

        # 共享任务队列
        manager = multiprocessing.Manager()
        download_queue = multiprocessing.Queue()
        upload_queue = multiprocessing.Queue()
        proxies_dict = manager.dict()
        manager_ns = manager.dict()
        manager_ns["gofun_task_kill_status"] = False

        # 下载回写代理
        download_and_upload_task_process = multiprocessing.Process(target=self._download_and_upload_task,
                                                                   name="_download_and_upload_task",
                                                                   args=(ini_info, logger, download_queue,
                                                                         upload_queue, proxies_dict, manager_ns)
                                                                   )
        download_and_upload_task_process.start()

        # gofun
        go_task_fun_task_process = multiprocessing.Process(target=self._go_task_fun_task,
                                                           name="_go_task_fun_task",
                                                           args=(ini_info, logger, download_queue,
                                                                 upload_queue, proxies_dict, go_task_function)
                                                           )
        go_task_fun_task_process.start()

        while True:
            logger.debug("进程正常...")
            gofun_task_kill_status = manager_ns["gofun_task_kill_status"]
            if gofun_task_kill_status:
                go_task_fun_task_process.kill()
                go_task_fun_task_process.terminate()
                go_task_fun_task_process.join()

            time.sleep(10)

    def _download_and_upload_task(self, ini_info, logger, download_queue, upload_queue, proxies_dict, manager_ns):
        """
            使用3个线程 打开 获取任务、回写任务、代理维护
        :param ini_info:
        :param logger:
        :param download_queue:
        :param upload_queue:
        :param proxies_dict:
        :return:
        """
        caller = inspect.stack()[1]  # 获取调用者的调用栈信息
        caller_name = caller.function  # 获取调用者的函数名
        caller_class = caller.frame.f_locals.get('self', None)  # 获取调用者的类实例
        if caller_name != "run" or caller_class is None:
            raise Exception("错误调用")

        # 获取任务
        thread_download_task = threading.Thread(target=self.__download_task,
                                                args=(download_queue, ini_info, logger, manager_ns))
        thread_download_task.start()

        # 回写任务
        thread_upload_task = threading.Thread(target=self.__upload_task,
                                              args=(upload_queue, ini_info, logger))
        thread_upload_task.start()

        # 维护代理
        thread_update_proxy = threading.Thread(target=self.__update_proxy,
                                               args=(proxies_dict, ini_info, logger))
        thread_update_proxy.start()

    def __download_task(self, download_queue, ini_info, logger, manager_ns):
        """
            获取任务
        :param queue:
        :return:
        """
        download_url = ini_info["download_url"]
        auto = ini_info["auto"]
        task = ini_info["task"]
        headers = {"Authorization": auto}
        params = {"taskType": task}

        download_queue_exist_cnt = 10
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
                    download_queue_exist_cnt -= 1
                    time.sleep(10)
                    if download_queue_exist_cnt <= 0 and manager_ns["gofun_task_kill_status"] == False:
                        manager_ns["gofun_task_kill_status"] = True
                        logger.warning("获取任务个数为0已超设置值,判断为无任务将关闭相关进程")
                    continue

                download_queue_exist_cnt = 10
                manager_ns["gofun_task_kill_status"] = False

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

    def _go_task_fun_task(self, ini_info, logger, download_queue, upload_queue, proxies_dict, go_task_function):
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
                        time.sleep(1)

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

    def get_download_task(self, download_queue, block, timeout):
        """
            获取下载任务
        :param download_queue:下载队列
        :param block: 是否阻塞等待 True阻塞/False不阻塞
        :param timeout:
        :return:
        error_code:1001 队列为空;
        """
        try:
            task_item = download_queue.get(block=block, timeout=timeout)
            return task_item
        except queue.Empty as e:
            # 捕获队列为空的异常
            # self.logger.info(f"get_download_task 获取下载任务 {download_queue, block, timeout} 报错 队列为空: {e}")
            return {"error": "队列为空", "error_code": 1001}
        except Exception as e:
            self.logger.critical(f"get_download_task 获取下载任务 {download_queue, block, timeout} 报错 {e}")
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
            self.logger.critical(f"update_upload_task 更新任务 {upload_queue, task_item} 报错 {e}")
            return False

    def reboot_process(self):
        pass
