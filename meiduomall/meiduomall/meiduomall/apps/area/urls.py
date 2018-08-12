from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from . import views
urlpatterns = []

#获取视图集的路由器对象
router = DefaultRouter()

#注册路由
router.register(r'areas',views.AreasViewSet,base_name='areas')

#添加到django的路由列表
urlpatterns += router.urls