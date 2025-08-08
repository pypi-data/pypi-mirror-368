import json
import time
import uuid
from datetime import datetime, timedelta
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from rpa_common.exceptions import TaskParamsException
from rpa_common.request.TaskRequest import TaskRequest
from rpa_common.service.ExecuteService import ExecuteService

taskRequest = TaskRequest()
executeService = ExecuteService()

class ShopApi():
    def __init__(self):
        super().__init__()

    def getInfoList(self, driver, options):
        '''
        @Desc    : 获取店铺信息
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        # 访问订单页面
        driver.get("https://api16-normal-sg.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(0.1)

        # URL
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/v1/shop_im/multi_shop/user/get_info_list"

        params = {
            "locale": "zh-CN",
            "language": "zh-CN",
            "oec_seller_id": oec_seller_id,
            "aid": "6556",
        }

        res = executeService.request(driver=driver, url=url, params=params, method="GET")
        return res

    def getSellerInfo(self, driver, options):
        '''
        @Desc    : 获取商家信息
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        # 访问订单页面
        driver.get("https://api16-normal-sg.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(0.1)

        # URL
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/v1/seller/entity/get"

        params = {
            "locale": "zh-CN",
            "language": "zh-CN",
            "oec_seller_id": oec_seller_id,
            "aid": "6556"
        }

        res = executeService.request(driver=driver, url=url, params=params, method="GET")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)

    def getWarehouseList(self, driver, options):
        '''
        @Desc    : 获取仓库信息
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        # 访问
        driver.get("https://api16-normal-sg.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(0.1)

        # URL
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/v3/seller/global/warehouses/get"

        params = {
            "locale": "zh-CN",
            "language": "zh-CN",
            "oec_seller_id": oec_seller_id,
            "aid": "6556"
        }

        res = executeService.request(driver=driver, url=url, params=params, method="GET")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)