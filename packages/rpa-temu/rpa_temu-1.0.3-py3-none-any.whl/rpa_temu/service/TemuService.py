import json
import os
from pathlib import Path
import time
from rpa_temu.api.shop import ShopApi
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from rpa_common.request import ShopRequest
from rpa_common.exceptions import LoginException,TaskParamsException
import undetected_chromedriver

# 公共服务
# 店铺信息服务
shopRequest = ShopRequest()
# 店铺api
shopApi = ShopApi()

class TemuService():
    def __init__(self):
        super().__init__()
        self.site_url = shopApi.site_url
    def login(self, driver:undetected_chromedriver.Chrome, shop_data:dict, options:dict) -> bool:
        """ 
        @Desc    : temu 登录
        @Author  : 黄豪杰
        @Time    : 2024/07/21 15:42:22
        """        
        # 记录开始时间
        start_time = time.time()
        
        storage_data = shop_data.get("storage_data")
        
        # 如果 storage_data 存在，注入缓存
        if storage_data:
            print("🌐 使用缓存尝试自动登录")
            self._inject_storage(driver, storage_data)
        
        res = shopApi.getUserInfo(driver, options)
        
        if 'success' in res and res['success']:
            print("✅ 成功获取店铺信息，可能已登录")
            need_login = False
        else:
            print("🔒 可能未登录")
            print(res)
            need_login = True

        # 根据 need_login 决定是否执行登录逻辑
        if need_login:
            # 执行登录流程
            self._account_login(driver, shop_data, options)
        else:
            # 已登录
            print("✅ 已登录")

        # 计算运行时长（秒）
        run_duration = time.time() - start_time
        print(f"用时：{run_duration}秒")
        print("✅ 登录成功")

        return True

    def _account_login(self, driver:undetected_chromedriver.Chrome, shop_data:dict, options:dict) -> bool:
        """ 
        @Desc    : 账号登录
        @Author  : 黄豪杰
        @Time    : 2024/07/21 15:42:22
        """        
        print("账号登录")

        shop_global_id = shop_data.get("shop_global_id")
        login_name = shop_data.get("login_name")
        password = shop_data.get("password")
        
        if not shop_global_id or not login_name or not password:
            raise TaskParamsException("请检查店铺参数")

        # 访问页面
        driver.get("https://seller.kuajingmaihuo.com/login")

        wait = WebDriverWait(driver, 15)

        # 显式等待页面加载完成
        wait.until(EC.url_contains("/login"))

        # 使用手机号登录
        phone_input = wait.until(EC.presence_of_element_located((By.ID, "usernameId")))
        phone_input.send_keys(login_name)
        print("✅ 手机号已填写")
        time.sleep(0.5)

        password_input = wait.until(EC.presence_of_element_located((By.ID, "passwordId")))
        password_input.send_keys(password)
        print("✅ 密码已填写")
        time.sleep(0.5)

        select_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.CBX_squareInputWrapper_5-116-1")))
        select_button.click()
        print("✅ 点击选中【我已阅读并同意】")
        time.sleep(0.5)
        
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.password-login_infoContent__m4Lhn > button")))
        login_button.click()
        print("✅ 点击登录按钮")
        time.sleep(1)
        
        # 获取警告
        if len(driver.find_elements(By.CSS_SELECTOR, "body > div:nth-child(4) > div > div > div > div")) > 0:
            raise LoginException(driver.find_element(By.CSS_SELECTOR, "body > div:nth-child(4) > div > div > div > div").text)
        
        # 显式等待页面加载完成
        wait.until(EC.url_contains("/settle/site-main"))

        # 获取登录信息
        res = shopApi.getUserInfo(driver, options)
        print("获取登录信息", res)

        if 'success' not in res or not res['success']:
            raise LoginException("登录失败", res)

        # 保存店铺缓存
        self._save_storage(driver, shop_global_id)

        return True
    
    def _inject_storage(self, driver:undetected_chromedriver.Chrome, storage_data:dict):
        '''
        @Desc    : 注入缓存
        @Author  : 黄豪杰
        @Time    : 2024/07/21 16:42:22
        '''
        try:
            cookies = storage_data.get("cookies")

            driver.execute_cdp_cmd("Network.enable", {})
            for cookie in cookies:
                try:
                    driver.execute_cdp_cmd("Network.setCookie", {
                        "name": cookie["name"],
                        "value": cookie["value"],
                        "domain": cookie["domain"],
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
    
    def _save_storage(self, driver:undetected_chromedriver.Chrome, shop_global_id:int):
        '''
        @Desc    : 保存店铺缓存
        @Author  : 黄豪杰
        @Time    : 2024/07/21 16:42:22
        '''
        # 获取 cookies
        print("获取 cookies")
        cookies = driver.get_cookies()

        storage_data = {
            "shop_global_id": shop_global_id,
            "cookies": json.dumps(cookies)
        }

        # 保存店铺缓存
        print("保存店铺缓存")
        res = shopRequest.saveStorage(storage_data)
        if res['code'] != 1:
            raise ValueError(f"保存店铺缓存失败 - {res}")

        print("保存缓存成功")
    
    def authorize(self, driver:undetected_chromedriver.Chrome, options:dict) -> bool:
        """ 
        @Desc    : 授权下级站点账号
        @Author  : 黄豪杰
        @Time    : 2024/07/21 15:42:22
        """
        site:str = options.get("site",'')
        if site.lower() not in self.site_url:
            raise TaskParamsException("登录站点账号 - 请检查站点参数")
        
        res = shopApi.getSiteUserInfo(driver, site)
        print("获取站点登录信息", res)
        if 'success' in res and res['success']:
            return True
        
        # 获取授权码
        obtainCode = shopApi.obtainCode(driver, site)
        
        time.sleep(1)
        
        if 'success' not in obtainCode or not obtainCode['success']:
            raise LoginException("登录站点账号 - 获取授权码失败", obtainCode)
        code = obtainCode['result']['code']
        # 登录授权码
        loginByCode = shopApi.loginByCode(driver, site, code)
        if 'success' not in loginByCode or not loginByCode['success']:
            raise LoginException("登录站点账号 - 登录授权码失败", obtainCode)
        return True
        
    
        
        