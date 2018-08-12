from django_redis import get_redis_connection
import base64,pickle
"""
合并购物车
将未登录用户的cookie中的购物车商品添加到用户登录后的redis中

修改登录代码
在普通登录后合并购物车
qq登录后合并购物车
"""

def minxiusercart(request,user,response):
    """合并购物车"""
    """
    在用户登录时，把用户cookie中的购物车商品添加到用户的redis缓存
    """

    #取出用户cookie中的商品
    cookie_cart = request.COOKIES.get('cart')

    if not cookie_cart:
        return response
    #解密取出商品
    cart_cookie = pickle.loads(base64.b64decode(cookie_cart.encode()))
    print(cart_cookie)

    """
    cart_cookie={
        'sku_id':{'count':count,'selected':selected}
        ...
    }
    """

    #组装数据
    #保存商品id和数量
    cart = {}
    #保存勾选的商品id
    cart_selected = []
    #保存没有勾选的商品id
    cart_unselected = []
    sku_id_list = cart_cookie.keys()
    for sku_id in sku_id_list:
        cart[sku_id]=cart_cookie[sku_id]['count']
        if cart_cookie[sku_id]['selected']:
            cart_selected.append(sku_id)
        else:
            cart_unselected.append(sku_id)

    #如果用户的购车里有商品
    if cart:
        #连接用户登录后的redis缓存购物车
        conn = get_redis_connection('cart')
        #将cookie的商品添加到redis
        pl = conn.pipeline()
        for key,value in cart.items():
            pl.hset('cart_%s'%user.id,key,value)
        if cart_selected:
            pl.sadd('cart_selected_%s'%user.id,*cart_selected)
        if cart_unselected:
            pl.srem('cart_selected_%s'%user.id,*cart_unselected)

        pl.execute()

    #删除cookie
    response.delete_cookie('cart')

    return response

