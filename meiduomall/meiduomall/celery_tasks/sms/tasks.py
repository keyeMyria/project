

"""
发出任务：
发送短信验证码
"""
from celery_tasks.main import celery_app
from meiduomall.libs.yuntongxun.sms import CCP

#使用celery_app.task()装饰创建任务  name参数为任务名字 装饰器来存放任务
#使用装饰器装饰发送短信验证码函数
@celery_app.task(name='send_smscode')
def send_sms_code(mobile,sms_code,temp_id):
    #创建发送短信验证码对象
    ccp = CCP()
    #发送短信验证码
    ccp.send_template_sms(mobile,sms_code,temp_id)
