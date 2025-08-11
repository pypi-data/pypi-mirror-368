#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    程序说明xxxxxxxxxxxxxxxxxxx
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2024/4/18    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import redis, time


class RedisDBPro:
    def __init__(self, ip=None, port=None, db=None,
                 user_pass=None, url=None, decode_responses=True, max_connections=1000, **kwargs):

        self._ip = ip
        self._port = port
        self._db = db
        self._user_pass = user_pass
        self._url = url
        self._decode_responses = decode_responses  # 自动解码返回的字节串
        self._max_connections = max_connections  # 同一个redis对象使用的并发数（连接池的最大连接数），超过这个数量会抛出redis.ConnectionError
        self._kwargs = kwargs
        # 连接
        self.__redis = None
        self.get_connect()

    def __del__(self):
        self.__redis.close()

    @classmethod
    def from_url(cls, url):
        """

        Args:
            url: redis://[[username]:[password]]@[host]:[port]/[db]

        Returns:

        """
        return cls(url=url)

    @property
    def _redis(self):
        try:
            if not self.__redis.ping():
                raise ConnectionError("unable to connect to redis")
        except:
            self._reconnect()

        return self.__redis

    @_redis.setter
    def _redis(self, val):
        self.__redis = val

    def _reconnect(self):
        # 检测连接状态, 当数据库重启或设置 timeout 导致断开连接时自动重连
        retry_count = 0
        while True:
            try:
                retry_count += 1
                print("redis 连接断开, 重新连接 {retry_count}".format(retry_count=retry_count))
                if self.get_connect():
                    print("redis 连接成功")
                    return True
            except (ConnectionError, TimeoutError) as e:
                print("连接失败 e: {e}".format(e=e))
            time.sleep(2)

    def get_connect(self):
        # 数据库连接
        try:
            if not self._url:
                self._redis = redis.StrictRedis(
                    host=self._ip,
                    port=self._port,
                    db=self._db,
                    password=self._user_pass,
                    decode_responses=self._decode_responses,
                    max_connections=self._max_connections,
                    **self._kwargs,
                )
            else:
                # url连接
                self._redis = redis.StrictRedis.from_url(
                    self._url, decode_responses=self._decode_responses, **self._kwargs
                )

        except Exception as e:
            raise e

        return self.__redis.ping()

    def sadd(self, table, values):
        """
        使用无序set集合存储数据， 去重
        table:集合名
        values: 值； 支持list 或 单个值
        ---------
        @result: 若库中存在 返回0，否则入库，返回1。 批量添加返回None
        """
        if isinstance(values, list):
            pipe = self._redis.pipeline()  # 创建一个pipeline对象，可以添加多个操作，最后execute提交
            pipe.multi()
            for value in values:
                pipe.sadd(table, value)
            result = pipe.execute()
            # print(result) # [1, 1, 0, 0, 0, 0, 0]
            return result.count(1)
        else:
            return self._redis.sadd(table, values)

    def spop(self, table):
        """
            从集合中弹出元素
        :param table:
        :return:
        """
        return self._redis.spop(table)

    def sget_count(self, table):
        """
            获取无序集合数量
        :param table:
        :return:
        """
        return self._redis.scard(table)

    def get_redis(self):
        return self._redis

    def incr(self, key):
        """
            对一个键的值进行自增操作
        :param key: 需要自增的key
        :return:
        """
        return self._redis.incr(key)

    def get_all_key(self, path):
        """
            获取所有的key
            常用的path：前缀为test的key test*，中间为test的key *test*
        :param path:
        :return:
        """
        return list(self._redis.scan_iter(path))

    def get(self, table):
        return self._redis.get(table)

    def set(self, table, value, **kwargs):
        """
            字符串 set
        :param table: 表
        :param value: 值
        :param kwargs: 参数解释为chatgpt提供
        :param kwargs: ex（可选）：设置键的过期时间，以秒为单位。例如，ex=10表示键将在10秒后过期
        :param kwargs: px（可选）：设置键的过期时间，以毫秒为单位。例如，px=10000表示键将在10秒后过期
        :param kwargs: nx（可选）：如果设置为True，则只有在键不存在时才设置键的值
        :param kwargs: xx（可选）：如果设置为True，则只有在键已存在时才设置键的值
        :param kwargs: kepp_ttl（可选）：如果设置为True，则保留键的过期时间。仅当键已存在且设置了过期时间时才有效
        :param kwargs: exat（可选）：设置键的过期时间，以UNIX时间戳表示。
        :param kwargs: pxat（可选）：设置键的过期时间，以毫秒级的UNIX时间戳表示。
        :param kwargs: replace（可选）：如果设置为True，则无论键是否存在，都会设置键的值。
        :return:
        """
        return self._redis.set(table, value, **kwargs)

    def delete(self, table):
        return self._redis.delete(table)




if __name__ == '__main__':
    pass
    # r = RedisDBPro(ip="127.0.0.1", port=6379, db=0, user_pass="xtn-kk")
    r = RedisDBPro.from_url('redis://:xtn-kk@127.0.0.1:6379/0')
    # status = r.sadd("test_redis_pro", [1, 2, 3, 4, 5, "6", "7"])
    # print(status)
    # print(r.get_all_key("*http*"))
    print(r.delete("test_redis_pro"))
