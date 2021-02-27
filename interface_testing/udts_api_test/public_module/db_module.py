# -*- coding:utf-8 -*-
"""
数据库操作模块
For MongoDB
"""

import pymongo
from interface_testing.udts_api_test.public_module.logger_module import logger


class MongoDB(object):

    def __init__(self, database_name, collection_name, host='localhost', port=27017):
        """
        初始化mongodb连接
        :param database_name: 初始数据库名
        :param collection_name: 初始集合名
        :param host: 主机名
        :param port: 端口
        """
        self.client = pymongo.MongoClient(host=host, port=port)
        self.database = self.client[database_name]
        self.collection = self.database[collection_name]

    def __del__(self):
        """程序结束后，自动关闭连接，释放资源"""
        self.client.close()

    def build_collection(self, database_name, collection_name):
        """
        构建数据库和集合
        :param database_name: 数据库名
        :param collection_name: 集合名
        :return: 返回集合句柄
        """
        database = self.client[database_name]
        collection = database[collection_name]
        logger.debug('构建MongoDB数据库 --> database: {}, collection: {}'.format(database_name, collection_name))
        return collection

    def insert_data(self, data, collection=None, do_many=False):
        """
        插入数据到集合
        :param data: 数据
        :param collection: 集合名
        :param do_many: 是否插入多行数据，默认False
        :return:
        """
        collection = collection or self.collection
        if do_many:
            if isinstance(data, list):
                collection.insert_many(data)
        else:
            collection.insert_one(data)

    def delete_data(self, collection=None, data={}, do_many=False):
        """
        删除集合内的指定数据
        :param collection: 集合名
        :param data: 数据
        :param do_many: 是否删除多行数据，默认False
        :return: 返回删除个数
        """
        collection = collection or self.collection
        if do_many:
            data = collection.delete_many(data)
        else:
            data = collection.delete_one(data)
        return data.deleted_count

    def update_data(self, collection=None, data={}, update_format={}, do_many=False, upsert=False):
        """
        更新集合数据
        :param collection: 集合名
        :param data: 数据
        :param update_format: 更新的格式
        :param do_many: 是否更新多行数据，默认False
        :param upsert: 是否更新匹配到的字段值，默认False
        :return: 返回更新个数
        """
        collection = collection or self.collection
        if do_many:
            data = collection.update_many(data, update_format, upsert=upsert)
        else:
            data = collection.update_one(data, update_format, upsert=upsert)
        return result.matched_count

    def query_data(self, collection=None, condition={}, use_find=False):
        """
        查询集合内的数据
        :param collection: 集合名
        :param condition: 查询条件
        :param use_find: 是否使用find查询，默认False
        :return:
        """
        collection = collection or self.collection
        if use_find:
            if condition:
                data = list(collection.find(condition))
            else:
                data = list(collection.find())  # 查询所有数据

            if data:
                for each in data:
                    del each['_id']  # 删除不需要的"_id"值
        else:
            data = collection.find_one(condition)
            del data['_id']  # 删除不需要的"_id"值

        return data

    def counter(self, collection=None, data={}):
        """
        查询集合内的指定字段个数
        :param collection:
        :param data:
        :return:
        """
        collection = collection or self.collection
        return collection.count_documents(data)


if __name__ == '__main__':
    # 测试MongoDB
    mongo = MongoDB(database_name='proxy_info', collection_name='all_proxy_ip')
    result = mongo.query_data(use_find=True)
    print(result)
    print(len(result))
    # 切换集合
    valid_proxy_ip = mongo.build_collection(database_name='proxy_info', collection_name='valid_proxy_ip')
    result = mongo.query_data(collection=valid_proxy_ip, use_find=True)
    print(result)
    print(len(result))
