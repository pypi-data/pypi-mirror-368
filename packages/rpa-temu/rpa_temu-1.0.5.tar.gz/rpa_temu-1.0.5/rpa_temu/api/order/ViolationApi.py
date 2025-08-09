import json
from rpa_temu.api.BaseApi import BaseApi
from rpa_common.service import ExecuteService
import undetected_chromedriver
import rpa_common.exceptions as exceptions

executeService = ExecuteService()

class ViolationApi(BaseApi):
    """ShopAmountApi 违规数据 - https://agentseller-eu.temu.com/mmsos/mall-appeal.html?targetType=1
    """    
    def __init__(self):
        super().__init__()
        
    def getViolationList(self, driver:undetected_chromedriver.Chrome, options:dict):
        """
        @Desc    : 违规列表
        @Author  : 黄豪杰
        @Time    : 2024/07/24 15:42:22
        """
        site:str = options.get("site")
        mallid = options.get("shop_id")
        start_time = options.get("start_time")
        end_time = options.get("end_time")
        pageNo = options.get("pageNo",1) # 页码
        pageSize = options.get("pageSize",100) # 每页数量
        targetType = options.get("targetType",1) # 1:订单违规 2:店铺违规
        
        if site.lower() not in self.site_url: 
            raise exceptions.TaskParamsException("暂不支持此站点")
        if not mallid: 
            raise exceptions.TaskParamsException("店铺ID不能为空")
        if not start_time or not end_time: 
            raise exceptions.TaskParamsException("请选择时间范围")
        
        url = self.site_url[site.lower()]
        url = f"{url}/reaper/violation/appeal/queryMallAppeals"
        
        driver.get(url)
        
        body = {
            "targetType":targetType,
            "pageNo":pageNo,
            "pageSize":pageSize,
            "informTimeBegin":self.date_to_timestamp(start_time),
            "informTimeEnd":self.date_to_timestamp(end_time)
        }
        
        headers = {
            "content-type": "application/json",
            "mallid": mallid,
        }
        res = executeService.request(driver=driver, url=url, params=None, method="POST",data=body, headers=headers)
        
        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"违规列表获取失败 - {res}")

        return res

    def getViolationDetail(self, driver:undetected_chromedriver.Chrome, options:dict):
        """
        @Desc    : 违规详情
        @Author  : 黄豪杰
        @Time    : 2024/07/24 15:42:22
        """
        site:str = options.get("site")
        mallid = options.get("shop_id")
        violationAppealSn = options.get("violationAppealSn")
        violationType = options.get("violationType")
        
        if site.lower() not in self.site_url: 
            raise exceptions.TaskParamsException("暂不支持此站点")
        if not mallid: 
            raise exceptions.TaskParamsException("店铺ID不能为空")
        if not violationAppealSn or not violationType: 
            raise exceptions.TaskParamsException("未选择违规单")
        
        url = self.site_url[site.lower()]
        url = f"{url}/reaper/violation/appeal/querySubTargetAppeals"
        
        driver.get(url)
        
        body = {
            "violationAppealSn":violationAppealSn,
            "violationType":violationType
        }
        
        headers = {
            "content-type": "application/json",
            "mallid": mallid,
        }
        res = executeService.request(driver=driver, url=url, params=None, method="POST",data=body, headers=headers)
        
        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"违规详情获取失败 - {res}")

        return res
    
        