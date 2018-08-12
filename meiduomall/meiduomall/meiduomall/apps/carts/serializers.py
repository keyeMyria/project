

from rest_framework import serializers

"""
创建商品添加到购物车的序列化器
"""
from goods.models import SKU
class CartSerializer(serializers.Serializer):

    sku_id = serializers.IntegerField(label='商品id',min_value=1)
    count = serializers.IntegerField(label='数量',min_value=1)
    selected = serializers.BooleanField(label='是否勾选',default=True)


    #校验
    def validate(self, attr):
        """校验商品id"""

        try:
            sku = SKU.objects.get(id=attr['sku_id'])
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        if attr['count'] > sku.stock:
            raise serializers.ValidationError('商品库存不足')

        return attr




"""创建购物车商品展示序列化器"""
class CartSKUSerializer(serializers.ModelSerializer):

    #添加额外的序列化自字段
    count = serializers.IntegerField(label='数量',min_value=1)
    selected = serializers.BooleanField(label='默认勾选',default=True)

    #指定模型序列化器的模型类
    class Meta:
        model = SKU
        fields = ['id', 'count', 'name', 'default_image_url', 'price', 'selected']




"""删除商品序列化器"""

class CartSKUDELSerializer(serializers.Serializer):

    sku_id = serializers.IntegerField(label='sku_id',min_value=1)


    #校验
    def validate(self, attrs):
        sku_id = attrs.get('sku_id')
        if not SKU.objects.get(id=sku_id):
            raise SKU.DoesNotEXist

        return attrs


"""全选序列化器"""
class CartSelectedSerializer(serializers.Serializer):

    selected = serializers.BooleanField(label='全选')





