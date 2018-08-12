from django.shortcuts import render

# Create your views here.

"""
判断用户名是否已经注册过
业务逻辑：根据请求查询数据库查询用户　返回json数据
{'username':username,'conut':count}
前端根据返回数据判断用户是否已经注册过
接口设计：/^usernames/(?P<username>\w{5,20})/$
请求方式:get
请求参数:username
响应：json
"""
from rest_framework.views import APIView
from .models import User
from rest_framework.response import Response
#创建判断用户名是否已经注册过类视图
class UserNanmeCountView(APIView):
    """判断用户名是否注册过"""

    #定义请求业务处理函数
    def get(self,request,username):
        #获取请求参数，查询数据库看是否有该用户名
        count = User.objects.filter(username=username).count()

        #封装返回数据
        data = {
            'username':username,
            'count':count
        }

        #返回请求
        return Response(data)


"""
判断手机号码是否已经注册过
业务逻辑：根据请求查询数据库查询用户　返回json数据
{'mobile':mobile,'conut':count}
使用jwt机制代替session　来辨别用户 后台生成token值写入响应数据中返回给客户端

前端根据返回数据判断用户是否已经注册过
接口设计：/^mobiles/(?P<mobile>1[3-9]{9})/$
请求方式:get
请求参数:mobile
响应：json
"""
#创建判断手机号码是否已经注册过类视图
class MobileCountView(APIView):
    """判断手机号码是否注册过"""

    # 定义请求业务处理函数
    def get(self, request, mobile):
        # 获取请求参数，查询数据库看是否有该手机号码
        count = User.objects.filter(mobile=mobile).count()

        # 封装返回数据
        data = {
            'mobile': mobile,
            'count': count
        }

        # 返回请求
        return Response(data)


"""
注册
点击注册按钮提交注册信息，后端接收请求，验证数据，保存到数据库并返回用户数据
接口设计
请求方式: post表单请求
请求接口url：/users/
请求参数：username,moblie,password,password2,sms_code,allow
响应数据：json 用户id 用户名　手机号
"""
from rest_framework.generics import CreateAPIView
from .serialzers import UserModelSerialzer
#CreateAPIView类封装了　post请求对应的create方法将数据校验并保存到数据
#创建注册类视图
class RegistUserAPI(CreateAPIView):
    """注册"""

    #指定序列化器
    serializer_class = UserModelSerialzer



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


# """
# 第三方QQ登录
# ：前端页面设置QQ登录按钮
# ：用户点击QQ登录跳转到第三方QQ登录页面
# ：用户在第三方QQ页面登录后，通过回调域返回登录的code信息
# ：获取code信息到第三方QQ服务器中请求access_token
# ：根据access_token信息到第三方QQ服务器请求用户的openid
#     ：根据返回的用户的openid解析用户的信息　拿到用户的openid
#         ：查询数据库用户和QQ关联的表判断用户是否是第一次登录
#             ：如果之前绑定过获取用户信息　用户直接登录商城
#             ：如果没有绑定过，绑定用户信息和QQ　才能商城
# """
#
# """
# 第三方QQ登录视图：
# 前端页面设置QQ登录按钮
# 用户点击QQ登录跳转到第三方QQ登录页面
# 接口设计：/oauth/qq/authorization/?next=xxx
# 请求方式：get
# 请求参数：next 查询字符串
# 返回响应：json login_url第三方QQ登录页面
#
# """
# from rest_framework.views import APIView
# #导入QQ登录辅助工具类
# from .utils import OAuthQQ
#
#
# # 获取第三方qq登录网址
# class QQAuthURLView(APIView):
#     """QQ登录视图"""
#
#     #定义get请求的业务处理函数
#     def get(self,request):
#         #接收请求数据
#         next = request.query_params.get('next')
#
#         #封装响应数据
#         oauthqq = OAuthQQ(state=next)
#
#         #获取访问第三方qq的网址
#         login_url = oauthqq.get_authqq_login_url()
#
#         #返回响应数据
#         return  Response({'login_url':login_url})
#
#
# """
# 接口设计：
# 用户在QQ登录成功后，QQ会将用户重定向回我们配置的回调callback网址
# 获取回调callback传回的用户登录qq的信息，请求第三方qq服务器获取access_token值
# 根据返回的access_token值请求第三qq服务器获取用户的openid信息
# 查询数据库的用户和qq登录关联表判断是否有登录过
# 接口url: /oauth/qq/user/?code=xxx
# 请求方式：get
# 请求参数：code
# 返回响应：json access_token token user_id uername
# """
# from rest_framework import status
# from .models import OAuthQQModel
# from rest_framework_jwt.settings import api_settings
# #获取accsess_token视图
# # class QQAuthUserView(APIView):
# class QQAuthUserView(CreateAPIView):
#     """
#     获取qq登录用户信息
#     """
#
#     #定义get请求处理业务函数
#     def get(self,request):
#
#         #获取请求数据
#         code = request.query_params.get('code')
#         #校验请求数据
#         if not code :
#             return Response({'message':'没有code信息'},status=status.HTTP_400_BAD_REQUEST)
#
#         #处理业务
#         """
#         获取回调callback传回的用户登录qq的信息，
#         请求第三方qq服务器获取access_token值
#         根据返回的access_token值请求第三qq服务器获取用户的openid信息
#         查询数据库的用户和qq登录关联表判断是否有登录过
#         """
#         try:
#             #取access_token值
#             oauth = OAuthQQ()
#             access_token = oauth.get_access_token(code)
#             #获取用户在qq登录过的openid
#             openid = oauth.get_openid(access_token)
#             #查询数据库用户和QQ关联表　看是否有该用户
#         except:
#             return Response({'message':'没有openi信息'},status=status.HTTP_503_SERVICE_UNAVAILABLE)
#
#         #查询数据库判断用户是否存在
#         try:
#             qq_user = OAuthQQModel.objects.get(openid=openid)
#         except:
#             #如果用户第一次登录
#             #绑定用户信息 并返回用户登录的信息和token值
#             token = oauth.get_oauth_qq_user_token(openid)
#             return Response({'token':token})
#         else:
#             #用户之前登录过
#             #获取用户登录的信息和token值
#             user = qq_user.user
#
#             jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
#             jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
#
#             payload = jwt_payload_handler(user)
#             token = jwt_encode_handler(payload)
#
#
#         #返回响应数据
#         data = {
#             'username':user.username,
#             'user_id':user.id,
#             'token':token
#
#         }
#         return Response(data=data)
#
#
#
#
# """
# 使用第三方QQ登录
# 接口设计
# 请求方式：post表单请求
# 接口url:/oauth/qq/user/
# 接收参数：mobile sms_code password access_token
# 返回响应：json token id username
# """
# # from rest_framework.generics import CreateAPIView
# # from .serialzers import OAuthQQModelSerializer
# # class QQAuthUserView(CreateAPIView):
# #     """QQ登录"""
# #
# #     #指定序列化器
# #     serializer_class = OAuthQQModelSerializer


"""
用户中心个人信息展示：
接口设计：
用户登录后，点击用户中心请求接口　
获取显示个人信息　用户名，手机号，邮箱，邮箱激活状态
请求方式：get
请求接口url:/user/
请求参数：使用rest_framework自带的认证校验用户是否登录的组件　获取当前登录用户的信息
返回响应：json　用户名，手机号，邮箱，邮箱激活状态
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView
from .serialzers import UserDetaillSerializer
#用户个人中心
class UserCenterView(RetrieveAPIView):
    """用户个人中心"""

    # rest_framework自带的验证权限
    #验证用户是否登录
    # 如果用户登录获取请求中的用户信息
    permission_classes = [IsAuthenticated]

    #指定序列化器
    serializer_class = UserDetaillSerializer

    #重写RetrieveAPIView的get_object()方法　
    def get_object(self):

        #返回登录用户的实例对象
        return self.request.user



"""
邮箱保存和发送验证
接口设计：
点击设置邮箱，把用户设置的邮箱保存到数据库，并且给用户发送邮箱激活验证链接
请求方式：put
请求接口：/email/
请求参数：user_id,email
返回响应：json user_id email
"""
from rest_framework.generics import UpdateAPIView
from .serialzers import EmailVerifySerializer
class EmailView(UpdateAPIView):
    """保存用户邮箱和发送验证码"""

    #获取请求数据
    #校验请求数据　保存数据库
    #返回响应

    serializer_class = EmailVerifySerializer

    def get_object(self):
        return self.request.user




"""
邮箱验证
接口设计：用户点击链接验证，服务器获取链接中传来的token 信息
解密token信息查用户信息　来判断用户是否验证过邮箱
请求方式：get
请求接口url:/emails/verification/?token=xxx
请求参数：查询字符串
返回响应：json
"""
from rest_framework import status
from .models import User
class EmaiVerifyView(APIView):
    """验证邮箱"""

    """
    服务器获取链接中传来的token 信息
    解密token信息查用户信息　来判断用户是否验证过邮箱
    """

    #定义get请求的业务处理函数
    def get(self,request):

        #获取请求数据 获取查询字符串
        token = request.query_params.get('token')

        #校验请求数据
        if not token:
            return Response({'message':'缺少token'},status=status.HTTP_400_BAD_REQUEST)

        #解密token数据 获取用户
        obj = User()
        try:
            user = obj.check_token(token)
        except:     #用户不存在抛出验证邮箱无效
            return  Response({'massage':'验证无效'},status=status.HTTP_400_BAD_REQUEST)
        #邮箱验证通过，跟新用户的邮箱信息 保存数据库
        user.email_active = True
        print(user.email)
        user.save()

        return Response({'massage':'ok'},status=status.HTTP_200_OK)




"""
用户收货地址接口
接口设计：
用户添加，删除，修改，收货地址，接收用户请求数据保存数据
限制用户收货地址数量５个
请求方式：post表单
接口url:/addresses/
请求参数：表单键值对
返回响应:json

使用拓展类mixin和视图集
视图集封装的请求动作，get->list,get->retrieve,post->create,put->updata,delete->destory
mixin类封装了请求动作对应的行动 list,retrieve,create,update,destory
根据请求的动作来添加业务处理逻辑
"""
from rest_framework.viewsets import ViewSet,GenericViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin,UpdateModelMixin,ListModelMixin
from .serialzers import UserAdressSerializer,AddressTitleSerializer
from .models import Address
from rest_framework.decorators import action

class AdressView(GenericViewSet,CreateModelMixin,UpdateModelMixin):
    """用户收货地址管理"""

    queryset = Address.objects.all()
    serializer_class = UserAdressSerializer

    #权限验证，确保用户登录了才能　添加收货地址　验证请求request.user
    permissions = [IsAuthenticated]

    #重写get_queryset方法　过滤没有被删除的收货地址
    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    """请求post　添加用户地址"""
    def create(self, request, *args, **kwargs):
        """
        判断用户的收货地址数量是否已经达到上限
        :param request: 表单数据
        :param args:
        :param kwargs:
        :return: 用户地址收货地址信息
        """
        #获取当前用户
        user = request.user
        #判断当前的用的收货管理地址数量
        if user.addresses.count() > 5:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return super().create( request, *args, **kwargs)


    """查看用户所有收货地址"""
    def list(self,request,*args,**kwargs):
        """
        显示用户所有的收货地址
        :param request:
        :param args:
        :param kwargs:
        :return: 返回用户收货地址
        """
       #获取查询集　　　list 方法是获取查询集 retrieve方法是获取一个对象
        queryset = self.get_queryset()
        seriaizer = self.get_serializer(instance=queryset,many=True)
        #获取当前用户
        user = request.user

        # 由一模型类条件查询多模型类数据格式：
        #一模型类关联属性名__一模型类属性名
        return Response(
            {
                'user_id':user.id,
                'limit':5,
                'default_address_id':user.default_address_id,    #一模型类关联属性名__一模型类属性名
                'addresses':seriaizer.data    #序列化后的数据
            }
        )
    """删除－过滤逻辑删除的地址"""
    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


    """
    需要多个修改动作
    重写action　put 对应的逻辑函数
    """

    """设置默认用户收货地址"""
    @action(methods=['put'], detail=True)
    def status(self,request,pk=None):
        """
        点击设置默认按钮设置的收货地址
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        #获取当前地址对象
        address = self.get_object()
        #设置成默认收货地址
        request.user.default_address = address

        #保存修改　提交数据库
        request.user.save()

        return Response({'message':'ok'},status=status.HTTP_200_OK)


    """设置标题"""
    @action(methods=['put'], detail=True)
    def title(self,request,pk=None):

        #获取收货地址对象
        address = self.get_object()
        #反序列化　修改地址信息
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        #返回序列化的数据
        return Response(serializer.data)



