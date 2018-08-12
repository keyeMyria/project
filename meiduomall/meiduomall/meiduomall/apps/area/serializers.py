from rest_framework import serializers
from .models import Area

"""
收货地址序列化器
获取省份信息序列化器
"""

class AreaPrSerilizer(serializers.ModelSerializer):
    """获取省份信息"""

    class Meta:
        model = Area
        fields = ['id','name']



"""获取省份下属的所有信息"""

class AreaMoreSerializer(serializers.ModelSerializer):
    """获取省份下属的所有信息
    """
    #指定外键关联集字段
    subs = AreaPrSerilizer(many=True,read_only=True)

    class Meta:
        model = Area
        fields = ['id','name','subs']