
# 使用TimedJSONWebSignatureSerializer可以生成带有有效期的token

from itsdangerous import TimedJSONWebSignatureSerializer as Serializers

from django.conf import settings


"""
加密第一次使用qq登录的用户的openid信息
用来为绑定qq用户信息做标识
"""
#创建加密工具
#secret_key为加密的秘钥，expires_in为有效期
serializer = Serializers(secret_key=settings.SECRET_KEY,expires_in=300)