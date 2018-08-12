
from rest_framework import serializers
from .models import SKU
"""
商品列表信息序列化器
通过点击商品分类　向后端请求该分类下所有商品显示在商品列表中
显示　名称　价钱　默认图片　评论量
"""
class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ['id','name','price','comments','default_image_url']




"""
创建haystack序列化器
序列化器用来检查前端传入的参数text，并且检索出数据后再使用这个序列化器返回给前端；
序列化器中的object字段是用来向前端返回数据时序列化的字段
"""

from drf_haystack.serializers import HaystackSerializer
from .search_indexes import SKUIndex


class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    object = SKUSerializer(read_only=True)

    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'object')
