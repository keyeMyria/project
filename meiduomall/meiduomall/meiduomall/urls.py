"""meiduomall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
import xadmin
from meiduomall.apps import users,verifications
urlpatterns = [

    # #django自带后台
    # url(r'^admin/', admin.site.urls),

    #使用xadmin模块应用
    url(r'^xadmin/',include(xadmin.site.urls)),
    #添加用户应用模块url
    url(r'^',include('users.urls')),
    #添加验证模块url
    url(r'^',include('verifications.urls')),
    #添加第三方qq登录url
    url(r'^oauth/',include('oauth.urls')),
    #添加收货地址url
    url(r'^',include('area.urls')),
    #添加商品模块url
    url(r'^',include('goods.urls')),
    #添加广告数据模块
    url(r'^',include('contents.urls')),
    #添加购物车url
    url(r'^',include('carts.urls')),

    #富文本编辑器　上传url

    url(r'^ckeditor/', include('ckeditor_uploader.urls')),

    #订单url
    url(r'^',include('order.urls')),

    #payment
    url(r'^',include('payment.urls')),


]
