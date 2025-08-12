import json
from app.models.base import redis_db_01


class UserDB:
    @staticmethod
    def get_user_info(user_name):
        """
            根据用户名获取结果
        :param order_id:
        :return:
        """
        key = f"user:{user_name}"
        user_info = redis_db_01.get(key)
        if user_info:
            return True
        return False
