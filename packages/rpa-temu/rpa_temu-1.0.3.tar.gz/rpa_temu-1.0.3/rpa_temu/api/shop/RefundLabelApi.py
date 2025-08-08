import json
from rpa_temu.api.BaseApi import BaseApi
from rpa_common.service import ExecuteService
import undetected_chromedriver
import rpa_common.exceptions as exceptions

executeService = ExecuteService()

class RefundLabelApi(BaseApi):
    """RefundLabelApi 退货面单 - https://agentseller-eu.temu.com/labor/stml-reverse-logistics
    """    
    def __init__(self):
        super().__init__()
        
    def getList(self, driver:undetected_chromedriver.Chrome, options:dict):
        """
        @Desc    : 退货面单列表
        @Author  : 黄豪杰
        @Time    : 2024/07/23 15:42:22
        """
        site:str = options.get("site")
        mallid = options.get("shop_id")
        start_time = options.get("start_time")
        end_time = options.get("end_time")
        pageSize = options.get("pageSize",100)
        scrollContextString = options.get("scrollContextString","")
        
        if site.lower() not in self.site_url: 
            raise exceptions.TaskParamsException("暂不支持此站点")
        if not mallid: 
            raise exceptions.TaskParamsException("店铺ID不能为空")
        if not start_time or not end_time: 
            raise exceptions.TaskParamsException("请选择时间范围")
        
        url = self.site_url[site.lower()]
        url = site.lower() == 'us' and f"{url}/portal/udp/sunce/seller/center/bill/list" or f"{url}/portal/sunce/seller/center/bill/list"
        
        driver.get(url)
        
        body = {
            "deductTimeBegin":self.date_to_timestamp(start_time),
            "deductTimeEnd":self.date_to_timestamp(end_time) + 86399999,
            "pageSize":pageSize,
            "scrollContextString":scrollContextString
        }
        
        headers = {
            "content-type": "application/json",
            "mallid": mallid,
        }
        res = executeService.request(driver=driver, url=url, params=None, method="POST",data=body, headers=headers)
        
        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"获取退货面单列表失败 - {res}")

        return res