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

class OrderApi():
    def __init__(self):
        super().__init__()

    def getOrderList(self, driver, options):
        '''
        @Desc    : 获取订单列表
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

        # 执行 JS 发起 fetch 请求
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/fulfillment/order/list"

        params = {
            "oec_seller_id":oec_seller_id,
            "aid": "6556",
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
            "sort_info": "6",
            "search_condition": {
                "condition_list": {
                    "time_order_created": {
                        "value": [
                            str(one_month_ago_timestamp),
                            str(now_timestamp)
                        ]
                    }
                }
            },
            "count": 20,
            "pagination_type": 0,
            "offset": 0,
            "search_cursor": "",
            "extra_data_list": [
                "48_hours_dispatch_tag",
                "split_combine_tag_v1",
                "free_sample_tag_v1",
                "hazmat_order_tag",
                "made_to_order_tag",
                "pre_order_tag",
                "pre_sell_tag",
                "zero_lottery_tag",
                "gift_insurance_tag",
                "internal_purchase_tag",
                "replacement_order_tag_v1",
                "risk_order_tag_v1",
                "combo_sku_tag",
                "refundable_sample_tag",
                "split_package_type_tag",
                "two_day_delivery",
                "DT_order"
            ]
        }

        request_id = str(uuid.uuid4())

        list_count = 0
        page_number = 1
        page_offset = 0
        page_size = 50

        while True:
            data["offset"] = page_offset
            data["count"] = page_size

            res = executeService.request(driver=driver, url=url, params=params, data=data, method="POST")
            temp_res = json.loads(res)

            temp_data = temp_res.get("data", {})
            total_count = temp_data.get("total_count", 0)
            temp_list = temp_data.get("main_orders", [])
            print("总条数", total_count)

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
            print("当前条数", list_count)
            if list_count >= total_count:
                break

            # 下一页
            page_number += 1
            page_offset += page_size

            # 休息一会
            time.sleep(0.3)

    def getOrderDetail(self, driver, options):
        '''
        @Desc    : 获取店铺订单详情
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        if "site" not in options:
            raise TaskParamsException("缺少 site")
        site = options.get("site")

        if "main_order_id" not in options:
            raise TaskParamsException("缺少 main_order_id")
        main_order_id = options.get("main_order_id")

        # 访问订单页面
        driver.get(f"https://seller.tiktokshopglobalselling.com/order/detail?order_no={main_order_id}&shop_region={site}")

        # 等待页面加载
        time.sleep(0.1)

        # 执行 JS 发起 fetch 请求
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/fulfillment/order/get"

        params = {
            "locale": "zh-CN",
            "language": "zh-CN",
            "oec_seller_id":oec_seller_id,
            "aid": "6556",
        }

        data = {
            "main_order_id": [
                main_order_id
            ],
            "extra_data_list": [
                "48_hours_dispatch_tag",
                "split_combine_tag_v1",
                "free_sample_tag_v1",
                "hazmat_order_tag",
                "made_to_order_tag",
                "pre_order_tag",
                "pre_sell_tag",
                "zero_lottery_tag",
                "gift_insurance_tag",
                "internal_purchase_tag",
                "replacement_order_tag_v1",
                "risk_order_tag_v1",
                "combo_sku_tag",
                "refundable_sample_tag",
                "split_package_type_tag",
                "two_day_delivery",
                "DT_order"
            ]
        }

        res = executeService.request(driver=driver, url=url, params=params, data=data, method="POST")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)

    def getOrderReturnList(self, driver, options):
        '''
        @Desc    : 获取退货退款
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

        # 执行 JS 发起 fetch 请求
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/v1/reverse/component/orders/list"

        params = {
            "oec_seller_id":oec_seller_id,
            "aid": "6556",
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
            "pagination_type": 0,
            "count": 20,
            "offset": 0,
            "search_condition": {
                "time_range_comp": {
                    "str_value_list": [
                        str(one_month_ago_timestamp),
                        str(now_timestamp)
                    ]
                },
                "tab": {
                    "str_value_list": [
                        "100"
                    ]
                },
                "order_sort_comp": {
                    "str_value_list": [
                        "OrderSort_UPADTE_TIME_DESC"
                    ]
                }
            },
            "component_version": "hit_opt_aware_revamp"
        }

        request_id = str(uuid.uuid4())

        list_count = 0
        page_number = 1
        page_offset = 0
        page_size = 20

        while True:
            data["offset"] = page_offset
            data["count"] = page_size

            res = executeService.request(driver=driver, url=url, params=params, data=data, method="POST")
            temp_res = json.loads(res)

            temp_data = temp_res.get("data", {})
            total_count = temp_data.get("total_count", 0)
            temp_list = temp_data.get("cards", [])
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
            page_offset += page_size

            # 休息一会
            time.sleep(0.3)