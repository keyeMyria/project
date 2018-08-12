#序列化器
from rest_framework import serializers
from django_redis import get_redis_connection
class VerificationSerializer(serializers.Serializer):
    """短息验证码序列化器"""

    #定义序列化字段
    #图片验证码
    text = serializers.CharField(max_length=4,min_length=4)
    #图片验证码的uuid
    image_code_id = serializers.UUIDField()

    # print(text,image_code_id)
    #定义校验器
    def validate(self, attrs):
        """验证图片验证码"""

        #获取请求数据  获取用户输入的图片验证码
        image_code_id = attrs.get('image_code_id')
        print('222222%s'%image_code_id)
        text = attrs.get('text')

        #根据前端的图片验证码的uuid从redis数据库中查找对应验证码
        #连接redis的图片验证码库
        redis_conn = get_redis_connection('verification')
        #获取真实的图片验证码 从数据库取出来的数据byte类型
        try:
            img_content = redis_conn.get('img_%s'% image_code_id).decode()
        except:
            raise serializers.ErrorDetail('请输入短信验证码')

        #判断是否图片验证码是否过期
        if not img_content:
            raise serializers.ErrorDetail('图片验证码过期')

        #删除redis数据库中的图片验证码
        redis_conn.delete('img_%s'% image_code_id)

        #校验用户输入的图片验证码
        if text.lower() != img_content.lower():
            print(text.lower(), img_content.lower())
            raise serializers.ErrorDetail('图片验证码错误')

        #用户手机号码是不是60秒内有发送的记录　限定一分钟内不能重复发短信验证码
        #查询数据库有该用户手机号的发短信验证码记录
        #获取用户手机号 通过序列器对象的上下文context获取视图对象　再根据视图对象获取视图的moblie参数
        # kwargs 是序列化器帮助我们是自己实现的一个类字典的封装
        # 视图对象初始化时将**kwargs的数据封装到kwargs类字典中
        # 视图对象初始化时将*args的数据封装到args元组中
        mobile = self.context['view'].kwargs['mobile']

        #通过序列化器对象的context属性或取请求对象request,视图对象view，请求数据格式format
        # print(self.context['view'])
        # print(self.context['view'].kwargs)
        # print(self.context['view'].args)
        # print('...')
        # print(self.context['request'])
        # print(self.context['request'].data)
        # print(self.context['request'].query_params)
        # print('...')
        # print(self.context['format'])
        sms_send_flag = redis_conn.get("sms_send_flag_%s"%mobile)

        #检查用户的手机号是不是在一分钟内获取过短信验证码
        if sms_send_flag:
            raise serializers.ErrorDetail('请求次数过于频繁')


        return attrs