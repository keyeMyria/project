from django.conf.urls import url
from . import views
urlpatterns =[
    #购物车
    url(r'^cart/$',views.CartAPIView.as_view()),
    #购物车全选
    url(r'^cart/selection/$',views.CartSelectedView.as_view())
]