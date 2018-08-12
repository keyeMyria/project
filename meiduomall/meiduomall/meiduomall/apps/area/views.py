from django.shortcuts import render

# Create your views here.



"""
收货地址
接口设计：
点击收货地址按钮返回所有省份信息
点击省份下拉选项获取所有信息
请求方式：get
请求接口url:/areas/
请求参数：无参数表示获取省份信息，带参数或取省的所有信息
返回参数：json

ReadOnlyModelViewSet继承了RetrieveModelMixin和ListModelMixin
ReadOnlyModelViewSet视图集封装了获取单个信息或者所有信息
通过action动作判断请求的是请求单个数据函数多个数据
"""
from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import AreaPrSerilizer,AreaMoreSerializer
from .models import Area
from rest_framework_extensions.mixins import CacheResponseMixin
#收货地址
class AreasViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    """收货地址"""

    #指定序列化器
    serializer_class = None
    queryset = None
    pagination_class = None

    """
    通过重写获取序列化器的方法来动态选择序列化器
    通过不同的序列化器来序列化获取请求单个数据和所有信息
    """

    #根据请求的的动作不同获取不同的数据集
    def get_queryset(self):
        """
        默认的get_queryset 返回的是all()
        根据请求的方法的动作不同选择不同的数据集
        """
        if self.action == 'list':
            print('>>>')
            return Area.objects.filter(parent=None)
        if self.action == 'retrieve':
            print('....')
            print(Area.objects.all())
            return Area.objects.all()


    #根据请求的动作不选择不同的序列化器 动态的选择序列化器
    def get_serializer_class(self):
        """重写选择序列化器方法"""

        #如果请求是查询省份下数的所有信息　返货AreaPrSerilizer
        if self.action == 'list':
            return AreaPrSerilizer
        else:
            #请求省份信息
            return AreaMoreSerializer



