from django.db import models

# Create your models here.

"""
创建用户和QQ关联模型类
"""
from django.db import models
#到入补充字段类
from meiduomall.utils.models import BaseModel

class OAuthQQModel(BaseModel):
    """用户和QQ关联模型类"""

    #设置模型类字段属性
    #外键关联用户表模型类
    user = models.ForeignKey('users.User',on_delete=models.CASCADE,verbose_name='用户')
    #第三方QQ平台的的用户信息 设置索引　提高查询性能
    openid = models.CharField(max_length=64,verbose_name='openid',db_index=True)

    #设置表信息
    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name


