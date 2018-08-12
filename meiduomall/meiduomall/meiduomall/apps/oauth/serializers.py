
"""
QQ登录序列化器

"""
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from users.models import User
from .utils import OAuthQQ
from .models import OAuthQQModel

"""
绑定第一次使用qq登录的用户信息

"""
class OAuthQQModelSerializer(serializers.ModelSerializer):
    """QQ登录模型序列化器"""

    # 指定序列化器序列化字段
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    token = serializers.CharField(label='登录状态token', read_only=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    # 绑定qq用户信息操作凭证　
    access_token = serializers.CharField(label='操作凭证', write_only=True)

    # 指定模型序列化器的模型类
    class Meta:
        model = User
        fields = ['mobile', 'password', 'sms_code', 'access_token', 'id', 'username', 'token']

        # 为字段天剑额外的校验参数
        extra_args = {
            'username': {
                'read_only': True
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

    # 校验字段
    def validate(self, attrs):
        # 获取字段数据
        mobile = attrs.get('mobile')
        password = attrs.get('password')
        access_token = attrs.get('access_token')
        sms_code = attrs['sms_code']

        # 校验字段数据
        # 校验短息验证码
        # 连接redis数据库
        redis_conn = get_redis_connection('verification')
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        print(real_sms_code,'...')
        if sms_code != real_sms_code.decode():
            raise serializers.ErrorDetail('短信验证码错误')

        # 校验密码　如果用户存在就校验用户密码
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            # 用户存在就校验用户密码
            if not user.check_password(password):
                raise serializers.ErrorDetail('密码错误')
            #返回用户模型类实例
            attrs['user']=user

        # 校验access_token
        # 如果accsess_token 代表可以获取用户第三QQ登录后的用户信息openid
        oauthqq = OAuthQQ()
        openid = oauthqq.check_accsess_token(access_token)
        if not openid:
            raise serializers.ErrorDetail('无效access_token')

        #获取qq用户信息
        qq_info = oauthqq.get_qq_user_info(access_token,openid)
        date = qq_info.read().decode()
        with open('qq_info.txt','w') as f :
            f.write(date)


        # 添加openid 到attrs字典　添加校验后的数据
        attrs['openid'] = openid

        return attrs

    # # 保存校验后的数据　反序列化　保存数据到数据
    def create(self, validated_data):
        """保存反序列化数据"""

        #h获取校验后的数据　反序列化
        mobile = validated_data.get('mobile')
        user = validated_data.get('user')
        openid = validated_data.get('openid')
        password = validated_data.get('password')

        #判断用户是否存在
        if not user:
            #表示用户使用qq第一次登录
            #绑定用户数据
            user = User.objects.create_user(username=mobile,password=password,mobile=mobile)

        #绑定qq和用户关联
        OAuthQQModel.objects.create(user=user, openid=openid)

        #为视图对象绑定user属性
        # self.context['views'].user=user

        #为登录过的用户签发jwt
        # 签发jwt token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token

        return user




