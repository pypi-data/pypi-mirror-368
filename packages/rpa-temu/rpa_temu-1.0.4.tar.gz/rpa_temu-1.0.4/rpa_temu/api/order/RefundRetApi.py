import json
from rpa_temu.api.BaseApi import BaseApi
from rpa_common.service import ExecuteService
import undetected_chromedriver
import rpa_common.exceptions as exceptions

executeService = ExecuteService()

class RefundRetApi(BaseApi):
    """RefundRetApi 退款退货 - https://agentseller-us.temu.com/mmsos/return-refund-list.html
    """    
    def __init__(self):
        super().__init__()
        
    def getRefundRetList(self, driver:undetected_chromedriver.Chrome, options:dict):
        """
        @Desc    : 退款退货列表
        @Author  : 黄豪杰
        @Time    : 2024/07/24 15:42:22
        """
        site:str = options.get("site")
        mallid = options.get("shop_id")
        start_time = options.get("start_time")
        end_time = options.get("end_time")
        pageNumber = options.get("pageNumber",1) # 页码
        pageSize = options.get("pageSize",100) # 每页数量
        
        if site.lower() not in self.site_url: 
            raise exceptions.TaskParamsException("暂不支持此站点")
        if not mallid: 
            raise exceptions.TaskParamsException("店铺ID不能为空")
        if not start_time or not end_time: 
            raise exceptions.TaskParamsException("请选择时间范围")
        
        url = self.site_url[site.lower()]
        url = f"{url}/garen/mms/afterSales/queryReturnAndRefundPaList"
        
        driver.get(url)
        
        body = {
            "pageNumber":pageNumber,
            "pageSize":pageSize,
            "startCreatedTime":self.date_to_timestamp(start_time),
            "endCreatedTime":self.date_to_timestamp(end_time),
            "groupSearchType":0,
            "timeSearchType":5000,
            "reverseSignedTimeSearchType":7000,
            "selectOnlyRefund":True,
            "selectReturnRefund":True
        }
        
        headers = {
            "content-type": "application/json",
            "mallid": mallid,
        }
        res = executeService.request(driver=driver, url=url, params=None, method="POST",data=body, headers=headers)
        
        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"退款退货列表获取失败 - {res}")

        return res

    def getRefundRetDetail(self, driver:undetected_chromedriver.Chrome, options:dict):
        """
        @Desc    : 退款退货详情
        @Author  : 黄豪杰
        @Time    : 2024/07/24 15:42:22
        """
        site:str = options.get("site")
        mallid = options.get("shop_id")
        parentOrderSn = options.get("parentOrderSn")
        parentAfterSalesSn = options.get("parentAfterSalesSn")
        
        if site.lower() not in self.site_url: 
            raise exceptions.TaskParamsException("暂不支持此站点")
        if not mallid: 
            raise exceptions.TaskParamsException("店铺ID不能为空")
        if not parentOrderSn or not parentAfterSalesSn: 
            raise exceptions.TaskParamsException("未选择退款订单")
        
        url = self.site_url[site.lower()]
        url = f"{url}/garen/mms/afterSales/queryReturnDetails"
        
        driver.get(url)
        
        body = {
            "parentOrderSn":parentOrderSn,
            "parentAfterSalesSn":parentAfterSalesSn
        }
        
        headers = {
            "content-type": "application/json",
            "mallid": mallid,
        }
        res = executeService.request(driver=driver, url=url, params=None, method="POST",data=body, headers=headers)
        
        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"退款退货详情获取失败 - {res}")

        return res