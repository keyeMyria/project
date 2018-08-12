"""
重写jwt_response_payload_handler的返回值
重写过jwt_response_payload_handler方法需要在重载JWT_AUTH配置
"""

def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


"""
增加：用户名和手机号码都能登录成功
通过修改Django认证系统的认证后端（主要是authenticate方法）
来支持登录账号既可以是用户名也可以是手机号。
"""
import re
from .models import User
def get_user_by_account(account):
    """
    根据帐号获取user对象
     account: 账号，可以是用户名，也可以是手机号
     User对象 或者 None
    """
    try:
        if re.match('^1[3-9]\d{9}$', account):
            # 帐号为手机号
            user = User.objects.get(mobile=account)
        else:
            # 帐号为用户名
            user = User.objects.get(username=account)

    #如果用户不存在用户模型类会自动抛出DoesNotExist
    except User.DoesNotExist:
        return None
    else:
        return user



"""
重新指定Django的用户认证系统的后端类
重写Django认证系统的认证后端（主要是authenticate方法）
来支持登录账号既可以是用户名也可以是手机号。
需要重载django的认证系统后端
"""
from django.contrib.auth.backends import ModelBackend

class UsernameMobileAuthBackEnd(ModelBackend):

    #重写authenticate方法增加支持使用手机号登录
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        return user


    # def authenticate(self, request, username=None, password=None, **kwargs):
    #     return super().authenticate(request, username, password, **kwargs)


# """
# 创建QQ登录辅助工具类
# """
# #导入配置信息
# from django.conf import settings
# #导入urllib模块　
# from urllib.parse import urlencode,parse_qs
# from urllib.request import urlopen
# import json
# from .token import serializer
# class OAuthQQ(object):
#     """QQ登录辅助工具类"""
#
#     def __init__(self,client_id=None,client_secret=None,redirect_uri=None,state=None):
#         self.client_id = client_id or settings.QQ_CLIENT_ID
#         self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
#         self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
#         self.state = state or settings.QQ_STAT
#
#
#     #获取QQ登录的login_url
#     def get_authqq_login_url(self):
#         """
#         获取qq登录网址
#         :return:login_url
#         """
#         #请求参数
#         params = {
#             'response_type': 'code',
#             'client_id': self.client_id,
#             'redirect_uri': self.redirect_uri,
#             'state': self.state,
#             'scope': 'get_user_info',
#         }
#         #拼接请求第三方qq登录的url　返回qq登录网址
#         #urlencode()方法将字段数据转换成查询字符串
#         url = 'https://graph.qq.com/oauth2.0/authorize?' +urlencode(params)
#
#         return url
#
#
#     #根据code请求第三方qq服务器获取access_token值
#     def get_access_token(self,code):
#         """
#         通过用户在第三qq登录返回的code信息 请求第三方qq服务器获取access_token值
#         返回access_token
#         """
#         #请求第三方qq服务器
#         url = 'https://graph.qq.com/oauth2.0/token?'
#         #请求参数
#         params = {
#             'grant_type': 'authorization_code',
#             'client_id': self.client_id,
#             'client_secret': self.client_secret,
#             'code': code,
#             'redirect_uri': self.redirect_uri
#         }
#         #拼接第三方qq服务器请求url
#         access_token_url = url + urlopen(params)
#         #使用urllib模块的request　请求第三方qq服务器　拿到返回值access_token
#         response = urlopen(access_token_url)
#
#         #解析urlopen()响应数据
#         response_str = response.read().decode()
#         #parse_qs()将字符串字典转换成字典
#         response_dict = parse_qs(response_str)
#
#         #获取access_token
#         access_token = response_dict.get('access_token')
#
#         #判断是否获取到access_token
#         if not access_token:
#             return None
#
#         return access_token
#
#     def get_openid(self,access_token):
#         """请求第三方qq服务器获取用户的openid 信息"""
#
#
#         # 请求第三方qq服务器
#         url = 'https://graph.qq.com/oauth2.0/me?access_token='
#         # 请求参数
#         params = access_token
#         # 拼接第三方qq服务器请求url
#         openid_url = url + access_token
#
#         # 使用urllib模块的request　请求第三方qq服务器　拿到返回值access_token
#         response = urlopen(openid_url)
#         #解析urlopen()响应数据
#         response_str = response.read().decode()
#         #获取openid
#         try:
#             data = json.loads(response_str[10:-4])
#         except:
#             return None
#         else:
#             openid = data.get('openid',None)
#         return openid
#
#
#     #为用户第一次使用qq登录生成token信息
#     def get_oauth_qq_user_token(self,openid):
#         """
#         用户第一次通过第三方qq登录绑定用户信息并返回用户登录的token
#         """
#         #封装数据
#         data = {
#             'openid':openid
#         }
#         #加密数据 加密后的数据为byte类型
#         secret_data = serializer.dumps(data)
#
#         return secret_data.decode()
#
#     #创建校验access_token函数
#     def check_accsess_token(self,acces_token):
#         """校验access_token"""
#         #能获取到openid 就代表access_token是有效的
#         openid = self.get_openid(acces_token)
#         return openid



""""""