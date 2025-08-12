#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    程序说明xxxxxxxxxxxxxxxxxxx
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2024/5/11    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import json
import pymysql
import datetime
from pymysql import err
from urllib import parse
from pymysql import cursors
from typing import List, Dict
from dbutils.pooled_db import PooledDB
from xtn_tools_pro.utils.log import Log
from xtn_tools_pro.utils.sql import get_insert_sql, get_insert_batch_sql, get_update_sql

log = Log(name="MysqlDB", color=True)


def auto_retry(func):
    def wapper(*args, **kwargs):
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except (err.InterfaceError, err.OperationalError) as e:
                log.error(
                    """
                    error:%s
                    sql:  %s
                    """
                    % (e, kwargs.get("sql") or args[1])
                )

    return wapper


class MysqlDBPro:
    def __init__(self, ip, port, db, user_name, user_pass, **kwargs):
        try:
            self.connect_pool = PooledDB(
                creator=pymysql,  # 指定数据库连接的创建方法，这里使用的是pymysql作为创建方法
                mincached=1,  # 连接池中空闲连接的初始数量
                maxcached=100,  # 连接池中空闲连接的最大数量
                maxconnections=100,  # 连接池允许的最大连接数
                blocking=True,  # 当连接池达到最大连接数时，是否阻塞等待连接释放
                ping=7,  # 连接池中的连接在重新使用之前，是否需要进行ping操作来验证连接的有效性，这里的7是一个时间间隔，表示每隔7秒会对连接进行一次ping操作
                host=ip,  # 数据库主机的IP地址
                port=port,  # 数据库的端口号
                user=user_name,  # 连接数据库的用户名
                passwd=user_pass,  # 连接数据库的密码
                db=db,  # 连接的数据库名
                charset="utf8mb4",  # 连接数据库时使用的字符编码
                cursorclass=cursors.SSCursor,  # 指定使用的游标类，这里使用的是cursors.SSCursor，该游标类在多线程下大批量插入数据时可以减少内存的使用
            )  # cursorclass 使用服务的游标，默认的在多线程下大批量插入数据会使内存递增

        except Exception as e:
            log.error(
                """
            连接失败：
            ip: {}
            port: {}
            db: {}
            user_name: {}
            user_pass: {}
            exception: {}
            """.format(
                    ip, port, db, user_name, user_pass, e
                )
            )
        else:
            log.debug("连接到mysql数据库 %s : %s" % (ip, db))

    @classmethod
    def from_url(cls, url, **kwargs):
        """

        Args:
            url: mysql://username:password@ip:port/db?charset=utf8mb4
            url: mysql://username:password@127.0.0.1:port/db?charset=utf8mb4
            **kwargs:

        Returns:

        """
        url_parsed = parse.urlparse(url)

        db_type = url_parsed.scheme.strip()
        if db_type != "mysql":
            raise Exception(
                "url error, expect mysql://username:ip:port/db?charset=utf8mb4, but get {}".format(
                    url
                )
            )

        connect_params = {
            "ip": url_parsed.hostname.strip(),
            "port": url_parsed.port,
            "user_name": url_parsed.username.strip(),
            "user_pass": url_parsed.password.strip(),
            "db": url_parsed.path.strip("/").strip(),
        }

        connect_params.update(kwargs)

        return cls(**connect_params)

    @staticmethod
    def unescape_string(value):
        if not isinstance(value, str):
            return value
        value = value.replace("\\0", "\0")
        value = value.replace("\\\\", "\\")
        value = value.replace("\\n", "\n")
        value = value.replace("\\r", "\r")
        value = value.replace("\\Z", "\032")
        value = value.replace('\\"', '"')
        value = value.replace("\\'", "'")
        return value

    def get_connection(self):
        conn = self.connect_pool.connection(shareable=False)
        # cursor = conn.cursor(cursors.SSCursor)
        cursor = conn.cursor()

        return conn, cursor

    def close_connection(self, conn, cursor):
        """
            关闭数据库连接和游标对象
        :param conn:
        :param cursor:
        :return:
        """
        if conn:
            conn.close()
        if cursor:
            cursor.close()

    def execute(self, sql):
        """
            执行sql
        :param sql:
        :return:
        """
        conn, cursor = None, None
        try:
            conn, cursor = self.get_connection()
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            log.error(
                """
                error:%s
                sql:  %s
            """
                % (e, sql)
            )
            return False
        else:
            return True
        finally:
            self.close_connection(conn, cursor)

    def add(self, sql, exception_callfunc=None):
        """
            单条 传入sql执行插入语句
        :param sql: sql
        :param exception_callfunc: 异常回调函数
        :return: 添加行数
        """
        affect_count = None
        conn, cursor = None, None

        try:
            conn, cursor = self.get_connection()
            affect_count = cursor.execute(sql)
            conn.commit()

        except Exception as e:
            log.error(
                """
                error:%s
                sql:  %s
            """
                % (e, sql)
            )
            if exception_callfunc:
                exception_callfunc(e)
        finally:
            self.close_connection(conn, cursor)

        return affect_count

    def add_smart(self, table, data: Dict, **kwargs):
        """
            单条 添加数据, 直接传递json格式的数据，不用拼sql
        :param table: 表
        :param data: 字典 {"xxx":"xxx"}
        :param kwargs:
        :return: 添加行数
        """
        sql = get_insert_sql(table, data, **kwargs)
        return self.add(sql)

    def add_batch(self, sql, datas: List[Dict]):
        """
            批量 添加数据
            建议配合 get_insert_batch_sql() 生成sql
            get_insert_batch_sql("user_copy1", [{"auth": 2, "id": "9", "email": "999"}]
        :param sql:
            insert ignore into `表` (字段1,字段2) values (%s, %s)
            insert into `表` (`字段1`,`字段2`,`字段3`) values (%s, %s, %s)
            这里有多少个字段，values后面就要有多少个%s
        :param datas: 列表 [{}, {}, {}]
        :return:
        """
        affect_count = None
        conn, cursor = None, None
        try:
            conn, cursor = self.get_connection()
            affect_count = cursor.executemany(sql, datas)
            conn.commit()

        except Exception as e:
            log.error(
                """
                error:%s
                sql:  %s
                """
                % (e, sql)
            )
        finally:
            self.close_connection(conn, cursor)

        return affect_count

    def add_batch_smart(self, table, datas: List[Dict], **kwargs):
        """
            批量 直接传递list格式的数据，不用拼sql
        :param table: 表名
        :param datas: 列表 [{}, {}, {}]
        :param kwargs:
        :return: 添加行数
        """
        sql, datas = get_insert_batch_sql(table, datas, **kwargs)
        return self.add_batch(sql, datas)

    def update(self, sql):
        """
            更新
        :param sql:
        :return:
        """
        conn, cursor = None, None

        try:
            conn, cursor = self.get_connection()
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            log.error(
                """
                error:%s
                sql:  %s
            """
                % (e, sql)
            )
            return False
        else:
            return True
        finally:
            self.close_connection(conn, cursor)

    def update_smart(self, table, data: Dict, condition):
        """
            更新 无需拼sql
        :param table: 表名
        :param data: 数据 {"xxx":"xxx"}
        :param condition: 更新条件 where后面的条件，如 condition='status=1'
        :return:
        """
        sql = get_update_sql(table, data, condition)
        return self.update(sql)

    def delete(self, sql):
        """
            删除
        :param sql:
        :return:
        """
        conn, cursor = None, None
        try:
            conn, cursor = self.get_connection()
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            log.error(
                """
                error:%s
                sql:  %s
            """
                % (e, sql)
            )
            return False
        else:
            return True
        finally:
            self.close_connection(conn, cursor)

    @auto_retry
    def find(self, sql, limit=0, to_json=False, conver_col=True):
        """
            查询
            无数据： 返回None或[] 取决于limit
            有数据： 如果limit=1 则返回 一条数据(字段1, 字段2) 其余返回[(字段1, 字段2),(字段1, 字段2)]
        :param sql:
        :param limit:
        :param to_json: 是否将查询结果转为json
        :param conver_col: 是否处理查询结果，如date类型转字符串，json字符串转成json。仅当to_json=True时生效
        :return:
        """
        conn, cursor = self.get_connection()

        cursor.execute(sql)

        if limit == 1:
            result = cursor.fetchone()  # 全部查出来，截取 不推荐使用
        elif limit > 1:
            result = cursor.fetchmany(limit)  # 全部查出来，截取 不推荐使用
        else:
            result = cursor.fetchall()

        if result is None:
            return result

        if to_json:
            columns = [i[0] for i in cursor.description]

            # 处理数据
            def convert(col):
                if isinstance(col, (datetime.date, datetime.time)):
                    return str(col)
                elif isinstance(col, str) and (
                        col.startswith("{") or col.startswith("[")
                ):
                    try:
                        # col = self.unescape_string(col)
                        return json.loads(col)
                    except:
                        return col
                else:
                    # col = self.unescape_string(col)
                    return col

            if limit == 1:
                if conver_col:
                    result = [convert(col) for col in result]
                result = dict(zip(columns, result))
            else:
                if conver_col:
                    result = [[convert(col) for col in row] for row in result]
                result = [dict(zip(columns, r)) for r in result]

        self.close_connection(conn, cursor)

        return result


