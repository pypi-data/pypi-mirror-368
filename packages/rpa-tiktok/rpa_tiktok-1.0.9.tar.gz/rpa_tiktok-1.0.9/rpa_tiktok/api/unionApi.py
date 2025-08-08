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

class UnionApi():
    def __init__(self):
        super().__init__()

    def getCreatorOrderList(self, driver, options):
        '''
        @Desc    : 获取联盟达人订单
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        if "site" not in options:
            raise TaskParamsException("缺少 site")
        site = options.get("site")

        # 访问订单页面
        driver.get("https://affiliate.tiktokglobalshop.com/api/v1/affiliate/orders")

        # 等待页面加载
        time.sleep(0.1)

        # 执行 JS 发起 fetch 请求
        url = "https://affiliate.tiktokglobalshop.com/api/v1/affiliate/orders"

        params = {
            "user_language": "zh-CN",
            "browser_language": "zh-CN",
            "aid": "6556",
            "app_name": "i18n_ecom_alliance",
            "device_id": "0",
            "oec_seller_id": oec_seller_id,
            "shop_region": site,
        }

        # 当前时间戳（毫秒）
        now_timestamp = int(time.time() * 1000)

        # 获取当前日期
        now = datetime.now()

        # 获取一个月前的日期
        one_month_ago = now - timedelta(days=30)

        # 获取一个月前当天的0点时间戳（毫秒）
        one_month_ago_zero = datetime(one_month_ago.year, one_month_ago.month, one_month_ago.day)
        one_month_ago_timestamp = int(one_month_ago_zero.timestamp() * 1000)

        data = {
            "conditions": {
                "time_period": {
                    "beginning_time": str(one_month_ago_timestamp),
                    "ending_time": str(now_timestamp),
                },
                "bill_type": 1,
                "cod_type": 0,
                "order_status": 0
            },
            "page": 1,
            "page_size": 50,
            "country": site
        }

        request_id = str(uuid.uuid4())

        list_count = 0
        page_number = 1
        page_size = 50

        while True:
            data["page"] = page_number
            data["page_size"] = page_size

            res = executeService.request(driver=driver, url=url, params=params, data=data, method="POST")
            temp_res = json.loads(res)

            total_count = temp_res.get("total_count", 0)
            temp_list = temp_res.get("orders", [])
            print("total_count", total_count)

            if page_number > 1 and not temp_list:
                break

            temp_count = len(temp_list)

            # 保存数据
            options['request_id'] = request_id
            options['page_number'] = page_number
            options['page_size'] = page_size
            options['list_count'] = temp_count
            options['total_count'] = total_count
            options['response'] = res
            taskRequest.save(options)

            list_count += temp_count
            if list_count >= total_count:
                break

            # 下一页
            page_number += 1

            # 休息一会
            time.sleep(0.3)

    def getOpenCollaboration(self, driver, options):
        '''
        @Desc    : 获取联盟公开合作
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        if "site" not in options:
            raise TaskParamsException("缺少 site")
        site = options.get("site")

        # 访问订单页面
        driver.get("https://affiliate.tiktokglobalshop.com/api/v1/affiliate/open_collaboration/promote_products/list")

        # 等待页面加载
        time.sleep(0.1)

        # 执行 JS 发起 fetch 请求
        url = "https://affiliate.tiktokglobalshop.com/api/v1/affiliate/open_collaboration/promote_products/list"

        params = {
            "user_language": "zh-CN",
            "browser_language": "zh-CN",
            "aid": "6556",
            "app_name": "i18n_ecom_alliance",
            "device_id": "0",
            "oec_seller_id": oec_seller_id,
            "shop_region": site,
        }

        data = {
            "shop_id": oec_seller_id,
            "cur_page": 1,
            "page_size": 100,
            "search_params": []
        }

        request_id = str(uuid.uuid4())

        list_count = 0
        page_number = 1
        page_size = 100

        while True:
            data["cur_page"] = page_number
            data["page_size"] = page_size

            res = executeService.request(driver=driver, url=url, params=params, data=data, method="POST")
            temp_res = json.loads(res)

            total_count = temp_res.get("total_num", 0)
            temp_list = temp_res.get("products", [])
            print("total_count", total_count)

            if page_number > 1 and not temp_list:
                break

            temp_count = len(temp_list)

            # 保存数据
            options['request_id'] = request_id
            options['page_number'] = page_number
            options['page_size'] = page_size
            options['list_count'] = temp_count
            options['total_count'] = total_count
            options['response'] = res
            taskRequest.save(options)

            list_count += temp_count
            if list_count >= total_count:
                break

            # 下一页
            page_number += 1

            # 休息一会
            time.sleep(0.3)