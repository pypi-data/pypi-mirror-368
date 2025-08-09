import json
from rpa_common import Common
from rpa_tiktok.service.TiktokService import TiktokService
from rpa_tiktok.api.UnionApi import UnionApi

common = Common()
unionApi = UnionApi()
tiktokService = TiktokService()

class UnionService():
    def __init__(self):
        super().__init__()

    def getCreatorOrderList(self, driver, shop_data, options):
        '''
        @Desc    : 获取联盟达人订单
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取联盟达人订单
        unionApi.getCreatorOrderList(driver, options)

    def getOpenCollaboration(self, driver, shop_data, options):
        '''
        @Desc    : 获取联盟公开合作
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取联盟达人订单
        unionApi.getOpenCollaboration(driver, options)