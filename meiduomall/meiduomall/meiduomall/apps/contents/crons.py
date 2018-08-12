from collections import OrderedDict
from django.conf import settings
from django.template import loader
import os
import time

from goods.models import GoodsChannel
from .models import ContentCategory

print(os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'index.html'))
def generate_static_index_html():
    """
    生成静态的主页html文件
    """
    print('%s: generate_static_index_html' % time.ctime())
    # 商品频道及分类菜单
    # 使用有序字典保存类别的顺序
    # categories = {
    #     1: { # 组1
    #         'channels': [{'id':, 'name':, 'url':},{}, {}...],
    #         'sub_cats': [{'id':, 'name':, 'sub_cats':[{},{}]}, {}, {}, ..]
    #     },
    #     2: { # 组2
    #
    #     }
    # }
    #封装数据
    categories = OrderedDict()
    #获取所有频道数据
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    for channel in channels:

        group_id = channel.group_id  # 当前组

        #一个组表示频道列表的一个频道，一个频道里有多个商品分类
        if group_id not in categories: #将同一个频道的商品分类放到一个频道
            #封装成一个频道下展示多个商品分类，子分类再展示子分类，
            categories[group_id] = {'channels': [], 'sub_cats': []}

        #频道里的商品分类数据
        cat1 = channel.category  # 当前频道的类别

        # 追加当前频道　同一个频道的顶级商品类　例如：手机/相机/数码
        categories[group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })
        # print('频道一级>>>>>>')
        # print(categories[group_id]['channels'])

        # 构建当前类别的子类别
        #根据一级类别获取二级类别信息  商品类别模型类是自关联关系　
        for cat2 in cat1.goodscategory_set.all():  #获取二级类别
            #给二级类别对象添加子类别属性
            cat2.sub_cats = []
            # print('二级>>>>>')
            print(cat2)
            for cat3 in cat2.goodscategory_set.all():   #获取三级类别
                cat2.sub_cats.append(cat3)            #封装二级类别数据
                # print('二级>>>>>')
                # print(cat2.sub_cats)
                # print('三级>>>')
                # print(cat3)
            categories[group_id]['sub_cats'].append(cat2)   #封装一级类别数据





    # 广告内容
    contents = {}
    #获取广告分类信息  获取所有广告类别数据
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        #获取分类广告的具体信息　　 一个类别的广告展示多个广告
        #cat.content_set 获取一个广告类别下的所有广告信息
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    # 渲染模板
    context = {
        'categories': categories,
        'contents': contents    #前端根据广告的放置位置的key 来取出对应的广告　再取出广告信息
    }
    template = loader.get_template('index.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)