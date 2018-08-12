from _decimal import Decimal

from django.shortcuts import render

# Create your views here.
"""
点击结算　跳转到订单详情页面
展示勾选商品的订单号　sku　数量 支付方式
接口设计
请求方式：get
接口url:/order/settlement/
请求参数：sku_id
返回响应：json 显示订单号 商品信息 支付方式
"""
from django_redis import get_redis_connection
from rest_framework.views import APIView
from .serializers import OrderSKUserializer,OrderSettlementSerializer
from rest_framework.permissions import IsAuthenticated
from goods.models import SKU
from rest_framework.response import Response

#订单详情页面
class OrderSettlementView(APIView):
    """订单页面"""

    #权限校验　必须登录
    permission_classes = [IsAuthenticated]

    def get(self,request):
        """
        提交订单额商品在redis中是被勾选的
        从redis中取出被勾选的商品
        序列化校验
        返回响应
        :param request:
        :return:
        """
        #获取请求参数
        user = request.user
        #获取用户redis中被勾选的商品
        conn = get_redis_connection('cart')

        #获取商品id 和数量
        redis_cart = conn.hgetall('cart_%s'%user.id)
        print(redis_cart)

        #获取勾选商品
        cart_selected = conn.smembers('cart_selected_%s'%user.id)
        print(cart_selected)


        cart_sku = {}
        for sku_id in cart_selected:
            print(sku_id)
            # {'sku_id':count }
            cart_sku[int(sku_id)] = int(redis_cart[sku_id])
            # cart[int(sku_id)] = int(redis_cart[sku_id])


        #查询商品
        skus = SKU.objects.filter(id__in=cart_sku.keys())
        for sku in skus:
            sku.count = cart_sku[sku.id]

        print(skus)
        #运费
        freight = Decimal('10.00')

        #反序列化数据
        data = {'freight':freight,'skus':skus}

        #反序列化
        ser = OrderSettlementSerializer(data)

        #返回响应 返回序列化后的数据
        return Response(ser.data)

"""
保存订单
点击保存订单，后台接收请求，获取当前用户
获取用户购物车勾选商品id ,校验商品库存，创建订单号，
返回订单号，订单总价
接口设计：
请求方式：post
请求参数：address,paymethod
接口url:/orders/
返回响应：json 订单号，订单总价
"""
from rest_framework.generics import CreateAPIView
from .serializers import SaveOrderSerializer
#保存订单页面视图
class SaveOrderView(CreateAPIView):
    """保存订单"""

    #校验用户是否登录
    permission_classes = [IsAuthenticated]

    #订单保存序列化器
    serializer_class = SaveOrderSerializer





