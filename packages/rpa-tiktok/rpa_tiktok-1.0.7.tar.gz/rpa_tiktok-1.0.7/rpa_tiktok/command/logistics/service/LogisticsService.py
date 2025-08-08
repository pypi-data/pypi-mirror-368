import json
from rpa_common import Common
from rpa_tiktok.service.TiktokService import TiktokService
from rpa_tiktok.api.LogisticsApi import LogisticsApi

common = Common()
tiktokService = TiktokService()
logisticsApi = LogisticsApi()

class LogisticsService():
    def __init__(self):
        super().__init__()

    def getPackagesList(self, driver, shop_data, options):
        '''
        @Desc    : 获取包裹列表
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 优化标题
        logisticsApi.getPackagesList(driver, options)