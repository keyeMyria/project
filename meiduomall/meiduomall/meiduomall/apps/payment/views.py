from django.shortcuts import render

# Create your views here.
"""
支付宝第三方支付
点击支付跳转到支付宝支付页面
支付成功后返回回调域和支付流水号和订单号
获取用户支付成功后支付宝返回的支付流水号和订单号　调用支付验证用户是否支付成功
接口设计
请求方式：get
请求参数：order_id
接口url：/orders/(?P<order_id>\d+)/payment/
返回响应：alipay_url
"""
from rest_framework.views import APIView
from order.models import OrderInfo
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from alipay import AliPay
from django.conf import settings
import os
from .models import Payment
class PayStatusView(APIView):
    """第三方支付"""
    """
    接收用户支付请求，响应第三方支付平台网址
    用户在支付宝服务器支付完后，支付宝服务器通过回调域把用户的支付流水号和订单返回
    或取支付宝回调域里的支付流水号和订单号　校验用户是否支付成功
    成功则创建支付信息
    """

    #权限验证　用户必须登录
    permission_classes = [IsAuthenticated]

    #用户支付业务逻辑函数
    def get(self,request,order_id):

        #获取请求参数：
        user = request.user
        order_id = order_id

        #校验订单信息是否正确
        try:
            order = OrderInfo.objects.get(
                order_id=order_id, user=request.user,
                pay_method=OrderInfo.PAY_METHODS_ENUM["ALIPAY"],
                status=OrderInfo.ORDER_STATUS_ENUM["UNPAID"]
            )
        except OrderInfo.DoesNotExist:
            return Response({'message': '订单信息有误'}, status=status.HTTP_400_BAD_REQUEST)

        #返回第三方支付网址
        #创建支付宝应用
        alipay_client = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url= None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        #传给支付宝的参数
        order_string = alipay_client.api_alipay_trade_page_pay(
            #d当单号
            out_trade_no=order_id,
            #总金额
            total_amount=str(order.total_amount),
            subject="美多商城%s" % order_id,
            return_url="http://www.meiduo.site:8080/pay_success.html",
        )
        #支付宝支付url
        alipay_url = settings.ALIPAY_URL + "?" + order_string

        return Response({'alipay_url': alipay_url})


"""
用户在支付宝服务器支付成功后支付宝返回重定向url和回调参数
回调参数中携带着用户订单在支付宝的支付信息:订单号，流水号等等
前端请求接口　
通过document.location.search从当前页面的地址的参数中提取出指定的参数值
获取回调网址的回调参数　使用支付宝sdk的verfy()验证用户是否支付成功
数据库保存用户支付信息

"""
class PaymentSaveView(APIView):
    """
    支付结果
    """
    #支付成功后的回调域请求业务逻辑
    #pay_success.html%EF%BC%8C%E5%B9%B6%E6%90%BA%
    def put(self, request):

        #获取请求参数
        data = request.query_params.dict()
        #获取验签
        signature = data.pop("sign")

        alipay_client = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            #__file__表示当前文件路径
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        #verify(data,signature)　后台校验支付宝回调参数　
        # data用户在支付宝支付后的参数，signature验签
        success = alipay_client.verify(data, signature)
        if success:
            # 订单编号
            order_id = data.get('out_trade_no')
            # 支付宝支付流水号
            trade_id = data.get('trade_no')
            #创建支付信息
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )
            #修改订单状态
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])
            return Response({'trade_id': trade_id})
        else:
            return Response({'message': '非法请求'}, status=status.HTTP_403_FORBIDDEN)



