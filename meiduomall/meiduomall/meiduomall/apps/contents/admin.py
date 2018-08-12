from django.contrib import admin

# Register your models here.
#注册站点模型类
from . import models

admin.site.register(models.ContentCategory)
admin.site.register(models.Content)