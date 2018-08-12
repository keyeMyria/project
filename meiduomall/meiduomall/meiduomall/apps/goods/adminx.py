"""xadmin站点配置"""

import xadmin
from xadmin import views
from . import models

#创建xadmin站点模型类管理器
class GoodsManangerBases(object):
    """xamdin站点模型类管理器－基本配置"""
    #基本配置－开启主题切换
    enable_themes = True
    use_bootswatch = True


# xadmin的全局配置 可以在任意应用模块中设置都可以生效
class GlobalSettings(object):
    """xadmin的全局配置"""
    site_title = "美多商城运营管理系统"  # 设置站点标题
    site_footer = "美多商城集团有限公司"  # 设置站点的页脚
    menu_style = "accordion"  # 设置菜单折叠


#设置xadmin站点视图的基本配置默认模型类
xadmin.site.register(views.BaseAdminView, GoodsManangerBases)
# 设置xadmin站点视图的全局配置模型类
xadmin.site.register(views.CommAdminView, GlobalSettings)


#goods模型类管理器
class SKUAdmin(object):
    """sku商品站点管理类"""
    #模型类图标
    model_icon = 'fa fa-gift'
    # 搜索框可以搜索的字段
    search_fields = ['id', 'name']
    #列表展示字段
    list_display = ['id', 'name', 'price', 'stock', 'sales', 'comments']
    #可以编辑的字段
    list_editable = ['price', 'stock']
    #只读字段
    readonly_fields = ['sales', 'comments']

    # 站点修改数据时　提交也不生成商品详情数据
    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)

#站点修改数据时　提交也不生成商品详情数据
class SKUSpecificationAdmin(object):
    """SKUSpecification站点管理器"""
    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        #站点修改数据时　提交也不生成商品详情数据
        generate_static_sku_detail_html.delay(obj.sku.id)

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)


class SKUImageAdmin(object):
    """SKUImageAdmi站点管理器"""


    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

        # 设置SKU默认图片
        sku = obj.sku
        if not sku.default_image_url:
            sku.default_image_url = obj.image.url
            sku.save()

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)



#goods站点模型类注册到xadmin站点
xadmin.site.register(models.GoodsChannel)
xadmin.site.register(models.GoodsCategory)
xadmin.site.register(models.Goods)
xadmin.site.register(models.Brand)
xadmin.site.register(models.GoodsSpecification)
xadmin.site.register(models.SpecificationOption)
xadmin.site.register(models.SKU,SKUAdmin)
xadmin.site.register(models.SKUSpecification,SKUSpecificationAdmin)
xadmin.site.register(models.SKUImage,SKUImageAdmin)
