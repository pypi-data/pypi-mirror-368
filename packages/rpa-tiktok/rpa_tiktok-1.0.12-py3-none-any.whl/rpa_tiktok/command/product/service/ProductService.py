import json
from rpa_common import Common
from rpa_tiktok.service.TiktokService import TiktokService
from rpa_tiktok.api.ProductApi import ProductApi

common = Common()
productApi = ProductApi()
tiktokService = TiktokService()

class ProductService():
    def __init__(self):
        super().__init__()

    def getCategory(self, driver, shop_data, options):
        '''
        @Desc    : 获取类目
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取店铺产品
        productApi.getCategory(driver, options)

    def getShopProductList(self, driver, shop_data, options):
        '''
        @Desc    : 获取店铺产品
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取店铺产品
        productApi.getShopProductList(driver, options)

    def getGlobalProductList(self, driver, shop_data, options):
        '''
        @Desc    : 获取全球产品
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取全球产品
        productApi.getGlobalProductList(driver, options)

    def getGlobalProductDetail(self, driver, shop_data, options):
        '''
        @Desc    : 获取全球产品详情
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取全球产品详情
        productApi.getGlobalProductDetail(driver, options)

    def getShopProductDetail(self, driver, shop_data, options):
        '''
        @Desc    : 获取店铺产品详情
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取店铺产品详情
        productApi.getShopProductDetail(driver, options)

    def createGlobalProduct(self, driver, shop_data, options):
        '''
        @Desc    : 创建全球产品
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取全球产品详情
        productApi.createGlobalProduct(driver, options)

    def getTitleCategory(self, driver, shop_data, options):
        '''
        @Desc    : 根据标题获取推荐类目
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取全球产品详情
        productApi.getTitleCategory(driver, options)

    def getCategoryProperties(self, driver, shop_data, options):
        '''
        @Desc    : 获取类目属性
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取全球产品详情
        productApi.getCategoryProperties(driver, options)

    def uploadImg(self, driver, shop_data, options):
        '''
        @Desc    : 上传图片
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取全球产品详情
        productApi.uploadImg(driver, options)

    def getProductRating(self, driver, shop_data, options):
        '''
        @Desc    : 获取商品评分
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取商品评分
        productApi.getProductRating(driver, options)

    def removeProduct(self, driver, shop_data, options):
        '''
        @Desc    : 下架店铺产品
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 下架店铺产品
        productApi.removeProduct(driver, options)

    def estimateShippingCost(self, driver, shop_data, options):
        '''
        @Desc    : 获取产品预估物流成本
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取产品预估物流成本
        productApi.estimateShippingCost(driver, options)

    def getProductBundle(self, driver, shop_data, options):
        '''
        @Desc    : 获取商品搭配
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取商品搭配
        productApi.getProductBundle(driver, options)

    def publishGlobalProduct(self, driver, shop_data, options):
        '''
        @Desc    : 发布到指定市场
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 发布到指定市场
        productApi.publishGlobalProduct(driver, options)

    def mcalculatePrice(self, driver, shop_data, options):
        '''
        @Desc    : 计算价格
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 发布到指定市场
        productApi.mcalculatePrice(driver, options)