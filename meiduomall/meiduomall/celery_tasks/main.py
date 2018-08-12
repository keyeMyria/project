"""
Celery是一个功能完备即插即用的任务队列
broker(中间人将任务保存到redis中)      >>>    worker(多进程处理任务)
接收任务　　　　　　　　　　　　　　　　　　　　　处理任务
"""
"""
任务队列是一种跨线程、跨机器工作的一种机制.
任务队列中包含称作任务的工作单元。有专门的工作进程持续不断的监视任务队列，并从中获得新的任务并处理.

1:创建任务队列应用　celery()
2:配置任务队列(将任务队列保存到redis数据库) config_from_object  任务中间人
3:创建任务功能函数，使用装饰器将任务函数绑定任务队列应用　　　　　任务处理者worker
4:添加任务到任务列表 autodiscover_tasks([])  参数为发出任务的文件 添加任务到broker
5:视图函数中触发任务功能函数　功能函数.delay()  发起任务

运行任务队列服务器
celery -A 任务队列入口文件　worker -l 日志等级
"""



from celery import Celery


# 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduomall.settings.dev'

#创建celery任务队列应用  参数为自动生成的工程任务名字
celery_app = Celery('meiduo')


#配置celery应用
celery_app.config_from_object('celery_tasks.config')



# 自动注册celery任务 autodiscover_tasks()　celery应用开启自动添加任务
# autodiscover_tasks()参数为发出任务的文件包　
# celery应用会通过autodiscover_tasks自动将该文件发出的任务添加到任务队列
celery_app.autodiscover_tasks(['celery_tasks.html','celery_tasks.sms','celery_tasks.email'])