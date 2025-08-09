import json
from rpa_temu.api.BaseApi import BaseApi
from rpa_common.service import ExecuteService
import undetected_chromedriver
import rpa_common.exceptions as exceptions

executeService = ExecuteService()

class BillDetailApi(BaseApi):
    """BillDetailApi 财务明细（对账中心） - https://seller.kuajingmaihuo.com/labor/bill
    """    
    def __init__(self):
        super().__init__()
        
    def getList(self, driver:undetected_chromedriver.Chrome, options:dict):
        """
        @Desc    : 财务明细列表
        @Author  : 黄豪杰
        @Time    : 2024/07/23 15:42:22
        """
        mallid = options.get("shop_id")
        start_time = options.get("start_time")
        end_time = options.get("end_time")
        pageSize = options.get("pageSize",100)
        pageNum = options.get("pageNum",1)
        
        if not mallid: 
            raise exceptions.TaskParamsException("店铺ID不能为空")
        if not start_time or not end_time: 
            raise exceptions.TaskParamsException("请选择时间范围")
        
        url = f"{self.home_url}/api/merchant/fund/detail/pageSearch"
        
        driver.get(url)
        
        body = {
            "beginTime":self.date_to_timestamp(start_time),
            "endTime":self.date_to_timestamp(end_time) + 86399999,
            "pageSize": pageSize,
            "pageNum": pageNum
        }
        
        headers = {
            "content-type": "application/json",
            "mallid": mallid,
        }
        res = executeService.request(driver=driver, url=url, params=None, method="POST",data=body, headers=headers)
        
        try :
            res = json.loads(res)
        except Exception as e:
            raise ValueError(f"获取财务明细列表失败 - {res}")

        return res