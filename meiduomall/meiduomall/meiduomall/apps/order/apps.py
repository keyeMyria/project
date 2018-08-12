from django.apps import AppConfig


class OrderConfig(AppConfig):
    name = 'order'
    #模型类在站点中显示的名字
    verbose_name = '订单'
    verbose_name_plural = verbose_name
