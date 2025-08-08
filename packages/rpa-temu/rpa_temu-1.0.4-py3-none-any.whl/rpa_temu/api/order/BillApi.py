import json
from rpa_temu.api.BaseApi import BaseApi
from rpa_temu.api.shop.ShopApi import ShopApi
from rpa_common.service import ExecuteService
import undetected_chromedriver
import rpa_common.exceptions as exceptions

executeService = ExecuteService()

# 店铺api
shopApi = ShopApi()

class BillApi(BaseApi):
    """BillApi 订单账单 - https://agentseller-eu.temu.com/labor/settle
    """    
    def __init__(self):
        super().__init__()
    def export(self, driver:undetected_chromedriver.Chrome, options:dict):
        """
        @Desc    : 导出账单
        @Author  : 黄豪杰
        @Time    : 2024/07/21 15:42:22
        """
        site:str = options.get("site")
        mallid = options.get("shop_id")
        start_time = options.get("start_time")
        end_time = options.get("end_time")
        
        if site.lower() not in self.site_url: 
            raise exceptions.TaskParamsException("暂不支持此站点")
        if not mallid: 
            raise exceptions.TaskParamsException("店铺ID不能为空")
        if not start_time or not end_time: 
            raise exceptions.TaskParamsException("请选择时间范围")
        
        url = self.site_url[site.lower()]
        url = f"{url}/api/merchant/file/export"
        
        userInfo = shopApi.getSiteUserInfoRow(driver,site)
        
        print(userInfo)
        print(mallid)
        print("店铺ID是否正确",mallid not in userInfo)
        
        if mallid not in userInfo: 
            raise exceptions.TaskParamsException("导出账单 - 请检查店铺ID是否正确")
        
        self.taskType = taskType = userInfo[mallid] == 1 and 11 or 12
        
        date:dict = taskType == 12 and {"beginDate":start_time, "endDate":end_time} or {"beginTime":self.date_to_timestamp(start_time), "endTime":self.date_to_timestamp(end_time) + 86399999}
        
        body = {
            "settleDataType":3,
            "taskType":taskType,
            **date
        }
        
        headers = {
            "content-type": "application/json",
            "mallid": mallid,
        }
        res = executeService.request(driver=driver, url=url, params=None, method="POST",data=body, headers=headers)
        
        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"导出账单失败 - {res}")

        return res
    
    def getList(self, driver:undetected_chromedriver.Chrome, options:dict):
        """
        @Desc    : 获取账单表格列表
        @Author  : 黄豪杰
        @Time    : 2024/07/21 15:42:22
        """
        site:str = options.get("site")
        mallid = options.get("shop_id")
        if site.lower() not in self.site_url: 
            raise exceptions.TaskParamsException("暂不支持此站点")
        if not mallid: 
            raise exceptions.TaskParamsException("店铺ID不能为空")
        
        url = self.site_url[site.lower()]
        url = f"{url}/api/merchant/file/export/history/page"
        
        if self.taskType:
            taskType = self.taskType
        else:
            userInfo = shopApi.getSiteUserInfoRow(driver,site)
            if mallid not in userInfo: 
                raise exceptions.TaskParamsException("获取账单表格列表 - 请检查店铺ID是否正确")
            self.taskType = taskType = userInfo[mallid] == 1 and 11 or 12
        
        body = {
            "taskType":taskType,
            "pageSize":5,
            "pageNum":1
        }
        
        headers = {
            "content-type": "application/json",
            "mallid": mallid,
        }
        res = executeService.request(driver=driver, url=url, params=None, method="POST",data=body, headers=headers)
        
        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"获取账单表格列表失败 - {res}")

        return res
    
    def getDownloadLink(self, driver:undetected_chromedriver.Chrome, options:dict,fileId:int):
        """
        @Desc    : 获取账单表格下载链接
        @Author  : 黄豪杰
        @Time    : 2024/07/21 15:42:22
        """
        site:str = options.get("site")
        mallid = options.get("shop_id")
        if site.lower() not in self.site_url: 
            raise exceptions.TaskParamsException("暂不支持此站点")
        if not mallid: 
            raise exceptions.TaskParamsException("店铺ID不能为空")
        
        url = self.site_url[site.lower()]
        url = f"{url}/api/merchant/file/export/download"
        
        if self.taskType:
            taskType = self.taskType
        else:
            userInfo = shopApi.getSiteUserInfoRow(driver,site)
            if mallid not in userInfo: 
                raise exceptions.TaskParamsException("获取账单表格下载链接 - 请检查店铺ID是否正确")
            self.taskType = taskType = userInfo[mallid] == 1 and 11 or 12
        
        body = {
            "taskType":taskType,
            "id":fileId
        }
        
        headers = {
            "content-type": "application/json",
            "mallid": mallid,
        }
        res = executeService.request(driver=driver, url=url, params=None, method="POST",data=body, headers=headers)
        
        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"获取账单表格列表失败 - {res}")

        return res