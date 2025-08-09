import json
from rpa_common import Common
from rpa_tiktok.service.TiktokService import TiktokService
from rpa_tiktok.api.OrderApi import OrderApi

common = Common()
tiktokService = TiktokService()
orderApi = OrderApi()

class OrderService():
    def __init__(self):
        super().__init__()

    def getOrderList(self, driver, shop_data, options):
        '''
        @Desc    : 获取订单列表
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 优化标题
        orderApi.getOrderList(driver, options)

    def getOrderDetail(self, driver, shop_data, options):
        '''
        @Desc    : 获取店铺订单详情
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 优化标题
        orderApi.getOrderDetail(driver, options)

    def getOrderReturnList(self, driver, shop_data, options):
        '''
        @Desc    : 获取退货退款
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 优化标题
        orderApi.getOrderReturnList(driver, options)