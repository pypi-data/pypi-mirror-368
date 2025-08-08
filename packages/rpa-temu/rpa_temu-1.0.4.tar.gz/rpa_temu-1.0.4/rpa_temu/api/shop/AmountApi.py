import json
from rpa_temu.api.BaseApi import BaseApi
from rpa_common.service import ExecuteService
import undetected_chromedriver
import rpa_common.exceptions as exceptions

executeService = ExecuteService()

class AmountApi(BaseApi):
    """AmountApi 资金中心 - https://seller.kuajingmaihuo.com/labor/account
    """    
    def __init__(self):
        super().__init__()
    
    def getAayment(self, driver:undetected_chromedriver.Chrome, options:dict):
        """
        @Desc    : 货款账户
        @Author  : 黄豪杰
        @Time    : 2024/07/24 15:42:22
        """
        mallid = options.get("shop_id")
        
        if not mallid: 
            raise exceptions.TaskParamsException("店铺ID不能为空")
        
        url = f"{self.home_url}/api/merchant/payment/account/amount/info"
        
        driver.get(url)
        
        body = {}
        
        headers = {
            "content-type": "application/json",
            "mallid": mallid,
        }
        res = executeService.request(driver=driver, url=url, params=None, method="POST",data=body, headers=headers)
        
        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"获取货款账户失败 - {res}")

        return res
    
    def getWithdrawals(self, driver:undetected_chromedriver.Chrome, options:dict):
        """
        @Desc    : 提现记录
        @Author  : 黄豪杰
        @Time    : 2024/07/24 15:42:22
        """
        mallid = options.get("shop_id")
        page = options.get("page",1)
        pageSize = options.get("pageSize",100)
        
        if not mallid: 
            raise exceptions.TaskParamsException("店铺ID不能为空")
        
        url = f"{self.home_url}/api/merchant/payment/account/withdraw/cash/record"
        
        driver.get(url)
        
        body = {
            "page":page,
            "pageSize":pageSize
        }
        
        headers = {
            "content-type": "application/json",
            "mallid": mallid,
        }
        
        res = executeService.request(driver=driver, url=url, params=None, method="POST",data=body, headers=headers)
        
        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"获取提现记录失败 - {res}")

        return res
    
        
        