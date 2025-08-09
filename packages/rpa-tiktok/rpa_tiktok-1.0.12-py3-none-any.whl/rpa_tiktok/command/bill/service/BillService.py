import json

from rpa_common import Common
from rpa_tiktok.service.TiktokService import TiktokService
from rpa_tiktok.api.BillApi import BillApi

common = Common()
billApi = BillApi()
tiktokService = TiktokService()

class BillService():
    def __init__(self):
        super().__init__()

    def getSettlementOrderList(self, driver, shop_data, options):
        '''
        @Desc    : 获取结算订单列表
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取结算订单列表
        billApi.getSettlementOrderList(driver, options)

    def getSettlementOrderDetail(self, driver, shop_data, options):
        '''
        @Desc    : 获取订单结算明细
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取订单结算明细
        billApi.getSettlementOrderDetail(driver, options)