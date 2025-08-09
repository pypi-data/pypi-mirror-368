import json
from rpa_common import Common
from rpa_tiktok.service.TiktokService import TiktokService
from rpa_tiktok.api.ShopApi import ShopApi

common = Common()
shopApi = ShopApi()
tiktokService = TiktokService()

class ShopService():
    def __init__(self):
        super().__init__()

    def getSellerInfo(self, driver, shop_data, options):
        '''
        @Desc    : 获取商家信息
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取商家信息
        shopApi.getSellerInfo(driver, options)

    def getWarehouseList(self, driver, shop_data, options):
        '''
        @Desc    : 获取仓库信息
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取商家信息
        shopApi.getWarehouseList(driver, options)
