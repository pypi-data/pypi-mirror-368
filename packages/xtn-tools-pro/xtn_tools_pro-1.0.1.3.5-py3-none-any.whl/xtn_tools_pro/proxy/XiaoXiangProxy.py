#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    小象代理专用
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2024/4/27    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import requests, time, random
from xtn_tools_pro.db.RedisDB import RedisDBPro
from xtn_tools_pro.utils.time_utils import get_time_now_timestamp, get_time_now_day59_timestamp

import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.filterwarnings("ignore", category=InsecureRequestWarning)


class ProxyPool:
    def __init__(self, ip, port, db=0, user_pass="", redis_proxy_name="XiaoXiangProxy",
                 XiaoXiangProxyAppKey=None, XiaoXiangProxyAppSecret=None, usage_cnt=100, usage_time=100):
        """
            小象代理专用
        :param ip: redis 数据库 ip
        :param port: redis 数据库 端口
        :param db: redis 数据库 db
        :param user_pass: redis 数据库 密码
        :param redis_proxy_name: redis 数据库 用于存储代理的key
        :param XiaoXiangProxyAppKey: 小象代理 应用id appKey
        :param XiaoXiangProxyAppSecret: 小象代理 应用密码 appSecret
        :param usage_cnt: 每个代理最长使用次数 单位秒 维护代理时用
        :param usage_time: 每个代理最长使用时间 单位秒 维护代理时用
        :param is_log: 是否记录日志
        """
        if not XiaoXiangProxyAppSecret or not XiaoXiangProxyAppKey:
            raise Exception("应用密码或应用id 不能为空")

        r = RedisDBPro(ip=ip, port=port, db=db, user_pass=user_pass)
        self.__redis_pool = r
        self.__redisProxyName = redis_proxy_name
        self.__XiaoXiangProxyAPI = "https://api.xiaoxiangdaili.com/ip/get?appKey={appKey}&appSecret={appSecret}&cnt=&wt=json".format(
            appKey=XiaoXiangProxyAppKey, appSecret=XiaoXiangProxyAppSecret)
        self.__XiaoXiangAutoBinding = "https://api.xiaoxiangdaili.com/app/bindIp?appKey={appKey}&appSecret={appSecret}&i=1".format(
            appKey=XiaoXiangProxyAppKey, appSecret=XiaoXiangProxyAppSecret)

        # 获取当天0点时间戳
        self.__now_day59_timestamp = get_time_now_day59_timestamp()
        self.__usage_cnt = usage_cnt
        self.__usage_time = usage_time

        # if is_log:
        #     # 日志
        #     nowDate = str(datetime.datetime.now().strftime('%Y_%m_%d'))
        #     logger.add(loggerPath.format(t=nowDate))

        self.bind_ip()

    def __log(self, text):
        """
            记录日志
        :param text:
        :return:
        """
        print(text)

    def __check_proxy(self):
        """
            维护检查代理，删除无用代理
            删除标准：1.代理使用超过xx次；2.使用时间超过xx秒；3.被爬虫标记使用次数为 999999 会被删除
        :return:
        """
        proxy_val_list = list(self.__redis_pool.get_all_key("{}*".format(self.__redisProxyName)))
        for proxy_val in proxy_val_list:
            # 获取时间
            time_out = proxy_val.split(":")[-1]
            # 获取使用次数
            proxy_val_count = int(self.__redis_pool.get(proxy_val))
            if int(time_out) + self.__usage_time < get_time_now_timestamp(is_time_10=True):
                del_state = self.__redis_pool.delete(proxy_val)
                self.__log(
                    "当前代理状态:{proxy_val},{time_out}_{py_time}当前代理已超过使用时间,删除状态为：{del_state}".
                        format(proxy_val=proxy_val, del_state=del_state,
                               time_out=time_out, py_time=get_time_now_timestamp(is_time_10=True)))
            elif int(proxy_val_count) >= self.__usage_cnt:
                del_state = self.__redis_pool.delete(proxy_val)
                self.__log(
                    "当前代理状态:{proxy_val},{text},删除状态为：{del_state}".format(proxy_val=proxy_val,
                                                                         text="当前代理被爬虫标记为不可用" if proxy_val_count >= 999999 else "当前代理已超过使用时间",
                                                                         del_state=del_state))

    def __get_proxy_length(self):
        """
            获取代理数
        :return:
        """
        proxy_val_list = list(self.__redis_pool.get_all_key("{}*".format(self.__redisProxyName)))
        return len(proxy_val_list)

    def __incr_proxy(self, proxy_val):
        """
            自增代理使用次数
        :param proxy_val: 代理
        :return:
        """
        proxy_val_con = self.__redis_pool.incr(proxy_val)
        return proxy_val_con

    def __get_api_proxy(self):
        """
            通过接口获取小象代理，并存储至数据库
            响应：
                {"code":1010,"success":false,"data":null,"msg":"请求过于频繁"}
                {"code":200,"success":true,"data":[{"ip":"125.123.244.60","port":37635,"realIp":null,"startTime":"2024-04-27 14:09:42","during":2}],"msg":"操作成功"}
        :return:
        """
        while True:
            self.__check_proxy()
            try:
                response = requests.get(url=self.__XiaoXiangProxyAPI, verify=False, timeout=3)
                if response.status_code == 200:
                    if response.json().get("msg") == "请求过于频繁":
                        self.__log("获取小象代理过于频繁，等待2s，{content}".format(content=response.text))
                        time.sleep(2)
                        continue
                    # 获取data
                    proxy_data_list = response.json().get("data", [])
                    if not proxy_data_list:
                        self.__log("获取小象代理失败 data 为空，等待2s，{content}".format(content=response.text))
                        time.sleep(2)
                        continue
                    else:
                        for data in proxy_data_list:
                            ip = "http://{ip}".format(ip=data.get("ip"))
                            port = data.get("port")
                            time_out = get_time_now_timestamp(is_time_10=True)
                            proxy_key = "{redis_proxy_name}:{ip}:{port}:{timeOut}".format(
                                redis_proxy_name=self.__redisProxyName,
                                ip=ip,
                                port=port,
                                timeOut=time_out,
                            )
                            proxy_key_con = self.__incr_proxy(proxy_key)
                            self.__log("获取代理:{proxy_key}，插入数据库状态为{proxy_key_con}".format(proxy_key=proxy_key,
                                                                                         proxy_key_con=proxy_key_con))
                        return True  # 获取成功
                else:
                    self.__log("获取小象代理返回响应码不为200，等待2s，{content}".format(content=response.text))
                    time.sleep(2)
                    continue
            except Exception as e:
                self.__log("获取小象代理报错：{e}".format(e=e))

    def bind_ip(self):
        # 手动绑定终端IP
        response = requests.get(url=self.__XiaoXiangAutoBinding, verify=False, timeout=3)
        self.__log(response.text)

    def run(self):
        while True:
            try:
                self.bind_ip()
                while True:
                    # 检查代理
                    self.__check_proxy()
                    # 获取小象代理
                    self.__get_api_proxy()
                    time.sleep(1)
                    # 判断时间是否超过当前23:59分时间戳
                    # t_a = get_time_now_timestamp(is_time_10=True)
                    # if t_a >= self.__now_day59_timestamp:
                    #     self.__log(
                    #         "时间23:59，结束循环，{t} {a} {a_v} {b} {b_v}".format(t=int(time.time()),
                    #                                                       a=type(t_a),
                    #                                                       a_v=t_a,
                    #                                                       b=type(self.__now_day59_timestamp),
                    #                                                       b_v=self.__now_day59_timestamp)
                    #     )
                    #     break
            except Exception as eee:
                self.__log("程序异常报错:{eee} {b_t} {b_v}".format(eee=eee,
                                                             b_t=type(self.__now_day59_timestamp),
                                                             b_v=self.__now_day59_timestamp))
                self.__check_proxy()
                # self.__del__()

    def get_proxy(self):
        """
            从代理池中获取代理
        :return:
        """
        try:
            while True:
                proxy_val_list = list(self.__redis_pool.get_all_key("{}*".format(self.__redisProxyName)))
                if proxy_val_list:
                    proxy_val = random.choice(proxy_val_list)
                    proxy_v = ":".join(str(proxy_val).split(":")[1:-1])
                    self.__log("获取到的代理为：{proxy_v}".format(proxy_v=proxy_v))
                    return proxy_v
                else:
                    self.__log("暂无代理，等待中")
                    time.sleep(2)
        except Exception as e:
            self.__log("从代理池中获取代理：{e}".format(e=e))

    def set_proxy_error(self, proxy_v):
        """
            爬虫手动传入代理，设置为 999999 不可用
        :param proxyV:
        :return:
        """
        try:
            proxy_val_list = list(self.__redis_pool.get_all_key("{}*".format(self.__redisProxyName)))
            for proxy_val in proxy_val_list:
                if proxy_v in proxy_val:
                    self.__redis_pool.set(proxy_val, "999999")
                    self.__log("设置不可用的代理 {proxy_v} 为 999999".format(proxy_v=proxy_v))
                    return
        except Exception as e:
            self.__log("爬虫手动传入代理：{e}".format(e=e))


if __name__ == '__main__':
    p = ProxyPool(ip="127.0.0.1", port=6379, db=0, user_pass="xtn-kk", XiaoXiangProxyAppKey="1107231349661913088",
                  XiaoXiangProxyAppSecret="8kignGIX")
    # print(p.set_proxy_error("http://49.83.105.188:32300"))
    p.run()
