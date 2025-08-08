import json
import time
import uuid
import undetected_chromedriver
from rpa_temu.api.shop import ShopApi,AmountApi
from rpa_common.library import Request
from rpa_common.request import ShopRequest
from rpa_common.request import TaskRequest
from rpa_temu.service import TemuService

# 店铺服务
shopRequest = ShopRequest()
# 任务服务
taskRequest = TaskRequest()
# temu服务
temuService = TemuService()
# 店铺api
shopApi = ShopApi()
# api
shopAmountApi = AmountApi()
# 请求服务
request = Request()

class Amount():
    
    def shop_amount(self, driver:undetected_chromedriver.Chrome, shop_data:dict, options:dict):
        """ temu 资金申报 
        Author: 黄豪杰
        Args:
            driver: 驱动
            shop_data: 店铺数据
            options: 任务参数
        """
        print("资金申报")

        
        # 请求ID
        request_id = str(uuid.uuid4())
        data = {
            "request_id":request_id,
            "type_id":options['type_id'],
            "task_id":options['task_id'],
            "account_id":options['account_id'],            
        }
        
        res = shopAmountApi.getAayment(driver, options)
        
        if 'success' not in res or not res['success']:
            raise ValueError(f"资金申报获取失败 - {res}")

        data = {
            **data,
            "response":json.dumps(res,ensure_ascii=False),
        }
        # 保存数据
        taskRequest.save(data)
        
        print("资金申报结束")

