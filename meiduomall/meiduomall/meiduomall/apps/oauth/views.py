from django.shortcuts import render

# Create your views here.


"""
登录：
接口设计
验证数据登录　为登录成功的用户响应jwt　
保持登录　验证前端将签发的JWT的token值　rest_framework_jwt会自动解码前端jwt的token值

Django REST framework JWT提供了登录签发JWT的obtain_jwt_token视图为用户登录成功后签发jwt-token值　
并返回响应jwt-token值　重写JWT的obtain_jwt_token视图的jwt_response_payload_handler方法　
返回响应　user_id,username,token

django自带的认证系统的后端的authenticate方法会自动验证用户登录(验证用户名和密码)
　重写authenticate方法增加使用用户手机号码也可以登录

请求方式：post表单提交
接口url:/authorizations/
接收参数：username,password
返回响应：json user_id,username,token

"""

#创建登录类视图
# Django REST framework JWT提供了登录签发JWT的视图　obtain_jwt_token
#但是jwt_response_payload_handler默认的返回值仅有token
#需要重写jwt_response_payload_handler　拿到user_id,username


"""
第三方QQ登录
：前端页面设置QQ登录按钮
：用户点击QQ登录跳转到第三方QQ登录页面
：用户在第三方QQ页面登录后，通过回调域返回登录的code信息
：获取code信息到第三方QQ服务器中请求access_token
：根据access_token信息到第三方QQ服务器请求用户的openid
    ：根据返回的用户的openid解析用户的信息　拿到用户的openid
        ：查询数据库用户和QQ关联的表判断用户是否是第一次登录
            ：如果之前绑定过获取用户信息　用户直接登录商城
            ：如果没有绑定过，绑定用户信息和QQ　才能商城
"""

"""
第三方QQ登录视图：
前端页面设置QQ登录按钮
用户点击QQ登录跳转到第三方QQ登录页面
接口设计：/oauth/qq/authorization/?next=xxx
请求方式：get
请求参数：next 查询字符串
返回响应：json login_url第三方QQ登录页面

"""
from rest_framework.views import APIView
#导入QQ登录辅助工具类
from .utils import OAuthQQ


# 获取第三方qq登录网址
class QQAuthURLView(APIView):
    """QQ登录视图"""

    #定义get请求的业务处理函数
    def get(self,request):
        #接收请求数据

        next = request.query_params.get('next')
        print(next)

        #封装响应数据
        oauthqq = OAuthQQ(state=next)

        #获取访问第三方qq的网址
        login_url = oauthqq.get_authqq_login_url()

        #返回响应数据
        return  Response({'login_url':login_url})


"""
接口设计：
用户在QQ登录成功后，QQ会将用户重定向回我们配置的回调callback网址
获取回调callback传回的用户登录qq的信息，请求第三方qq服务器获取access_token值
根据返回的access_token值请求第三qq服务器获取用户的openid信息
查询数据库的用户和qq登录关联表判断是否有登录过
接口url: /oauth/qq/user/?code=xxx
请求方式：get
请求参数：code
返回响应：json access_token token user_id uername
"""
from rest_framework import status
from .models import OAuthQQModel
from rest_framework_jwt.settings import api_settings
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from .serializers import OAuthQQModelSerializer
from .exceptions import QQAPIException
import logging
from carts.utils import minxiusercart


#创建日志对象 加载配置日志记录器
loger = logging.getLogger('django')


#获取accsess_token视图
# class QQAuthUserView(APIView):
class QQAuthUserView(CreateAPIView):
    """
    获取qq登录用户信息
    """
    #指定序列化器
    serializer_class = OAuthQQModelSerializer   #createAPIView封装post请求的对应的业务处理函数

    #定义get请求处理业务函数
    def get(self,request):

        #获取请求数据
        code = request.query_params.get('code')
        print(code)
        #校验请求数据
        if not code :
            return Response({'message':'没有code信息'},status=status.HTTP_400_BAD_REQUEST)

        #处理业务
        """
        获取回调callback传回的用户登录qq的信息，
        请求第三方qq服务器获取access_token值
        根据返回的access_token值请求第三qq服务器获取用户的openid信息
        查询数据库的用户和qq登录关联表判断是否有登录过
        """
        try:
            #取access_token值
            oauth = OAuthQQ()

            access_token = oauth.get_access_token(code)

            #获取用户在qq登录过的openid
            # 查询数据库用户和QQ关联表　看是否有该用户
            openid = oauth.get_openid(access_token)

            #自定义的异常类　需要手动抛出异常
            # if not all([access_token,openid]):
                # raise(QQAPIException('qq服务器错误'))
        except QQAPIException :
            # print(err)
            return Response({'message':'没有openid信息'},status=status.HTTP_503_SERVICE_UNAVAILABLE)

        #查询数据库判断用户是否存在
        try:
            qq_user = OAuthQQModel.objects.get(openid=openid)
            # if not qq_user:
                # raise(QQAPIException('第一次使用qq登录'))
        except :
            #如果用户第一次登录
            #绑定用户信息 并返回qq用户登录的信息加密的token值
            token = oauth.get_oauth_qq_user_token(openid)
            return Response({'access_token':token})

        else:
            #用户之前登录过
            #获取用户登录的信息和jwt-token值
            user = qq_user.user

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)


        #返回响应数据
        data = {
            'username':user.username,
            'user_id':user.id,
            'token':token

        }
        #合并购物车
        resp = Response(data=data)
        response = minxiusercart(request,user,resp)

        return response

    #重写qq登录绑定接口，在qq用户绑定登录后合并用户购物车
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response = minxiusercart(request,self.user,response)

        return response


"""
使用第三方QQ登录
接口设计
请求方式：post表单请求
接口url:/oauth/qq/user/
接收参数：mobile sms_code password access_token
返回响应：json token id username
"""
# from rest_framework.generics import CreateAPIView
# from .serialzers import OAuthQQModelSerializer
# class QQAuthUserView(CreateAPIView):
#     """QQ登录"""
#
#     #指定序列化器
#     serializer_class = OAuthQQModelSerializer