if __name__ == '__main__':
    pass
    # mysql_db = MysqlDBPro(ip="127.0.0.1", port=3306, db="xtn_home", user_name="root", user_pass="xtn-kk")
    # sql = """insert into `user_copy1` (`id`, `email`, `auth`) values (8, '888', 2)"""
    # print(mysql_db.add(sql))
    # print(mysql_db.add_smart("user_copy1", {"id": "9", "email": "999"}))
    # sql = "insert ignore into `user_copy1` (`id`,`email`) values (%s, %s)"
    # sql, datas = get_insert_batch_sql("user_copy1", [{"auth": 2, "id": "9", "email": "999"}])
    # print(mysql_db.add_batch(sql, datas))

    # print(mysql_db.add_batch_smart("user_copy1", [{"auth": 2, "id": "9", "email": "999"},
    #                                               {"auth": 2, "id": "10", "email": "10"},
    #                                               {"id": "11", "auth": 1, "email": "11"},
    #                                               {"auth": 2, "id": "12", "email": "12"}]))

    # 更新案例
    # sql = "UPDATE user_copy1 SET status = '2', auth = 1 WHERE id = 2;"
    # print(mysql_db.update(sql))

    # 更新 无需拼接sql案例
    # print(mysql_db.update_smart("user_copy1", {"email": "123", "status": 4}, "id=22"))

    # 查询案例
    # print(mysql_db.find("select * from user_copy1 where id=11",1,True))
