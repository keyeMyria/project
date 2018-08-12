

"""
数据主从读写分离
分配数据库主从服务器的权限
主服务器写入(增删改)
从服务器读取数据(查)
"""


class MasterSlaveDBRouter(object):
    """数据库主从读写分离路由"""

    #数据库读写分离　写入(增删改)服务器属性选择函数
    def db_for_read(self, model, **hints):
        """读数据库"""
        return "slave"

    # 数据库读写分离　读取(查询)服务器属性选择函数
    def db_for_write(self, model, **hints):
        """写数据库"""
        return "default"

    #主从服务器关联属性
    def allow_relation(self, obj1, obj2, **hints):
        """是否运行关联操作"""
        return True