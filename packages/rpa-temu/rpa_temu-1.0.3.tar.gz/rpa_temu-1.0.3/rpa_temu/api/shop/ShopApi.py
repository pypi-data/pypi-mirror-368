import json
from rpa_temu.api.BaseApi import BaseApi
from rpa_common.service import ExecuteService
import undetected_chromedriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

executeService = ExecuteService()

class ShopApi(BaseApi):
    """ShopApi 店铺接口
    """    
    def __init__(self):
        super().__init__()  
    def getUserInfo(self, driver:undetected_chromedriver.Chrome, options:dict)->dict:
        """
        @Desc    : 店铺信息获取
        @Author  : 黄豪杰
        @Time    : 2024/07/21 15:42:22
        """
        
        url = f"{self.home_url}/bg/quiet/api/mms/userInfo"
        
        if not self.is_same_domain(driver.current_url,url):
            driver.get(url)
        
            wait = WebDriverWait(driver, 15)
            # 显式等待页面加载完成
            wait.until(EC.url_contains(self.get_path_and_query(url)))
        
        params = {}

        res = executeService.request(driver=driver, url=url, params=params, method="POST")
        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"店铺信息获取失败 - {res}")
        
        return res
    
    def obtainCode(self, driver:undetected_chromedriver.Chrome,site:str)->dict:
        """
        @Desc    : 获取授权码
        @Author  : 黄豪杰
        @Time    : 2024/07/22 15:42:22
        """
        url = f"{self.home_url}/bg/quiet/api/auth/obtainCode"
        
        if not self.is_same_domain(driver.current_url,url):
            driver.get(url)
            
            wait = WebDriverWait(driver, 15)
            # 显式等待页面加载完成
            wait.until(EC.url_contains(self.get_path_and_query(url)))        
        
        redirectUrl = self.site_url[site.lower()]
        
        body = {
            "redirectUrl":redirectUrl
        }
        headers = {
            "content-type": "application/json",
        }
        
        res = executeService.request(driver=driver, url=url, params=None, method="POST",data=body, headers=headers)

        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"获取授权码失败 - {res}")

        return res
    
    def loginByCode(self, driver:undetected_chromedriver.Chrome,site:str, code:str)->dict:
        """
        @Desc    : 授权登录
        @Author  : 黄豪杰
        @Time    : 2024/07/22 15:42:22
        """   
        
        url = self.site_url[site.lower()]
        
        url = f"{url}/api/seller/auth/loginByCode"
        
        if not self.is_same_domain(driver.current_url,url):
            driver.get(url)
            
            wait = WebDriverWait(driver, 15)
            # 显式等待页面加载完成
            wait.until(EC.url_contains(self.get_path_and_query(url)))
        
        body = {
            "code":code,
            "confirm":False
        }
        headers = {
            "content-type": "application/json",
        }
        
        res = executeService.request(driver=driver, url=url, params=None, method="POST",data=body, headers=headers)
        
        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"授权登录失败 - {res}")

        return res
    
    def getSiteUserInfo(self, driver:undetected_chromedriver.Chrome,site:str) ->dict:
        """
        @Desc    : 站点账号获取店铺信息
        @Author  : 黄豪杰
        @Time    : 2024/07/22 15:42:22
        """ 
        url = self.site_url[site.lower()]
        url = f"{url}/api/seller/auth/userInfo"
        
        if not self.is_same_domain(driver.current_url,url):
            driver.get(url)
            
            wait = WebDriverWait(driver, 15)
            # 显式等待页面加载完成
            wait.until(EC.url_contains(self.get_path_and_query(url)))      
        
        params = {}

        res = executeService.request(driver=driver, url=url, params=params, method="POST")
        
        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"获取站点账号获取店铺信息失败 - {res}")

        return res
    
    def getSiteUserInfoRow(self, driver:undetected_chromedriver.Chrome,site:str) -> dict:
        """
        @Desc    : 获取站点信息 - 处理过的
        @Author  : 黄豪杰
        @Time    : 2024/07/22 15:42:22
        """
        
        res = self.getSiteUserInfo(driver, site)
        if 'success' not in res or not res['success']:
            raise ValueError("店铺信息获取失败")
        
        return {
            item['mallId']: item['managedType'] for item in res['result']['mallList']
        }   
        
        
        