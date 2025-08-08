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

class BillApi():
    def __init__(self):
        super().__init__()

    def getSettlementOrderList(self, driver, options):
        '''
        @Desc    : 获取结算订单列表
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
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/v1/pay/statement/order/list"

        # 当前时间戳（毫秒）
        now_timestamp = int(time.time() * 1000)

        # 当前时间
        now = datetime.now()

        # 一周前的日期
        one_week_ago = now - timedelta(days=7)

        # 一周前的 0 点
        one_week_ago_zero = datetime(one_week_ago.year, one_week_ago.month, one_week_ago.day)
        one_week_ago_timestamp = int(one_week_ago_zero.timestamp() * 1000)

        params = {
            "oec_seller_id": oec_seller_id,
            "aid": "6556",
            "pagination_type": "1",
            "from": "0",
            "size": "5",
            "terminal_type": "1",
            "page_type": "6",
            "settlement_status": "2",
            "bill_period_time_lower": str(one_week_ago_timestamp),
            "bill_period_time_upper": str(now_timestamp),
            "need_total_amount": "false",
            "no_need_sku_record": "false",
            "statement_version": "0",
        }

        request_id = str(uuid.uuid4())
        list_count = 0
        page_number = 1
        page_from = 0
        page_size = 100

        while True:
            params["from"] = str(page_from)
            params["size"] = str(page_size)

            res = executeService.request(driver=driver, url=url, params=params, method="GET")
            temp_res = json.loads(res)

            temp_data = temp_res.get("data", {})
            total_count = temp_data.get("total_record", 0)
            temp_list = temp_data.get("order_records", [])

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
            page_from += page_size

            # 休息一会
            time.sleep(0.3)

    def getSettlementOrderDetail(self, driver, options):
        '''
        @Desc    : 获取订单结算明细
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        if "statement_detail_id" not in options:
            raise TaskParamsException("缺少 statement_detail_id")
        statement_detail_id = options.get("statement_detail_id")

        # 访问订单页面
        driver.get("https://api16-normal-sg.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(0.1)

        # URL
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/v1/pay/statement/transaction/detail"

        params = {
            "locale": "zh-CN",
            "language": "zh-CN",
            "oec_seller_id": oec_seller_id,
            "aid": "6556",
            "terminal_type": "1",
            "page_type": "8",
            "statement_detail_id": statement_detail_id,
            "statement_version": "0",
        }

        res = executeService.request(driver=driver, url=url, params=params, method="GET")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)