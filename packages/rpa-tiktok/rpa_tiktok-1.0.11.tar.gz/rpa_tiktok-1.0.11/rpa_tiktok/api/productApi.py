import json
import time
import hashlib
import urllib.request
import os
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

class ProductApi():
    def __init__(self):
        super().__init__()

    def getCategory(self, driver, options):
        '''
        @Desc    : 获取类目
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        # 访问页面
        driver.get("https://api16-normal-useast1a.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(10)

        # 执行 JS 发起 fetch 请求
        url = "https://api16-normal-useast1a.tiktokshopglobalselling.com/api/v1/product/global/product_creation/preload_all_categories"

        params = {
            "oec_seller_id": oec_seller_id,
            "aid": "6556"
        }

        res = executeService.request(driver=driver, url=url, params=params, method="GET")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)

    def getShopProductList(self, driver, options):
        '''
        @Desc    : 获取店铺产品
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        # 访问页面
        driver.get("https://api16-normal-sg.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(0.1)

        # 执行 JS 发起 fetch 请求
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/v1/product/local/products/list"

        params = {
            "oec_seller_id": oec_seller_id,
            "aid": "6556",
            "tab_id": "1",
            # "search_content": "1",
            "page_number": "1",
            "page_size": "100",
            "sku_number": "1",
            "product_sort_fields": "3",
            "product_sort_types": "0",
        }

        request_id = str(uuid.uuid4())
        list_count = 0
        page_number = 1
        page_size = 100

        while True:
            params["page_number"] = str(page_number)
            params["page_size"] = str(page_size)

            res = executeService.request(driver=driver, url=url, params=params, method="GET")
            temp_res = json.loads(res)

            temp_data = temp_res.get("data", {})
            total_count = temp_data.get("total_product_count", 0)
            temp_list = temp_data.get("products", [])

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

    def getGlobalProductList(self, driver, options):
        '''
        @Desc    : 获取全球产品
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        # 访问页面
        driver.get("https://api16-normal-useast1a.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(0.1)

        # 执行 JS 发起 fetch 请求
        url = "https://api16-normal-useast1a.tiktokshopglobalselling.com/api/v1/product/global/products/list"

        params = {
            "oec_seller_id": oec_seller_id,
            "aid": "6556",
            "tab_id": "1",
            "sort_type": "0",
            "sort_field": "0",
            "page_number": "1",
            "page_size": "100",
            "sku_number": "1",
            "filter_new_pop": "true",
        }

        request_id = str(uuid.uuid4())

        list_count = 0
        page_number = 1
        page_size = 100

        while True:
            params["page_number"] = str(page_number)
            params["page_size"] = str(page_size)

            res = executeService.request(driver=driver, url=url, params=params, method="GET")
            temp_res = json.loads(res)

            temp_data = temp_res.get("data", {})
            total_count = temp_data.get("total_product_count", 0)
            temp_list = temp_data.get("products", [])

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

    def getGlobalProductDetail(self, driver, options):
        '''
        @Desc    : 获取全球产品详情
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")
        product_id = options.get("product_id")

        # 访问页面
        driver.get("https://api16-normal-useast1a.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(0.1)

        # 执行 JS 发起 fetch 请求
        url = "https://api16-normal-useast1a.tiktokshopglobalselling.com/api/v1/product/global/product/get"

        params = {
            "oec_seller_id": oec_seller_id,
            "aid": "6556",
            "product_id": product_id,
        }

        res = executeService.request(driver=driver, url=url, params=params, method="GET")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)

    def getShopProductDetail(self, driver, options):
        '''
        @Desc    : 获取店铺产品详情
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        if "site" not in options:
            raise TaskParamsException("缺少 site")
        site = options.get("site")

        if "product_id" not in options:
            raise TaskParamsException("缺少 product_id")
        product_id = options.get("product_id")

        # 访问页面
        driver.get(f"https://seller.tiktokshopglobalselling.com/product/edit/{product_id}?shop_region={site}")

        # 等待页面加载
        time.sleep(0.1)

        # 执行 JS 发起 fetch 请求
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/v1/product/local/product/get"

        params =  {
            "locale": "zh-CN",
            "language": "zh-CN",
            "oec_seller_id": oec_seller_id,
            "aid": "6556",
            "app_name": "i18n_ecom_shop",
            "product_id": product_id
        }

        res = executeService.request(driver=driver, url=url, params=params, method="GET")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)

    def getTitleCategory(self, driver, options):
        '''
        @Desc    : 根据标题获取推荐类目
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "product_id" not in options:
            raise TaskParamsException("缺少 product_id")
        oec_seller_id = options.get("shop_id")

        if "title" not in options:
            raise TaskParamsException("缺少 title")
        title = options.get("title")

        # 访问订单页面
        driver.get("https://api16-normal-useast1a.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(0.1)

        # URL
        url = "https://api16-normal-useast1a.tiktokshopglobalselling.com/api/v1/product/global/category_rec/list"

        params = {
            "locale": "zh-CN",
            "language": "zh-CN",
            "oec_seller_id": oec_seller_id,
            "aid": "6556",
            "title": title,
        }

        res = executeService.request(driver=driver, url=url, params=params, method="GET")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)

    def uploadImg(self, driver, options):
        '''
        @Desc    : 上传图片
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        if "url" not in options:
            raise TaskParamsException("缺少 url")
        file_url = options.get("url")

        # 访问订单页面
        driver.get("https://api16-normal-useast1a.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(10)

        # URL
        url = "https://api16-normal-useast1a.tiktokshopglobalselling.com/api/v1/product/global/material_center/material/create"

        params = {
            "locale": "zh-CN",
            "language": "zh-CN",
            "oec_seller_id": oec_seller_id,
            "aid": "6556"
        }

        filename = os.path.basename(file_url)
        name, extension = os.path.splitext(filename)
        name_md5 = hashlib.md5(name.encode('utf-8')).hexdigest()
        material_name = f"{name_md5}{extension}"

        print("name_md5", name_md5)
        print("extension", extension)

        data = {
            "material_name": material_name,
            "parent_folder_id": 3,
            "material_type": 1,
        }

        res = executeService.request_file(driver=driver, url=url, params=params, file_url=file_url, data=data, method="POST")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)

    def getCategoryProperties(self, driver, options):
        '''
        @Desc    : 获取类目属性
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        if "category_id" not in options:
            raise TaskParamsException("缺少 category_id")
        category_id = options.get("category_id")

        # 访问订单页面
        driver.get("https://api16-normal-useast1a.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(0.1)

        # URL
        url = "https://api16-normal-useast1a.tiktokshopglobalselling.com/api/v1/product/global/category/bind_info/get"

        params = {
            "locale": "zh-CN",
            "language": "zh-CN",
            "oec_seller_id": oec_seller_id,
            "aid": "6556",
            "category_id": category_id,
        }

        res = executeService.request(driver=driver, url=url, params=params, method="GET")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)

    def getProductRating(self, driver, options):
        '''
        @Desc    : 获取商品评分
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        # 访问页面
        driver.get("https://api16-normal-sg.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(0.1)

        # 执行 JS 发起 fetch 请求
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/v1/review/biz_backend/list"

        params = {
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
            "review_start_time": one_month_ago_timestamp,
            "review_end_time": now_timestamp,
            "page": 1,
            "size": 50
        }

        request_id = str(uuid.uuid4())

        list_count = 0
        page_number = 1
        page_size = 50

        while True:
            params["page"] = page_number
            params["size"] = page_size

            res = executeService.request(driver=driver, url=url, params=params, data=data, method="POST")
            temp_res = json.loads(res)

            temp_data = temp_res.get("data", {})
            total_count = temp_data.get("total", 0)
            temp_list = temp_data.get("list", [])

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

    def removeProduct(self, driver, options):
        '''
        @Desc    : 下架店铺产品
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        if "product_id" not in options:
            raise TaskParamsException("缺少 product_id")
        product_id = options.get("product_id")

        # 访问订单页面
        driver.get("https://api16-normal-sg.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(0.1)

        # URL
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/v1/product/products/deactivate"

        params = {
            "locale": "zh-CN",
            "language": "zh-CN",
            "oec_seller_id": oec_seller_id,
            "aid": "6556"
        }

        data = {
            "product_ids": [
                product_id
            ],
            "sale_platforms": [
                0
            ]
        }

        res = executeService.request(driver=driver, url=url, params=params, data=data, method="POST")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)

    def createGlobalProduct(self, driver, options):
        '''
        @Desc    : 创建全球产品
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        if "product" not in options:
            raise TaskParamsException("缺少 product")
        product = options.get("product")

        # 访问订单页面
        driver.get("https://api16-normal-useast1a.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(10)

        # URL
        url = "https://api16-normal-useast1a.tiktokshopglobalselling.com/api/v1/product/global/product/save_live"

        params = {
            "locale": "zh-CN",
            "language": "zh-CN",
            "oec_seller_id": oec_seller_id,
            "aid": "6556"
        }

        data = {
            "product": json.loads(product)
        }

        res = executeService.request(driver=driver, url=url, params=params, data=data, method="POST")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)

    def estimateShippingCost(self, driver, options):
        '''
        @Desc    : 获取产品预估物流成本
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        warehouse_id = options.get("warehouse_id")
        package_weight = options.get("package_weight")
        category_id = options.get("category_id")
        package_dimension_unit = options.get("package_dimension_unit")
        package_width = options.get("package_width")
        package_height = options.get("package_height")
        package_length = options.get("package_length")
        site = options.get("site")
        product_id = options.get("product_id")

        # 访问页面
        driver.get(f"https://seller.tiktokshopglobalselling.com/product/edit/{product_id}?shop_region={site}")

        # 等待页面加载
        time.sleep(0.1)

        # URL
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/v1/product/shipping/fee/estimate"

        params = {
            "locale": "zh-CN",
            "language": "zh-CN",
            "oec_seller_id": oec_seller_id,
            "aid": "6556"
        }

        data = {
            "warehouse_ids": [],
            "warehouse_id": warehouse_id,
            "package_weight": str(package_weight),
            "category_id": category_id,
            "product_properties": [],
            "package_dimension_unit": package_dimension_unit,
            "package_width": package_width,
            "package_height": package_height,
            "package_length": package_length
        }

        res = executeService.request(driver=driver, url=url, params=params, data=data, method="POST")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)

    def getProductBundle(self, driver, options):
        '''
        @Desc    : 获取商品搭配
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        # 访问页面
        driver.get("https://api16-normal-sg.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(0.1)

        # 执行 JS 发起 fetch 请求
        url = "https://api16-normal-sg.tiktokshopglobalselling.com/api/v1/product/local/bundles/list"

        params = {
            "oec_seller_id": oec_seller_id,
            "aid": "6556",
        }

        data = {
            "page_number": 1,
            "page_size": 50
        }

        request_id = str(uuid.uuid4())

        list_count = 0
        page_number = 1
        page_size = 50

        while True:
            params["page"] = page_number
            params["size"] = page_size

            res = executeService.request(driver=driver, url=url, params=params, data=data, method="POST")
            temp_res = json.loads(res)

            temp_data = temp_res.get("data", {})
            total_count = temp_data.get("total_bundle_count", 0)
            temp_list = temp_data.get("bundle_overviews", [])

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

    def publishGlobalProduct(self, driver, options):
        '''
        @Desc    : 发布到指定市场
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        product_id = options.get("product_id")
        regions = options.get("regions")
        sku_params = options.get("sku_params")
        region_product_params = options.get("region_product_params")

        # 访问订单页面
        driver.get("https://api16-normal-useast1a.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(10)

        # URL
        url = "https://api16-normal-useast1a.tiktokshopglobalselling.com/api/v1/product/global/product/publish"

        params = {
            "locale": "zh-CN",
            "language": "zh-CN",
            "oec_seller_id": oec_seller_id,
            "aid": "6556"
        }

        data = {
            "product_id": product_id,
            "regions": regions,
            "sku_params": sku_params,
            "region_product_params": region_product_params
        }

        res = executeService.request(driver=driver, url=url, params=params, data=data, method="POST")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)

    def mcalculatePrice(self, driver, options):
        '''
        @Desc    : 计算价格
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        if "shop_id" not in options:
            raise TaskParamsException("缺少 shop_id")
        oec_seller_id = options.get("shop_id")

        product_id = options.get("product_id")
        regions = options.get("regions")
        region_warehouses = options.get("region_warehouses")
        category_id = options.get("category_id")
        global_sku_dutiable_prices = options.get("global_sku_dutiable_prices")
        product_properties = options.get("product_properties")
        package_weight = options.get("package_weight")
        package_width = options.get("package_width")
        package_height = options.get("package_height")
        package_length = options.get("package_length")

        # 访问订单页面
        driver.get("https://api16-normal-useast1a.tiktokshopglobalselling.com")

        # 等待页面加载
        time.sleep(10)

        # URL
        url = "https://api16-normal-useast1a.tiktokshopglobalselling.com/api/v1/product/global/price/mcalculate"

        params = {
            "locale": "zh-CN",
            "language": "zh-CN",
            "oec_seller_id": oec_seller_id,
            "aid": "6556"
        }

        data = {
            "global_product_id": product_id,
            "regions": regions,
            "region_warehouses": region_warehouses,
            "category_id": category_id,
            "global_sku_dutiable_prices": global_sku_dutiable_prices,
            "product_properties": product_properties,
            "package_weight": package_weight,
            "package_width": package_width,
            "package_height": package_height,
            "package_length": package_length
        }

        res = executeService.request(driver=driver, url=url, params=params, data=data, method="POST")

        request_id = str(uuid.uuid4())

        # 保存数据
        options['request_id'] = request_id
        options['response'] = res
        taskRequest.save(options)