import xadmin
from . import models

#创建order模块的模型类管理器
class OrderAdminManager(object):
    #显示字段
    list_display = ['order_id', 'create_time', 'total_amount', 'pay_method', 'status']
    refresh_times = [3, 5]
    #数据表
    data_charts = {
                        #表标题　　　　　　　　　x轴字段　　　　　　　　　　　　　y轴字段
        "order_amount": {'title': '订单金额', "x-field": "create_time", "y-field": ('total_amount',),
                         #x轴按创建时间排序
                         "order": ('create_time',)},
        "order_count": {'title': '订单量', "x-field": "create_time", "y-field": ('total_count',),
                        "order": ('create_time',)},
    }


#将order模块的模型类注册到xadmin站点
xadmin.site.register(models.OrderInfo,OrderAdminManager)
xadmin.site.register(models.OrderGoods)