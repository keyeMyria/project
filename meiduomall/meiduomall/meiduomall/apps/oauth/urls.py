from django.conf.urls import url
from . import views


urlpatterns = [

    # 添加获取第三方qq登录网址
    url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
    # 添加获取第三方QQ登录后用户的信息openid
    # 添加绑定第三方QQ登录
    url(r'^qq/user/$', views.QQAuthUserView.as_view())
]
