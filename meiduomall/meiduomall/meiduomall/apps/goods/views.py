from django.shortcuts import render

# Create your views here.
"""
展示商品列表信息
需要对商品数据进行分页支持，并且可以按照创建时间（默认）、价格、销量（人气）进行排序
分类查询商品数据　将类别下所有在在售的信息全部查询出来分页显示

请求方式:get
接口url:/categories/(?P<category_id>\d+)/skus
请求参数：商品分类id 前端传过来
返回响应：商品类别下的所有信息　id name price comments default_image_url
"""

from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView,GenericAPIView
from .serializers import SKUSerializer
from .models import SKU

class SKUListView(ListAPIView,GenericAPIView):
    """商品列表展示"""

    """
    获取分类id 查询类别下所有的商品　
    按照创建时间/价格/人气过滤条件分页展示

    REST framework提供了对于排序的支持，使用REST framework提供的OrderingFilter过滤器后端即可。
    OrderingFilter过滤器要使用ordering_fields 属性来指明可以进行排序的字段有哪些
    """

    #指定rest_framework排序后端
    filter_backends = (OrderingFilter,)
    #排序字段
    ordering_fields = ('create_time', 'price', 'sales')

    #指定序列化器
    serializer_class = SKUSerializer


    #获取查询集
    #重写获取查询数据集　查询类别下所有在售商品信息 所以需要重写
    def get_queryset(self):

        #获取分类id
        category_id = self.kwargs.get('category_id')
        #获取类别下所有商品
        queryset = SKU.objects.filter(category_id=category_id, is_launched=True)
        # print(queryset)
        return queryset



#drf-haystack是为了在REST framework中使用haystack而进行的封装
from drf_haystack.viewsets import HaystackViewSet
from .serializers import SKUIndexSerializer

class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer





