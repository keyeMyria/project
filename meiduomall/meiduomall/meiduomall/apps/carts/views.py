from django.shortcuts import render

# Create your views here.

"""
购物车：
在用户登录与未登录状态下，都可以保存用户的购物车数据
用户可以对购物车数据进行增、删、改、查
用户对于购物车数据的勾选也要保存，在订单结算页面会使用勾选数据
用户登录时，合并cookie中的购物车数据到redis中
"""
from rest_framework.views import APIView
from django_redis import get_redis_connection
from .serializers import CartSerializer,CartSKUSerializer,CartSKUDELSerializer
from rest_framework.response import Response
from rest_framework import status
import pickle
import base64
from . import constants
from goods.models import SKU
#购物车视图
class CartAPIView(APIView):
    """购物车"""

    # perform_authentication方法　会对传入额请求进行身份验证
    #重写认证方法　让没有登录的用户也能将商品添加到购物车
    def perform_authentication(self, request):

        pass

    #添加购物车
    def post(self,request):
        """
        添加商品到购物车接口
        :param request: 商品sku_id
        :return: 返回商品sku_id 数量，selected
        思路：
        获取请求的sku_id
        判断用户是否登录，登录的用户将商品保存到redis
        未登录的用户　将商品保存到cookie
        返回商品sku_id count selected(默认勾选)
        """

        #获取请求参数
        data = request.data

        #获取数据
        #创建序列化器对象
        ser = CartSerializer(data=data)
        #反序列化数据　序列化器自动校验数据
        ser.is_valid(raise_exception=True)
        #获取序反序列化的数据　validated_data 是反序列化检验后的数据但是还没保存到数据库
        sku_id = ser.validated_data.get('sku_id')
        count = ser.validated_data.get('count')
        selected = ser.validated_data.get('selected')

        #判断用户是否登录
        try:
            #获取登录的用户
            user = request.user
        except Exception:
            #没有登录的用户
            user = None

        # is_authenticate 是用户的一个属性　返回值是布尔型　　只要用户登录成功后该用户的is_authenticated属性就为true
        #如果用户登录　将用户添加到购物车中的商品保存到数据库缓存
        if user and user.is_authenticated:
            #用户已经登录 将用户添加到购物车的商品保存到redis
            #连接redis数据库
            conn = get_redis_connection('cart')
            #将商品sku_id count selected
            #使用redis hash类型保存　hincrby(键,域,值) 键打印出来的数据是　{域：值,,,}

            # 记录购物车商品数量
            pl = conn.pipeline()
            #hincrby()商品一次添加一个，添加重复的商品　数量加１
            #crat:{'sku_id1':count,sku_id2:count,,,,}
            pl.hincrby('cart_%s'%user.id,sku_id,count)  #保存商品数量 哈希类型数据　键打印出来的是{域：值,域：值}
            #记录购物车商品默认勾选　
            if selected:
                #sadd(键,值) 键：(值1,,,,)
                pl.sadd('cart_selected_%s'%user.id,sku_id)  #集合类型数据　键打印出来的是 {member1,member2,,}

            pl.execute()    #执行管道操作　一起将redis操作命令执行

            # print(conn.hgetall('cart_%s' % user.id))
            # print(conn.smembers('cart_selected_%s'% user.id))

            #返回响应　响应序列化后的数据　.data
            return Response(ser.data,status=status.HTTP_201_CREATED)


        #如果用户没有登录,将用户添加到购物车的保存cookie中
        else:
            #用户没有登录  将用户添加到购物车的商品保存到cookie

            #获取没有登录的用户的cookie 中的购物车
            cart = request.COOKIES.get('cart')

            #判断没有登录的用户购物车中是否有商品
            if cart:
                #如果cookie 的购物车中有商品
                cart_byte = cart.encode()   #将字符串格式cookie信息转换成byte　便于base64解码
                cart_base64 = base64.b64decode(cart_byte)
                #得到购物车
                cart_dict = pickle.loads(cart_base64)

                #如果用户的购物车中已经的商品　再点击添加购车　就把商品的数量加一
                sku_id = cart_dict.get('sku_id')
                if sku_id:
                    count += int(cart_dict.get('count'))
            else:
                #如果cookie中没有　返回响应时重新写入购物车cookie
                cart_dict = {}


            # 封装cookie中购物车数据
            cart_dict[sku_id] = {
                'count':count,
                'selected':selected
            }
            # pickle.dumps()将python数据转换成byte　pickle.loads()将byte装换成python数据
            cookie_cart = pickle.dumps(cart_dict)
            cookie_cart = base64.b64encode(cookie_cart).decode() #转换成字符串格式

            #将购物成cookie写入响应体中　便于前端保存cookie
            response = Response(ser.data)
            response.set_cookie('cart',cookie_cart,expires=constants.CART_COOKIE_EXPIRES)

            #返回响应
            return response


    #查询购物车
    def get(self,request):
        """
        用户点击购物车，购物车页面显示用户天剑到购物车的商品
        判断用户是偶登录
        已登录的用户，从redis中取出用户添加达商品，在购物车页面显示
        没有的登录的用户从用的cookie中取出添加的商品，在购物车页面展示
        :param request:
        :return: 返回　商品sku_id的商品信息 默认勾选　数量
        """
        #判断用户是否登录
        try:
            #从请求对象中获取用户
            user = request.user
        except Exception:

            user = None
        if user and user.is_authenticated :
            #表示用户已经登录过 从redis 中去初二用户添加过的商品
            #连接redis数据库
            conn = get_redis_connection('cart')
            #取出添加商品的id 数量
            cart_sku＿count = conn.hgetall('cart_%s'%user.id)
            #取出默认勾选的商品
            cart_selected = conn.smembers('cart_selected_%s'%user.id)

            #取出所有商品 组装数据
            cart = {}
            for sku_id,count in cart_sku＿count.items():     #从redis数据库重查询出来的字符串类型数据
                cart[int(sku_id)]={
                    'count':count,
                    'selected':sku_id in cart_selected  #sku_id in cart_select -->True/False
                }


        #如果用户没有登录　从用户的cookie 中取出添加的商品
        else:
            try:
                #获取用户的cookie 的购物车
                cart_cookie = request.COOKIES.get('cart')
                # 解密cart_cookie  base64 decode()是将bytez装成　base64 加密后的数据
                # base64 encode() 是将base64加密后的byte转换成　16进制的byte
                cart_base64 = base64.b64decode(cart_cookie.encode())
                # 将解码后数据转换成字典
                cart = pickle.loads(cart_base64)
            except Exception:
                cart = {}


        #从购物车中获取商品 凑够商品字典中遍历出商品sku_id
        skus = SKU.objects.filter(id__in=(cart.keys()))
        for sku in skus:
            #从购车中取出商品
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']


        #序列化商品数据　获取商品的sku信息
        ser = CartSKUSerializer(instance=skus,many=True)

        return Response(ser.data)



    #更新购物车
    def put(self,request):
        """
        用户在购物车页面对商品进行修改编辑
        接收用户对商品的修改　处理业务逻辑
        如果用户登录　将用户在购物车页面对商品的修改　在redis中对用户的商品进行修改
        如果用户没有登录　将用户在购物车页面对商品的修改　在用户的cookie中　对商品进行修改
        :param request: sku_id 商品的数量　count
        :return: 返回商品sku信息　数量　默认勾选
        """
        #判断用户是否登录
        try:
            #获取登录的用户
            user = request.user
        except Exception:
            #没有登录的用户
            user = None

        #获取请求数据
        data = request.data
        #获取序列化对象
        ser = CartSerializer(data=data)

        #校验数据
        ser.is_valid(raise_exception=True)
        #获取序列化器校验后的数据
        sku_id = ser.validated_data.get('sku_id')
        count = ser.validated_data.get('count')
        selected = ser.validated_data.get('selected')
        print(count)


        if user and user.is_authenticated:
            #用户已经登录 将用户添加到购物车的商品保存到redis
            #连接redis数据库
            conn = get_redis_connection('cart')
            #将商品sku_id count selected
            #使用redis hash类型保存　hincrby(键,域,值) 键打印出来的数据是　{域：值,,,}

            #将用户在购物车页面对商品的操作保存到redis数据库
            pl = conn.pipeline()

            pl.hset('cart_%s'%user.id,sku_id,count)

            #判断是否勾选
            if selected:
                pl.hincrby('cart_selected_%s'%user.id,sku_id)
            else:
                #不勾选
                pl.srem('cart_selected_%s'%user.id,sku_id)

            #返回响应数据
            return Response(ser.data)

        #用没有登录
        else:
            #从用户的cookie中获取购物车
            cart_cookie = request.COOKIES.get('cart')

            if cart_cookie:
                #如果用户cookie中购物车信息
                #解密
                cart_byte = base64.b64decode(cart_cookie.encode())
                #获取购物车字典
                cart = pickle.loads(cart_byte)

            else:
                cart={}

            #修改商品信息
            cart[sku_id]={
                'count':count,
                'selected':selected
            }

            #重新写入序列化后的数据　
            cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()

            #将cookie写入响应体
            response = Response(ser.data)
            response.set_cookie('cart',cookie_cart,constants.CART_COOKIE_EXPIRES)

            # 返回响应
            return response


    #删除购物车商品
    def delete(self,request):
        """
        用户点击删除按钮出发请求，
        接收请求，判断使用是否登录
        用户登录　就删除redis中的商品
        没有登录就删除cookie的商品
        :param request: sku_id
        :return:
        """
        #获取请求参数
        data = request.data

        #获取序列化器对下个
        ser = CartSKUDELSerializer(data=data)
        ser.is_valid(raise_exception=True)
        sku_id = ser.validated_data.get('sku_id')

        # 判断用户是否登录
        try:
            # 获取登录的用户
            user = request.user
        except Exception:
            # 没有登录的用户
            user = None

        if user and user.is_authenticated:
            #用户已经登录 将用户添加到购物车的商品保存到redis
            #连接redis数据库
            conn = get_redis_connection('cart')
            #将商品sku_id count selected
            #使用redis hash类型保存　hincrby(键,域,值) 键打印出来的数据是　{域：值,,,}

            #删除sku_id
            pl = conn.pipeline()
            pl.hdel('cart_%s'%user.id,sku_id)
            pl.srem('cart_selected_%s'%user.id,sku_id)
            pl.execute()


            #返回响应数据
            return Response(status=status.HTTP_204_NO_CONTENT)

        #用没有登录
        else:
            #从用户的cookie中获取购物车
            cart_cookie = request.COOKIES.get('cart')

            if cart_cookie:
                #如果用户cookie中购物车信息
                #解密
                cart_byte = base64.b64decode(cart_cookie.encode())
                #获取购物车字典
                cart = pickle.loads(cart_byte)

                # 从cookie中删除商品sku_id
                if sku_id in cart.keys():
                    del cart[sku_id]

            else:
                cart={}



            #重新删除后的购物车cookie数据　
            cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()

            #将cookie写入响应体
            response = Response(status=status.HTTP_204_NO_CONTENT)
            response.set_cookie('cart',cookie_cart,constants.CART_COOKIE_EXPIRES)

            # 返回响应
            return response



