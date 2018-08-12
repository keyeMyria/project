from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token

from rest_framework.routers import DefaultRouter
#用户模块的url
urlpatterns = [
    #校验手机号
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$',views.MobileCountView.as_view()),
    #校验用户名
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.UserNanmeCountView.as_view()),
    #注册
    url(r'^users/$',views.RegistUserAPI.as_view()),

    # 使用rest_framework_jwt提供了登录签发JWT的视图
    # url(r'^authorizations/$',obtain_jwt_token),
    #登录合并购物车
    url(r'^authorizations/$',views.UserAuthorizeView.as_view()),

    #用户个人中心
    url(r'^user/$',views.UserCenterView.as_view()),

    #用户添加邮箱
    url(r'^email/$',views.EmailView.as_view()),

    #验证用户邮箱
    url(r'^emails/verification/$',views.EmaiVerifyView.as_view()),

    #历史浏览记录
    url(r"^browse_histories/$",views.HistoryView.as_view())


    # # 添加获取第三方qq登录网址
    # url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
    # # 添加获取第三方QQ登录后用户的信息openid
    # # 添加绑定第三方QQ登录
    # url(r'^qq/user/$', views.QQAuthUserView.as_view())

]

router = DefaultRouter()
router.register(r'addresses',views.AdressView)

urlpatterns += router.urls
