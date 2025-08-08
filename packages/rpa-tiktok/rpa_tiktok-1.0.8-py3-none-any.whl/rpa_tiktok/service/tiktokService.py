import json
import time
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from rpa_common import Common
from rpa_common.exceptions import LoginException
from rpa_common.request.ShopRequest import ShopRequest
from rpa_common.service.GoogleService import GoogleService
from rpa_tiktok.api.ShopApi import ShopApi

common = Common()
shopRequest = ShopRequest()
googleService = GoogleService()
shopApi = ShopApi()

class TiktokService():
    def __init__(self):
        super().__init__()

    def login(self, driver, data, options):
        '''
        @Desc    : 登录
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("登录")
        # 记录开始时间
        start_time = time.time()

        storage_data = data.get("storage_data")

        # 如果 storage_data 存在，注入缓存
        print("注入缓存")
        if storage_data:
            print("🌐 使用缓存尝试自动登录")
            self.inject_storage(driver, storage_data)

        # 获取登录信息
        res = shopApi.getInfoList(driver, options)
        print("获取登录信息", res)
        res = json.loads(res)

        if res['code'] == 0:
            print("✅ 成功获取店铺信息，可能已登录")
            need_login = False
        else:
            print("🔒 可能未登录")
            print(res)
            need_login = True

        # 根据 need_login 决定是否执行登录逻辑
        if need_login:
            # 执行登录流程
            login_res = self.account_login(driver, data, options)
            # 登录失败
            if login_res['status'] == 0:
                return login_res
        else:
            # 已登录
            print("✅ 已登录")

        # 计算运行时长（秒）
        run_duration = time.time() - start_time
        print(f"用时：{run_duration}秒")
        print("✅ 登录成功")

        return common.back(1, '登录成功')

    def account_login(self, driver, data, options):
        '''
        @Desc    : 账号登录
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        print("账号登录")

        shop_global_id = data.get("shop_global_id")
        login_name = data.get("login_name")
        password = data.get("password")
        google_auth_key = data.get("google_auth_key")

        # 访问页面
        driver.get("https://seller.tiktokshopglobalselling.com/account/login")

        wait = WebDriverWait(driver, 15)

        # 等待页面加载完成
        wait.until(EC.url_contains("/account/login"))

        email_login_button = wait.until(EC.element_to_be_clickable((By.ID, "TikTok_Ads_SSO_Login_Email_Panel_Button")))
        email_login_button.click()
        print("✅ 点击了“使用邮箱登录”")
        time.sleep(1)

        email_input = wait.until(EC.presence_of_element_located((By.ID, "TikTok_Ads_SSO_Login_Email_Input")))
        email_input.send_keys(login_name)
        print("✅ 邮箱已填写")
        time.sleep(1)

        password_input = wait.until(EC.presence_of_element_located((By.ID, "TikTok_Ads_SSO_Login_Pwd_Input")))
        password_input.send_keys(password)
        print("✅ 密码已填写")
        time.sleep(1)

        login_button = wait.until(EC.element_to_be_clickable((By.ID, "TikTok_Ads_SSO_Login_Btn")))
        login_button.click()
        print("✅ 点击了登录按钮")

        time.sleep(5)

        print("获取验证码")
        res = googleService.get_verify_code(google_auth_key)
        if res['status'] == 1:
            print(res['message'])
            verify_code = res['data']

            # 输入验证码
            print("输入验证码")
            common.input_text(driver, verify_code, [(By.ID, "TT4B_TSV_Verify_Code_Input"), (By.ID, "TikTok_Ads_SSO_Login_Code_Input")])

            # 点击登录
            print("点击登录")
            common.click_element(driver, [(By.ID, "TT4B_TSV_Verify_Submit_Btn"), (By.ID, "TikTok_Ads_SSO_Login_Code_Btn")])

            print("等待10秒")
            time.sleep(10)

        # 获取登录信息
        res = shopApi.getInfoList(driver, options)
        print("获取登录信息", res)
        res = json.loads(res)

        if res['code'] != 0:
            raise LoginException("登录失败", res)

        # 保存店铺缓存
        self.save_storage(driver, shop_global_id)

        return common.back(1, '登录成功')

    def inject_storage(self, driver, storage_data):
        '''
        @Desc    : 注入缓存
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        try:
            cookies = storage_data.get("cookies")

            driver.execute_cdp_cmd("Network.enable", {})
            for cookie in cookies:
                try:
                    # 新域名 cookie
                    driver.execute_cdp_cmd("Network.setCookie", {
                        "name": cookie["name"],
                        "value": cookie["value"],
                        "domain": cookie["domain"],
                        "path": cookie.get("path", "/"),
                        "secure": cookie.get("secure", False),
                        "httpOnly": cookie.get("httpOnly", False),
                        "sameSite": cookie.get("sameSite", "None")
                    })

                    # 旧域名 cookie
                    original_domain = cookie["domain"]
                    if original_domain in ["seller.tiktokshopglobalselling.com", ".tiktokshopglobalselling.com"]:
                        new_domain = original_domain.replace("tiktokshopglobalselling.com", "tiktokglobalshop.com")
                        driver.execute_cdp_cmd("Network.setCookie", {
                            "name": cookie["name"],
                            "value": cookie["value"],
                            "domain": new_domain,
                            "path": cookie.get("path", "/"),
                            "secure": cookie.get("secure", False),
                            "httpOnly": cookie.get("httpOnly", False),
                            "sameSite": cookie.get("sameSite", "None")
                        })
                except Exception as e:
                    print(f"⚠️ CDP 注入 cookie 失败：{cookie}, 错误：{e}")

        except Exception as e:
            print(f"⚠️ 缓存登录失败: {e}")

        print("注入缓存成功")

    def save_storage(self, driver, shop_global_id):
        '''
        @Desc    : 保存店铺缓存
        @Author  : 钟水洲
        @Time    : 2024/05/31 15:42:22
        '''
        # 获取 cookies
        print("获取 cookies")
        cookies = driver.get_cookies()
        # 获取 API域名的缓存
        print("获取 API域名的缓存")
        driver.get("https://api16-normal-sg.tiktokshopglobalselling.com/")
        time.sleep(3)
        cookies += driver.get_cookies()

        storage_data = {
            "shop_global_id": shop_global_id,
            "cookies": json.dumps(cookies)
        }

        # 保存店铺缓存
        print("保存店铺缓存")
        res = shopRequest.saveStorage(storage_data)
        if res['code'] != 1:
            print("保存缓存成功")
            return common.back(0, res['msg'])

        print("保存缓存成功")