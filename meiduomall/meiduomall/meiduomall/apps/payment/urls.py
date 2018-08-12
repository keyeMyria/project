from django.conf.urls import url
from . import views

urlpatterns = [
    #支付连接
    url(r'^orders/(?P<order_id>\d+)/payment/$',views.PayStatusView.as_view()),
    #保存支付订单

    # 获取支付成功后直翻返回来的数据
    url(r'^ /payment/status/$',views.PaymentSaveView.as_view())
]