"""
购物车商品全选，非全选
全选:将购物车中所有商品全部显示勾选
接口设计
请求方式：put
接口url:/cart/selection
请求参数：selected
返回响应：json
"""
from .serializers import CartSelectedSerializer
class CartSelectedView(APIView):
    """全选/非全选"""

    def perform_authentication(self, request):

        pass

    def put(self,request):

        #获取请求参数
        user = request.user
        data = request.data
        #获取序列化器对象
        ser = CartSelectedSerializer(data=data)
        ser.is_valid(raise_exception=True)
        #获取序列化器校验后的数据
        selected = ser.validated_data.get('selected')


        #判断用户是否登录
        if user and user.is_authenticated:

            conn = get_redis_connection('cart')
            #将用户的商品全部勾选

            #hgetall 获取键　对应的所有的域：值
            cart = conn.hgetall('cart_%s'%user.id)
            """
            cart>>{'sku_id1':count,sku_id2:count,,,,}
            """
            print(cart)
            #遍历所有商品id
            sku_id_list = cart.keys()

            if selected:
                #全选
                conn.sadd('cart_selected_%s'%user.id,*[sku_id_list])
            else:
                #取消全选
                conn.srem('cart_selected_%s'%user.id,*[sku_id_list])

            return Response({'message':'ok'})


        else:
            #从cookie中获取购物车信息
            cart_cookie = request.COOKIES.get('cart')
            response = Response({'message':'ok'})

            if cart_cookie:
                # 解密
                cart = pickle.loads(base64.b64decode(cart_cookie.encode()))
                #给所有的商品　添加全选或非全选
                for sku_id in cart:
                    cart[sku_id]['selected']=selected


                """
                cart={
                'sku_id1:{'count':xx,'selected':xx},
                'sku_id2:{'count':xx,'selected':xx)
                ...
                }
                """

            else:
                cart={}

            #重写cookie
            cookie_cart = base64.b64encode(pickle.dumps(cart.encode(cart)))
            response.set_cookie('cart',cookie_cart,constants.CART_COOKIE_EXPIRES)

            return response













