"""
创建QQ登录辅助工具类
"""
#导入配置信息
from django.conf import settings
#导入urllib模块　
from urllib.parse import urlencode,parse_qs
from urllib.request import urlopen
import json
from .token import serializer
class OAuthQQ(object):
    """QQ登录辅助工具类"""

    # def __init__(self,client_id=None,client_secret=None,redirect_uri=None,state=None):
    #     self.client_id = client_id or settings.QQ_CLIENT_ID
    #     self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
    #     self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
    #     self.state = state or settings.QQ_STAT

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None,scope=None):
        self.client_id = client_id or settings.QQ_CLIENT_ID
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE  # 用于保存登录成功后的跳转页面路径
        self.scope = scope or settings.QQ_SCOPE


    #获取QQ登录的login_url
    def get_authqq_login_url(self):
        """
        获取qq登录网址
        :return:login_url
        """
        #请求参数
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            'scope': 'get_user_info',
        }
        #拼接请求第三方qq登录的url　返回qq登录网址
        #urlencode()方法将字段数据转换成查询字符串
        url = 'https://graph.qq.com/oauth2.0/authorize?' +urlencode(params)

        return url


    #根据code请求第三方qq服务器获取access_token值
    def get_access_token(self,code):
        """
        通过用户在第三qq登录返回的code信息 请求第三方qq服务器获取access_token值
        返回access_token
        """
        #请求第三方qq服务器
        url = 'https://graph.qq.com/oauth2.0/token?'
        #请求参数
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        #拼接第三方qq服务器请求url
        access_token_url = 'https://graph.qq.com/oauth2.0/token?' + urlencode(params)
        #使用urllib模块的request　请求第三方qq服务器　拿到返回值access_token
        response = urlopen(access_token_url)

        #解析urlopen()响应数据
        response_str = response.read().decode()
        #parse_qs()将字符串字典转换成字典
        response_dict = parse_qs(response_str)

        #获取access_token
        access_token = response_dict.get('access_token',None)

        #判断是否获取到access_token
        if not access_token:
            return None

        return access_token[0]

    def get_openid(self,access_token):
        """请求第三方qq服务器获取用户的openid 信息"""


        # 请求第三方qq服务器
        # 拼接第三方qq服务器请求url
        openid_url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token

        # 使用urllib模块的request　请求第三方qq服务器　拿到返回值access_token
        response = urlopen(openid_url)
        #解析urlopen()响应数据
        response_str = response.read().decode()
        #获取openid

        try:
            data = json.loads(response_str[10:-4])
            # print(data)
        except:
            return None

        openid = data.get('openid',None)

        return openid


    #为用户第一次使用qq登录生成token信息
    def get_oauth_qq_user_token(self,openid):
        """
        用户第一次通过第三方qq登录绑定用户信息并返回用户登录的token
        """
        #封装数据
        data = {
            'openid':openid
        }
        #加密数据 加密后的数据为byte类型
        secret_data = serializer.dumps(data)

        return secret_data.decode()

    #创建校验access_token函数
    def check_accsess_token(self,acces_token):
        """校验access_token"""
        data= serializer.loads(acces_token)
        # 解密access_token
        #能获取到原来加密的openid
        openid = data.get('openid')
        return openid

    #根据openid获取qq用户的用户名和性别
    def get_qq_user_info(self,access_token,opendid):
        #请求qq服务器获取qq用户信息
        print('1',access_token)
        print('2',opendid)
        print('3',self.client_id)
        base_url = 'https://graph.qq.com/user/get_user_info?'
        #请求url

        params = {
            "access_token":access_token,
            "oauth_consumer_key":self.client_id,
            "openid":opendid
        }
        url = base_url + urlencode(params)
        response = urlopen(url)
        #获取信息字典
        # resp_data = json.loads(response.read().decode())

        print(response)

        return response