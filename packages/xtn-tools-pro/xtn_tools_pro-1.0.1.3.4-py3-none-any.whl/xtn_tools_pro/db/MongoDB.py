#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    MongoDBPro
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2024/4/17    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
from urllib import parse
from typing import List, Dict, Optional
from xtn_tools_pro.utils.time_utils import *
from pymongo import MongoClient as _MongoClient
from pymongo.database import Database as _Database
from pymongo.collection import Collection as _Collection
from pymongo.errors import DuplicateKeyError, BulkWriteError


class MongoDBPro:
    def __init__(self, ip=None, port=None, db=None, user_name=None, user_pass=None, url=None, **kwargs):
        if url:
            self.client = _MongoClient(url, **kwargs)
        else:
            self.client = _MongoClient(host=ip,
                                       port=port,
                                       username=user_name,
                                       password=user_pass,
                                       authSource=db)

        self.db = self.get_database(db)

    @classmethod
    def from_url(cls, url, **kwargs):
        url_parsed = parse.urlparse(url)
        # 获取 URL的协议
        db_type = url_parsed.scheme.strip()
        if db_type != "mongodb":
            raise Exception(
                "url error, expect mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]], but get {}".format(
                    url
                ))
        return cls(url=url, **kwargs)

    def close(self):
        """
            关闭数据库
        :return:
        """
        self.client.close()

    def get_database(self, database, **kwargs) -> _Database:
        """
            根据db名获取数据库对象
        """
        return self.client.get_database(database, **kwargs)

    def get_collection(self, coll_name, **kwargs) -> _Collection:
        """
            根据集合名获取集合对象
        """
        return self.db.get_collection(coll_name, **kwargs)

    def run_command(self, command: Dict):
        """
            参考文档 https://www.geek-book.com/src/docs/mongodb/mongodb/docs.mongodb.com/manual/reference/command/index.html
        """
        return self.db.command(command)

    def find(self, coll_name: str, condition: Optional[Dict] = None,
             limit: int = 0, **kwargs) -> List[Dict]:
        """
            find
            coll_name:集合名称
            condition:查询条件 例如：{"name": "John"}、{"_id": "xxxxx"}
        """
        condition = {} if condition is None else condition
        command = {"find": coll_name, "filter": condition, "limit": limit}
        command.update(kwargs)
        result = self.run_command(command)
        cursor = result["cursor"]
        cursor_id = cursor["id"]
        while True:
            for document in cursor.get("nextBatch", cursor.get("firstBatch", [])):
                # 处理数据
                yield document
            if cursor_id == 0:
                # 游标已经完全遍历，没有剩余的结果可供获取
                # 游标的生命周期已经结束，例如在查询会话结束后。
                # 游标被显式地关闭，例如使用 db.killCursor() 命令关闭游标。
                break
            result = self.run_command(
                {
                    "getMore": cursor_id,  # 类似于mongo命令行中的it命令，通过索引id用于获取下一批结果
                    "collection": coll_name,
                    "batchSize": kwargs.get("batchSize", 100),
                }
            )
            # 覆盖原来的参数
            cursor = result["cursor"]
            cursor_id = cursor["id"]
            # print("下一批获取")

    def add_data_one(self, coll_name: str, data: Dict, insert_ignore=False,
                     is_add_create_time=False,
                     is_add_create_time_field_name="create_dt"):
        """
            添加单条数据
            coll_name: 集合名
            data: 单条数据
            insert_ignore: 索引冲突是否忽略 默认False
            is_add_create_time: 是否在数据中添加一个创建数据10时间戳字段 默认False不创建
            is_add_create_time_field_name: 自定义创建数据时间戳字段名：默认：create_dt
        Returns: 插入成功的行数
        """
        if is_add_create_time:
            data[is_add_create_time_field_name] = get_time_now_timestamp(is_time_10=True)
        collection = self.get_collection(coll_name)
        try:
            collection.insert_one(data)
        except DuplicateKeyError as e:
            if not insert_ignore:
                raise e
            return 0
        return 1

    def find_id_is_exist(self, coll_name, _id):
        """
            根据id查询id是否存在
        :param _id:id
        :return: 存在返回True 否则False
        """
        condition = {"_id": _id}
        status = list(self.find(coll_name, condition))
        if status:
            return True
        return False


if __name__ == '__main__':
    pass
    # mongo_db = MongoDBPro("127.0.0.1", 27017, "spider_pro")
    # # mongo_db.add_data_one("test", {"_id": "1", "data": "aaa"})
    # print(mongo_db.find_id_is_exist("test", "1"))
    # print(mongo_db.find_id_is_exist("test", "11"))
