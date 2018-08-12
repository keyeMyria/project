"""创建模型序列化器"""
"""
用户模型类序列化器为了校验注册信息
继承用户模型类来创建
"""

import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from .models import User


class UserModelSerialzer(serializers.ModelSerializer):
    """用户模型序列化器"""
    # 添加自定义序列化字段
    password2 = serializers.CharField(label='确认密码', write_only=True)
    allow = serializers.CharField(label='同意协议选项', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    token = serializers.CharField(label='登录状态token', read_only=True)  # 增加token字段

    # 指定模型类序列化器的映射的模型类
    class Meta:
        # 指明序列化数据表的模型类
        model = User
        # 指明序列化字段
        fields = ('id', 'username', 'mobile', 'password', 'password2', 'sms_code', 'allow', 'token')
        # 添加字段的额外的校验参数选项
        extra_args = {
            'username': {
                'max_length': 20,
                'mix_length': 5,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名'}
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    # 校验字段数据
    def validate_mobile(self, value):
        """手机号码校验"""
        # 获取请求的手机号
        mobile = value
        # 校验手机号
        if not re.match(r'1[3-9]\d{9}', mobile):
            raise serializers.ErrorDetail('手机号有误')
        return value

    def validate_allow(self, value):
        """校验alow选项"""
        # 获取请求数据
        allow = value
        # 判断是否勾选allow选项
        if allow != 'true':
            raise serializers.ErrorDetail('请同意用户协议')

        return value

    def validate(self, attrs):
        """校验密码和确认密码,短信验证码"""
        # 获取请求数据
        password = attrs.get('password')
        password2 = attrs.get('password2')
        sms_code = attrs.get('sms_code')

        # 验证密码：
        if password != password2:
            raise serializers.ErrorDetail('两次输入密码不一致')

        # 从redis中取出真实的短信验证码
        # 连接redis
        redis_conn = get_redis_connection('verification')
        mobile = attrs.get('mobile')
        real_sms_code = redis_conn.get('sms_%s' % mobile).decode()

        # 验证短信验证码
        if sms_code != real_sms_code:
            raise serializers.ErrorDetail('短信验证码错误')

        return attrs

    # 保存校验成功后的数据到数据库
    def create(self, validated_data):
        # 创建用户对象
        user = User()
        user.username = validated_data.get('username')
        user.mobile = validated_data.get('mobile')
        user.password = validated_data.get('password')
        # 保存到数据
        user.save()

        # 把密码加密
        user.set_password(validated_data.get('password'))
        user.save()

        # 使用jwt机制来识别用户，和保持登录
        # 补充生成记录登录状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        print(token)
        # 将jwt写入user　返回响应　客户端会自动保存jwt的token值
        user.token = token

        # 返回对象
        return user


# """
# QQ登录序列化器
#
# """
# from .utils import OAuthQQ
# from .models import OAuthQQModel
#
#
# class OAuthQQModelSerializer(serializers.ModelSerializer):
#     """QQ登录模型序列化器"""
#     # 指定序列化器序列化字段
#     sms_code = serializers.CharField(label='短信验证码', write_only=True)
#     token = serializers.CharField(label='登录状态token', read_only=True)
#     mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
#     # 操作凭证
#     access_token = serializers.CharField(label='操作凭证', write_only=True)
#
#     # 指定模型序列化器的模型类
#     class Meta:
#         model = User
#         fields = ['mobile', 'password', 'sms_code', 'access_token', 'id', 'username', 'token']
#         # 为字段天剑额外的校验参数
#         extra_args = {
#             'username': {
#                 'read_only': True
#             },
#             'password': {
#                 'write_only': True,
#                 'min_length': 8,
#                 'max_length': 20,
#                 'error_messages': {
#                     'min_length': '仅允许8-20个字符的密码',
#                     'max_length': '仅允许8-20个字符的密码',
#                 }
#             }
#         }
#
#     # 校验字段
#     def validate(self, attrs):
#         # 获取字段数据
#         mobile = attrs.get('mobile')
#         password = attrs.get('password')
#         access_token = attrs.get('access_token')
#         sms_code = attrs['sms_code']
#
#         # 校验字段数据
#         # 校验短息验证码
#         # 连接redis数据库
#         redis_conn = get_redis_connection('verification')
#         real_sms_code = redis_conn.get('sms_%s' % mobile)
#         if sms_code != real_sms_code:
#             raise serializers.ErrorDetail('短信验证码错误')
#
#         # 校验密码　如果用户存在就校验用户密码
#         try:
#             user = User.objects.get(mobile=mobile)
#         except User.DoesNotExist:
#             pass
#         else:
#             # 用户存在就校验用户密码
#             if not user.check_password(password):
#                 raise serializers.ErrorDetail('密码错误')
#             #返回用户模型类实例
#             attrs['user']=user
#
#         # 校验access_token
#         # 如果accsess_token 代表可以获取用户第三QQ登录后的用户信息openid
#         oauthqq = OAuthQQ()
#         openid = oauthqq.check_accsess_token(access_token)
#         if not openid:
#             raise serializers.ErrorDetail('无效access_token')
#         # 添加openid 到attrs字典　添加校验后的数据
#         attrs['openid'] = openid
#
#         return attrs
#
#     # 保存校验后的数据　反序列化　保存数据到数据
#     def create(self, validated_data):
#         """保存反序列化数据"""
#
#         #h获取校验后的数据　反序列化
#         mobile = validated_data.get('mobile')
#         user = validated_data.get('user')
#         openid = validated_data.get('openid')
#         password = validated_data.get('password')
#
#         #判断用户是否存在
#         if not user:
#             #表示用户使用qq第一次登录
#             #绑定用户数据
#             user = User.objects.create_user(username=mobile,password=password,mobile=mobile)
#
#         #绑定qq和用户关联
#         OAuthQQModel.objects.create(user=user, openid=openid)
#
#         #为登录过的用户签发jwt
#         # 签发jwt token
#         jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
#         jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
#
#         payload = jwt_payload_handler(user)
#         token = jwt_encode_handler(payload)
#
#         user.token = token
#
#         return user



"""
用户详情序列化器
"""
from celery_tasks.email.tasks import send_verify_email
class UserDetaillSerializer(serializers.ModelSerializer):
    """用户详情序列化器"""

    class Meta:
        model = User
        fields = ['username','id','email','email_active','mobile']



"""验证邮箱序列化器"""

class EmailVerifySerializer(serializers.ModelSerializer):
    """邮箱验证序列化器"""


    class Meta:
        model = User
        fields = ['email','email_active']


    #email字段默认是可以不填，重写序列化器的update方法　更新eamil
    def update(self, instance, validated_data):
        """更新eamil"""
        #获取验证后的email　信息
        email = validated_data.get('email')

        #保存用户邮箱信息
        instance.email = email


        #生成验证链接
        verify_url = instance.generate_verify_email_url()

        # 发送邮箱验证链接
        send_verify_email.delay( email,verify_url)


        instance.save()
        return instance





"""用户地址管理序列化器"""
from .models import Address
class UserAdressSerializer(serializers.ModelSerializer):
    """用户地址管理序模型类列化器"""

    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    #指定序列化器模型类
    class Meta:
        model = Address
        #eclude取反　
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        """
        保存
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



class AddressTitleSerializer(serializers.ModelSerializer):
    """标题序列化器"""

    class Meta:
        model = Address
        fields = ['title']



"""
历史浏览记录序列化器
校验前端传来的商品id　校验商品书否存在，将商品id缓存到redis
"""
from goods.models import SKU
from django_redis import get_redis_connection
class HistorySerialier(serializers.Serializer):
    """历史浏览记录序列化器"""

    sku_id = serializers.IntegerField(label='sku_id',min_value=1)


    #校验sku_id
    def validate_sku_id(self,value):

        """
        查询数据库看是否有该商品
        """
        if not SKU.objects.get(id=value):
            return SKU.DoesNotExist
        return value


    #将用户浏览的商品id　缓存到redis　用户id作为键，商品id作为value
    def create(self, validated_data):

        #连接redis数据库
        conn = get_redis_connection('history')

        #获取用户对象
        user_id = self.context['request'].user.id

        #将商品id 保存到redis
        sku_id = validated_data.get('sku_id')

        #保存到redis
        pl = conn.pipeline()

        # 移除已经存在的本商品浏览记录
        pl.lrem("history_%s" % user_id, 2, sku_id)
        #添加数据 lpush新建并添加数据　lset不能添加到空列表中
        pl.lpush('history_%s'%user_id,sku_id)
        #设置最多保存5个商品信息
        pl.ltrim('history_%s'%user_id,0,4)

        pl.execute()

        return validated_data






