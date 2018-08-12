from django.conf.urls import url
from . import views
#验证模块的url
urlpatterns = [
    #图片验证码url
    url(r'^image_codes/(?P<image_code_id>[\w-]+)/$',views.ImagesCodeView.as_view()),
    #短信验证码url
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$',views.SmsCodeView.as_view()),

]