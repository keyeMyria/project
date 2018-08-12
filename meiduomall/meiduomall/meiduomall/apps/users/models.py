from django.db import models

# Create your models here.

#导入Django认证系统的用户模型类
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as JST,BadData
from django.conf import settings
from . import constants

"""
创建用户表：
继承django提供的用户模型类
增加自定义字段
重新声明AUTH_USER_MODEL参数的设置　指定为自定义的用户模型类
"""
from meiduomall.utils.models import BaseModel

class User(AbstractUser):
    """用户模型类"""
    #增加手机号字段
    mobile = models.CharField(max_length=11,unique=False,verbose_name='手机号码')

    #增加用户中心显示的email激活状态字段
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    #添加用户默认收货地址字段
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')


    #设置表信息
    class Meta:
        db_table = 'tb_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    #定对象显示信息
    def __str__(self):
        return self.username


    def generate_verify_email_url(self):
        """加密用户id信息"""

        #获取用户信息
        data = {'user_id': self.id, 'email': self.email}

        # 生成加密工具对象 参数一是加密的秘钥，参数二是过期时间
        ser = JST(secret_key=settings.SECRET_KEY,expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)

        # 加密对象的dumps()方法　实现加密　返回的是二进制数据
        token = ser.dumps(data).decode()

        #拼接验证链接
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.htmls?token=' + token

        return verify_url


    #解密验证链接的用户信息
    def check_token(self,token):


        # 生成加密工具对象 参数一是加密的秘钥，参数二是过期时间
        ser = JST(secret_key=settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)

        #解密  解密不需要decode()
        data = ser.loads(token)

        #查询用户信息
        try:
            user_id = data.get('user_id')
            user_email = data.get('email')

        except BadData : #解密错误抛出解密的异常
            return None

        #判断用户是否验证过邮箱
        try:
            user = User.objects.get(id=user_id,email=user_email)
        except User.DoesNotExist:  #查询不到用户代表用户没有验证邮箱
            return None

        return user





#
# """
# 创建用户和QQ关联模型类
# """
# from django.db import models
# #到入补充字段类
# from meiduomall.utils.models import BaseModel
#
# class OAuthQQModel(BaseModel):
#     """用户和QQ关联模型类"""
#
#     #设置模型类字段属性
#     #外键关联用户表模型类
#     user = models.ForeignKey('users.User',on_delete=models.CASCADE,verbose_name='用户')
#     #第三方QQ平台的的用户信息 设置索引　提高查询性能
#     openid = models.CharField(max_length=64,verbose_name='openid',db_index=True)
#
#     #设置表信息
#     class Meta:
#         db_table = 'tb_oauth_qq'
#         verbose_name = 'QQ登录用户数据'
#         verbose_name_plural = verbose_name
#
#


"""
用户收货地址模型类
"""
class Address(BaseModel):
    """
    用户地址
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('area.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('area.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('area.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']
