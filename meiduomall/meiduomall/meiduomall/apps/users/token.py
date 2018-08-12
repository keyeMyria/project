



# 使用TimedJSONWebSignatureSerializer可以生成带有有效期的token

from itsdangerous import TimedJSONWebSignatureSerializer as Serializers

from django.conf import settings

#创建加密工具
#secret_key为加密的秘钥，expires_in为有效期
serializer = Serializers(secret_key=settings.SECRET_KEY,expires_in=300)