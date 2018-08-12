"""
创建索引类，来指明让搜索引擎对哪些字段建立索引，也就是可以通过哪些字段的关键字来检索数据
创建索引类
通过使用haystack来调用Elasticsearch搜索引擎
：安装haystack和elasticsearch模块
：注册应用
：配置haystack使用的搜索引擎后端
：创建索引类
"""

from haystack import indexes
from .models import SKU

class SKUIndex(indexes.SearchIndex,indexes.Indexable):
    """索引表模型类"""

    #创建搜索的关键字
    #document 指明以text为搜索关键词 document=true 表名该字段是主要进行关键字查询字段
    #use_template　在模板文件中指明要建立索引的字段

    #模板中的字段
    #此模板指明当将关键词通过text参数名传递时，可以通过sku的name、caption、id来进行关键字索引查询
    text = indexes.CharField(document=True,use_template=True)

    #获取需要建立索引的模型类
    def get_model(self):
        """返回建立索引的模型类"""
        return SKU

    #获取需要建立索引的查询集数据
    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)