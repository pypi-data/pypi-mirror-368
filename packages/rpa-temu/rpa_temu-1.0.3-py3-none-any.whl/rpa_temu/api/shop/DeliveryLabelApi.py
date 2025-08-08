import json
from rpa_temu.api.BaseApi import BaseApi
from rpa_common.service import ExecuteService
import undetected_chromedriver
import rpa_common.exceptions as exceptions

executeService = ExecuteService()

class DeliveryLabelApi(BaseApi):
    """DeliveryLabelApi 发货账单 - https://agentseller-eu.temu.com/labor/stml-logistics
    """    
    def __init__(self):
        super().__init__()
        
    def getList(self, driver:undetected_chromedriver.Chrome, options:dict):
        """
        @Desc    : 发货账单列表
        @Author  : 黄豪杰
        @Time    : 2024/07/23 15:42:22
        """
        mallid = options.get("shop_id")
        site:str = options.get("site")
        start_time = options.get("start_time")
        end_time = options.get("end_time")
        settleStatus = options.get("settleStatus",1)
        rowCount = options.get("rowCount",100)
        scrollContext = options.get("scrollContext","")
        
        if site.lower() not in self.site_url: 
            raise exceptions.TaskParamsException("暂不支持此站点")
        if not mallid: 
            raise exceptions.TaskParamsException("店铺ID不能为空")
        if not start_time or not end_time: 
            raise exceptions.TaskParamsException("请选择时间范围")
        
        url = self.site_url[site.lower()]
        url = site.lower() == 'us' and f"{url}/api/udp/yuanbenchu/seller_central/recon_bill/list" or f"{url}/portal/selene/seller/portal/recon/list"
        
        driver.get(f"{self.site_url[site.lower()]}/api/charge_back/query/status/count")
        
        body = {
            "settleStatus":settleStatus,
            "rowCount": rowCount,
            "scrollContext":scrollContext
        }
        
        if settleStatus == 1:
            body['deductTimeBegin'] = self.date_to_timestamp(start_time)
            body['deductTimeEnd'] = self.date_to_timestamp(end_time) + 86399999
        
        headers = {
            "content-type": "application/json",
            "mallid": mallid,
        }
        res = executeService.request(driver=driver, url=url, params=None, method="POST",data=body, headers=headers)
        
        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"获取发货账单失败 - {res}")

        return res