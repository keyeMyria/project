from django.http.response import HttpResponse

# Create your views here.
"""
图片验证码接口设计：
前端通过图片验证码接口获取图片验证，后端通过接口返回图片验证码
用户点击图片生成新的图片验证码
业务流程：
    获取图片验证id
    生成图片验证返回前端
请求方式：get　　
接口url:/image_codes/?P<image_code_id>[\w-]+/ 　获取前端请求图片验证码的id　uuid
返回图片验证码:HttpResponse    返回HttpResponse响应　设置Context-Type='image/jpg 返回图片

"""
from django.views import View
#导入图片验证模块
from meiduomall.libs.captcha.captcha import captcha
#导入django的redis数据库连接方法
from django_redis import get_redis_connection
#导入常量
from . import constant

"""图片验证码类视图"""
class ImagesCodeView(View):
    """图片验证码"""

    #定义get请求方式的业务处理函数
    def get(self,request,image_code_id):

        #获取用户请求的图片验证码id
        image_code_id = image_code_id



        # 生成图片验证码和图片验证内容
        text,image = captcha.generate_captcha()

        print(text)

        #将图片保存到redis数据库并设置有效期，用于后面验证
        #连接redis数据库 get_redis_connection()参数为为redis的配置名 返回连接对象
        redis_conn = get_redis_connection("verification")
        #保存到redis数据库
        redis_conn.setex('img_%s'%image_code_id,constant.IMAGE_CODE_REDIS_EXPIRES,text)

        test_conn = get_redis_connection("default")
        #sting
        str1 = test_conn.get('name')
        print('type>>',type(str1),str1)
        #list
        list1 = test_conn.lrange('list1',0,-1)
        print('type>>', type(list1),list1)
        #hash
        obj1 = test_conn.hget('set1','name')
        obj2 = test_conn.hgetall('set1')
        print('type>>', type(obj1),obj1)
        print('type>>', type(obj2),obj2)
        #set
        set1 = test_conn.smembers('obj')
        print('type>>', type(set1),set1)











        # 固定返回验证码图片数据，不需要REST framework框架的Response帮助我们决定返回响应数据的格式
        # 所以此处直接使用Django原生的HttpResponse即可
        #返回图片验证码
        response=HttpResponse(image,content_type='images/jpg')
        response.set_cookie('id', 'xxx',max_age=60)
        return  response



"""
短信验证码接口设计
前端点击发送获取短信验证码，向后端请求短信验证码，
点击获取短信验证码前端将图片验证码的id和请求短信验证码的手机号码发给后端
业务处理流程
    检查图片验证码
    检查是否在60s内有发送记录
    生成短信验证码
    保存短信验证码与发送记录
    发送短信
请求方式：get  通过路由参数将手机号码和通过查询字符串方式将手机号码和图片验证码id  发给后端
接口url:/sms_code/(?P<moblie>1[3-9]\d{9})/?image_code_id=&text=
返回响应：json
"""
"""短信验证码类视图"""
from rest_framework.generics import GenericAPIView
#导入序列化器
from .serializer import VerificationSerializer
#导入短信验证码工具库
import random

#导入rest_frame　的响应
from rest_framework.response import Response

#使用celery异步发送短信验证码
from celery_tasks.sms.tasks import send_sms_code

class SmsCodeView(GenericAPIView):
    """短信验证码"""

    #指定序列化器
    serializer_class = VerificationSerializer


    #定义get请求的业务处理函数
    def get(self,request,mobile):
       """发送短信验证码"""

       #获取请求数据　获取查询字符串
       #获取图片验证码和图片验证码id
       data = request.query_params

       #通过序列化器　校验图片验证码，检查用户手机号是否在一分钟内已经发送过
       #获取序列器对象
       ser = self.get_serializer(data=data)
       ser.is_valid(raise_exception=True)
       # print(ser.validated_data)

       #生成短信验证码
       sms_code = "%06s"%random.randint(0,999999)

       #保存短信验证码到redis和用户请求短信验证码的记录
       #连接redis　数据库
       redis_conn = get_redis_connection('verification')

       # 使用管道的方式将数据添加到数据库  管道功能将命令集整合起来通过
       p = redis_conn.pipeline()

       #将用户的手机号码作为key　发给用户的短信验证码作为value保存到redis 并设置过期时间
       # redis_conn.setex('sms_%s'%mobile,constant.MS_CODE_REDIS_EXPIRES,sms_code)
       p.setex('sms_%s'%mobile,constant.MS_CODE_REDIS_EXPIRES,sms_code) #将命令添加到管道

       #将给用户手机号发送过短信验证码做一个一个记录保存数据库　用来判断限制同一个用一分钟内只能获取一次短信验证码
       # redis_conn.setex("sms_send_flag_%s"%mobile,constant.SEND_SMS_CODE_INTERVAL,1)
       p.setex("sms_send_flag_%s"%mobile,constant.SEND_SMS_CODE_INTERVAL,1)  #将命令添加到管道


       p.execute()

       #发送短信验证码到用户手机
       #生成发送短信验证码对象
       # ccp = CCP()
       # # #发送短信
       # ccp.send_template_sms(mobile,sms_code,constant.SMS_CODE_TEMP_ID)

       #使用django_celery_results　异步发送短息验证码
       #发送短信验证码函数通过delay方法触发生成任务
       send_sms_code.delay(mobile,sms_code,constant.SMS_CODE_TEMP_ID)

       #返回响应
       return Response({"message:ok"})
