

"""
定义分页器
：创建分页器模型类
：注册rest_framework插件
"""
from rest_framework.pagination import PageNumberPagination
#创建分页器模型类
class MYPageNumberPagination(PageNumberPagination):

    #m每页显示的数量
    page_size = 4

    #客户端可以使用这个查询参数控制页面大小
    page_size_query_params = 'page_size'
    #每页最多显示的数量
    max_page_size = 20