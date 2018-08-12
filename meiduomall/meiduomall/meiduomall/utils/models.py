

"""定义模型类基类"""
from django.db import models

class BaseModel(models.Model):
    """定义模型类基类　
        为其他模型类提供补充字段
    """

    #定义创建时间字段　datetime属性　auto_now_add=True表示创建时自动添加创建时间
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    #创建更新时间字段　datetime属性　auto_now=True表示更新时自动添加更新时间
    update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')

    # 设置表信息
    class Meta:
        # abstract 说明是抽象模型类, 用于继承使用，数据库迁移时不会创建BaseModel的表
        abstract = True