"""
用户历史浏览记录
接口设计：
将用户浏览的商品id缓存到redis中，点击用户中心，前端页面自动请求接口
将用户历史浏览记录展示在个人中心页面
请求接口：/browse_histories/
请求方式：post
请求参数：sku_id
返回响应：json sku_id name price defualt_image_url
"""
from .serialzers import HistorySerialier
from django_redis import get_redis_connection
from goods.models import SKU
#导入展示浏览记录的商品序列化器
from goods.serializers import SKUSerializer
class HistoryView(CreateModelMixin,GenericAPIView):
    """历史浏览记录"""
    """
    获取浏览商品的id
    将浏览的商品id保存的redis 数据库

    点击用户中心展历史浏览的额商品
    获取登录用户信息　到redis 数据库查询用户对应的历史浏览数据
    到mysql数据库查询　用户历史浏览的商品　
    返回商品信息　
    """

    #验证用户是否登录
    permission_classes = [IsAuthenticated]
    #指定序列化器　添加历史浏览记录
    serializer_class = HistorySerialier


    #保存用户历史浏览记录
    def post(self,request):
        return self.create(request)


    #获取用户浏览记录
    def get(self,request):
        """点击用户中心展示个人的历史浏览"""
        """
        获取用户id　查询redis　用户历史浏览商品
        获取商品信息　返回
        """
        #获取登录用户信息
        user_id = request.user.id
        #连接redis
        conn = get_redis_connection('history')
        #查询
        sku_id = conn.lrange('history_%s'%user_id,0,-1)
        print(sku_id)

        sku_list = []
        #获取商品信息
        for id in sku_id:
            sku = SKU.objects.get(id=id)
            sku_list.append(sku)

        #序列化商品信息
        ser = SKUSerializer(instance=sku_list,many=True)

        data = ser.data

        return Response(data)



"""
修改登录接口
添加合并购物车功能
修改obtain_jwt_token视图 添加合并购物车
"""
from carts.utils import minxiusercart
from rest_framework_jwt.views import ObtainJSONWebToken
class UserAuthorizeView(ObtainJSONWebToken):
    """登录合并购物车"""


    def post(self, request, *args, **kwargs):

        #获取登录后返回的响应
        response = super().post(request, *args, **kwargs)

        #重写drf_jwt的登录校验 登录校验后返回用户对象　在登录校验后合并用户购物车
        seriliazer = self.get_serializer(data=request.data)
        if seriliazer.is_valid():
            user = seriliazer.validated_data.get('user')
            #用户登录校验后　合并用户购物车
            response = minxiusercart(request,user,response)

        return response


























