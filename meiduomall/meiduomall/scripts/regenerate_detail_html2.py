#!/usr/bin/env python

"""
功能：手动生成所有SKU的静态detail html文件
使用方法:
    ./regenerate_detail_html.py
"""
import sys
sys.path.insert(0, '../')

import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduomall.settings.dev'

import django
django.setup()

from django.template import loader
from django.conf import settings

from goods.utils import get_categories
from goods.models import SKU


"""
获取商品详详情
根据前端传来的sku_id　查询出商品sku详情(名称，价格，副标题，销量，进货价)
根据sku商品　查询出spu商品 >>>获取面包线
根据sku商品查询出sku商品规格信息
"""

def generate_static_sku_detail_html(sku_id):
    """
    生成静态商品详情页面
    :param sku_id: 商品sku id
    """
    # 商品分类菜单
    categories = get_categories()

    # 获取当前sku的信息
    sku = SKU.objects.get(id=sku_id)
    print('sku>>',sku)
    #商品sku和skuimage是一对多关系
    sku.images = sku.skuimage_set.all()
    print('sku.image>>', sku.images)

    # 面包屑导航信息中的频道
    goods = sku.goods
    print('goods>>>',goods)
    # goods.channel = goods.category1.goodschannel_set.all()[0]
    goods.channel = goods.category1
    print('面包线>>>>')
    print(goods.category1.goodschannel_set.all())
    print('....')
    print(goods.category1)

    # 构建当前商品的规格键　sku商品和skuspecification是一对多关系　一个sku商品有多个规格选项
    sku_specs = sku.skuspecification_set.order_by('spec_id')
    print('sku_specs>>',sku_specs)
    sku_key = []
    for spec in sku_specs:
        #获取规格的所有选项值
        sku_key.append(spec.option.id)

    # 获取当前商品的所有SKU　eg:获取苹果6下的所有苹果6手机
    skus = goods.sku_set.all()
    print('skus>>>',skus)
    # 封装spu下所有的sku的规格选项，通过点击规格选项选取spu下不同的sku

    # 构建不同规格参数（选项）的sku字典
    # spec_sku_map = {
    #     (规格1参数id, 规格2参数id, 规格3参数id, ...): sku_id,
    #     (规格1参数id, 规格2参数id, 规格3参数id, ...): sku_id,
    #     ...
    # }
    spec_sku_map = {}
    for s in skus:
        # 获取sku的规格参数
        s_specs = s.skuspecification_set.order_by('spec_id')
        # 用于形成规格参数-sku字典的键
        key = []
        for spec in s_specs:
            key.append(spec.option.id)
        # 向规格参数-sku字典添加记录
        spec_sku_map[tuple(key)] = s.id

    # 获取当前商品的规格信息
    specs = goods.goodsspecification_set.order_by('id')
    print('specs>>',specs)
    # 若当前sku的规格信息不完整，则不再继续
    if len(sku_key) < len(specs):
        return
    for index, spec in enumerate(specs):
        # 复制当前sku的规格键
        key = sku_key[:]
        # 该规格的选项
        options = spec.specificationoption_set.all()
        for option in options:
            # 在规格参数sku字典中查找符合当前规格的sku
            key[index] = option.id
            option.sku_id = spec_sku_map.get(tuple(key))

        spec.options = options

    # 渲染模板，生成静态html文件
    context = {
        'categories': categories,
        'goods': goods,
        'specs': specs,
        'sku': sku,

    }

    template = loader.get_template('detail.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'goods/'+str(sku_id)+'.html')
    with open(file_path, 'w') as f:
        f.write(html_text)




def generate_static_sku_detail_html2(sku_id):
    """获取商品详情"""
    """
    获取商品菜单　返回categories
    获取商品规格信息 返sku
    获取商品面包线     返回goods
    获取商品规格信息      返回specs
    """

    #获取商品菜单
    categories = get_categories()

    #获取当前sku商品信息
    sku = SKU.objects.get(id=sku_id)
    print('获取当前sku商品:',sku)
    #获取商品所有图片　前端通过sku.images 获取商品的图片
    sku.images=sku.skuimage_set.all()
    print('获取当前sku商品的图片:', sku.images)



    #获取商品面包线
    #得到商品的spu
    goods = sku.goods
    print('获取当前sku商品的spu:', goods)
    #根据spu找到一级标题　在根据一级标题找到所在的频道
    #获取商品的频道  方便前端通过goods.channel　来获取商品的频道信息
    goods.channel = goods.category1.goodschannel_set.all()[0]
    print('获取当前sku商品的spu的频道:', goods.channel)


    #构建商品的规格键
    # sku_key = [规格1参数id， 规格2参数id， 规格3参数id, ...]
    #获取当前商品的规格参数
    sku_specs = sku.skuspecification_set.order_by('spec_id')    #结果是查询集
    print('获取当前sku商品的规格参数:', sku_specs)

    sku_key = []
    for spec in sku_specs:
        #sku_key 存放当前sku商品的规格参数的选项id
        sku_key.append(spec.option.id)

    #获取当前商品的所有sku
    skus = goods.sku_set.all()      #获取spu的所有sku
    print('获取sku规格参数:',sku_key)
    print('获取当前spu的所有sku商品:', skus)


    #构建不同规格参数选项的sku字典
    spec_sku_dict = {}

    #获取所有sku商品的规格参数选项
    for sku in skus:
        #获取sku的规格参数
        sku_specs = sku.skuspecification_set.order_by('spec_id')

        #组装规格参数－sku字典的键
        key = []
        for spec in sku_specs:
            #获取每个规格的选项id
            key.append(spec.option.id)

        #选择相应的对个选项　得到对应的sku商品
        spec_sku_dict[tuple(key)] = sku.id

    print('获取当前spu的所有sku商品的规格参数:', spec_sku_dict)
    #获取当前spu商品的规格信息
    specs = goods.goodsspecification_set.order_by('id')
    print('获取spu的规格名称:',specs)
    #如果当前sku的规格信息不完整　则不再继续
    print('获取sku_key:',len(sku_key))
    print('获取specs:',len(specs))
    if len(sku_key)<len(specs):
        #该商品的规格信息不完整
        return


    """组装所有spu商品的规格的选项"""
    #enumerate() 给spu商品加上index 组成字典
    for index,spec in  enumerate(specs):

        #复制当前的sku规格键  深拷贝　这里只是借用该列表格式，没有其他用途
        #这里只是借用该列表格式用于在规格参数的sku字典中查询符合当前规格的sku
        key = sku_key[:]

        #该sku商品的选项
        options = spec.specificationoption_set.all()
        for option in options:

            #在规格参数的sku字典中查询符合当前规格的sku

            #得到所有sku规格信息的选项id
            key[index] = option.id
            print('key[index]',key[index])

            #选择选项对应的规格信息的sku商品id 没有就设为none
            option.sku_id = spec_sku_dict.get(tuple(key))
            print('option.sku_id ',option.sku_id )

        #得到所有spu商品的规格信息的选项　
        spec.options = options
    print('获取当前spu的所有sku商品的规格名称', specs)



    # 渲染模板数据　
    context = {
        'categories': categories,
        'goods': goods,
        'specs': specs,
        'sku': sku

    }
    temlates = loader.get_template('detail.html')
    html_text = temlates.render(context)

    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR,'goods/'+str(sku_id)+'.html')

    #写入静态html
    with open(file_path,'w') as f:
        f.write(html_text)






if __name__ == '__main__':
    skus = SKU.objects.get(id=1)
    # for sku in skus:
    #     print(sku.id)
    generate_static_sku_detail_html2(skus.id)