import json
from rpa_common import Common
from rpa_tiktok.service.TiktokService import TiktokService
from rpa_tiktok.api.OptimizerApi import OptimizerApi

common = Common()
tiktokService = TiktokService()
optimizerApi = OptimizerApi()

class OptimizerService():
    def __init__(self):
        super().__init__()

    def getOptimizerTitle(self, driver, shop_data, options):
        '''
        @Desc    : 获取优化标题
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 优化标题
        optimizerApi.getOptimizerTitle(driver, options)

    def optimizerTitle(self, driver, shop_data, options):
        '''
        @Desc    : 优化标题
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 优化标题
        optimizerApi.optimizerTitle(driver, options)