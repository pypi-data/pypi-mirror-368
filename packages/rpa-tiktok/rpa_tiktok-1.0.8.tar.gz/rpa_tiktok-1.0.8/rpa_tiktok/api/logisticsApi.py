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

class LogisticsApi():
    def __init__(self):
        super().__init__()

    def getPackagesList(self, driver, options):
        '''
        @Desc    : 获取物流记录
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
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/v1/seller/package/list"

        params = {
            "locale": "zh-CN",
            "language": "zh-CN",
            "oec_seller_id": oec_seller_id,
            "aid": "6556",
        }

        # 当前时间戳（秒）
        now_timestamp = int(time.time())

        # 获取当前日期
        now = datetime.now()

        # 获取一个月前的日期
        one_month_ago = now - timedelta(days=30)

        # 获取一个月前当天的0点时间戳（秒）
        one_month_ago_zero = datetime(one_month_ago.year, one_month_ago.month, one_month_ago.day)
        one_month_ago_timestamp = int(one_month_ago_zero.timestamp())

        data = {
            "tab": 1,
            "search_condition": {
                "pkg_tag": [],
                "order_ids": [],
                "tracking_nos": [],
                "package_ids": [],
                "product_ids": [],
                "time_range": [
                    {
                        "start_time": one_month_ago_timestamp,
                        "end_time": now_timestamp,
                        "time_range_type": 1
                    }
                ],
                "logistics_types": [
                    1
                ],
                "shipment_types": [
                    1,
                    2
                ],
                "biz_source": [
                    1
                ]
            },
            "pagination": {
                "page": 1,
                "size": 20
            },
            "pagination_type": 1,
            "search_cursor": ""
        }

        request_id = str(uuid.uuid4())

        list_count = 0
        page_number = 1
        page_size = 50

        while True:
            data["pagination"]['page'] = page_number
            data['pagination']["size"] = page_size

            res = executeService.request(driver=driver, url=url, params=params, data=data, method="POST")
            temp_res = json.loads(res)

            temp_data = temp_res.get("data", {})
            total_count = temp_data.get("total_count", 0)
            temp_list = temp_data.get("packages", [])

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