
from rest_framework import serializers
from goods.models import SKU
"""
订单页详情序列化器
返回商品信息
sku_id default_image_url count price 订单号
"""
class OrderSKUserializer(serializers.ModelSerializer):
    """订单详情序列化器"""

    count = serializers.IntegerField(label='数量',min_value=1)


    class Meta:
        model = SKU
        fields = ['id', 'name', 'default_image_url', 'price', 'count']



class OrderSettlementSerializer(serializers.Serializer):
    """
    订单结算数据序列化器
    """
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    #序列化器嵌套
    skus = OrderSKUserializer(many=True)


from .models import OrderInfo,OrderGoods
from django_redis import get_redis_connection
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
import logging

logger = logging.getLogger('django')

"""
提交订单后校验下单的数据
返回订单总价和订单号
"""
class SaveOrderSerializer(serializers.ModelSerializer):
    """下单数据序列化器"""

    class Meta:
        model = OrderInfo
        fields = ['order_id', 'address', 'pay_method']
        #只读字段
        read_only_fields =['order_id']
        #下单时地址和支付方式必须输入
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }


    def create(self, validated_data):
        """
        序列化器校验数据后添加业务逻辑
        查询库存
        创建订单号
        处理并发下单情况造成死锁
        计算订单总价
        """
        #获取当前下单用户
        user = self.context['request'].user

        #获取校验后的数据
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

        address = validated_data['address']
        pay_method = validated_data['pay_method']

        #使用事务来处理并发下单情况下造成死锁问题
        with transaction.atomic():
            # 创建一个保存点 用于事务的一系列操作失败后　事务回滚到当前状态
            save_id = transaction.savepoint()
            try:
                #创建订单
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal(0),
                    freight=Decimal(10),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'CASH'] else OrderInfo.ORDER_STATUS_ENUM['UNPAID']

                )

                #从redis中获取下单的商品(用户下单的商品必然是勾选过的商品)
                redis_conn = get_redis_connection('cart')
                #获取用户勾选下单的商品
                cart_selected = redis_conn.smembers('cart_selected_%s'%user.id)
                cart_redis = redis_conn.hgetall('cart_%s'%user.id)
                cart={}
                for sku_id in cart_selected:
                    cart[int(sku_id)] = int(cart_redis[sku_id])

                #获取商品所有id
                sku_id_list = cart.keys()
                # skus = SKU.objects.filter(id__in=cart.keys())
                #判断下单商品的数量是否查过商品库存
                for sku_id in sku_id_list:

                    while True:

                        #获取商品
                        sku = SKU.objects.get(id=sku_id)
                        #获取下单商品的数量
                        order_count = int(cart[sku.id])
                        #获取商品sku库存
                        origin_counts = sku.stock
                        origin_sales = sku.sales

                        if order_count > origin_counts:

                            transaction.savepoint_rollback(save_id)
                            raise serializers.ErrorDetail('库存不足')



                        #下单成功后修改库存和销量
                        new_counts = origin_counts -order_count
                        new_sales = origin_sales + order_count


                        #乐观锁在更新的时候判断此时的库存是否是之前查询出的库存
                        ret = SKU.objects.filter(id=sku.id, stock=origin_counts).update(stock=new_counts, sales=new_sales)
                        if ret == 0:
                            #如果该商品的库存不足，跳到for循环 下一个商品
                            continue

                        # sku.sales,sku.stock = new_sales,new_counts
                        # sku.save()
                        sku.goods.sales += order_count
                        sku.goods.save()

                        #计算出订单总价
                        order.total_amount += (sku.price*order_count)
                        order.total_count += order_count



                        #创建商品订单
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=order_count,
                            price=sku.price
                        )
                        #更新成功
                        break

                #修改订单总价费用　总价＋邮费
                order.total_amount += order.freight
                print(order.total_amount)
                order.save()
            except serializers.ValidationError:
                raise
            except Exception as e:
                print('...')
                logger.error(e)
                #事务失败或中断后事务回滚
                transaction.savepoint_rollback(save_id)
                raise

            #事务的一系列操作成功后　提交数据库
            transaction.savepoint_commit(save_id)

            #删除redis中用户已经下单的商品
            conn = get_redis_connection('cart')
            conn.hdel('cart_%s'%user.id,*cart_selected)
            conn.srem('cart_selected_%s'%user.id,*cart_selected)


            #保存订单
            return order




