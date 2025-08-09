import json
import time
import uuid
import undetected_chromedriver
from rpa_temu.api.shop import ShopApi
from rpa_temu.api.order import BillApi
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
orderBillApi = BillApi()
# 请求服务
request = Request()

class Bill():
    def __init__(self):
        pass
    
    def order_bill(self, driver:undetected_chromedriver.Chrome, shop_data:dict, options:dict):
        """ temu 订单账单 
        Author: 黄豪杰
        Args:
            driver: 驱动
            shop_data: 店铺数据
            options: 任务参数
        """        
        print("订单账单")

        # 站点登录
        temuService.authorize(driver, options)
        
        # 测试固定时间
        if 'start_time' not in options and 'end_time' not in options:
            options['start_time'] = '2025-06-01'
            options['end_time'] = '2025-06-30'
        
        # 导出账单
        res = orderBillApi.export(driver, options)
        if ('success' not in res or not res['success']) and res['errorMsg'] != "导出任务已存在, 请勿重复创建, 请前往【导出历史】查看":
            raise ValueError(f"导出账单表格失败 - {res}")
         
        time.sleep(1)
        # 获取账单列表
        res = orderBillApi.getList(driver, options)
        if 'success' not in res or not res['success']:
            raise ValueError(f"获取账单列表失败 - {res}")
        fileId = res['result']['merchantMerchantFileExportHistoryList'][0]['id']
        
        num = 0
        while True:
            if num > 10:
                raise ValueError(f"获取账单下载链接超时")
            time.sleep(1)
            # 获取账单下载链接
            res = orderBillApi.getDownloadLink(driver, options,fileId)
            if 'success' not in res or not res['success']:
                raise ValueError(f"获取账单下载链接失败 - {res}")
            
            if 'result' in res and 'fileUrl' in res['result']:
                break
            
            num += 1
            
        fileUrl = res['result']['fileUrl']
        
        print(f"账单下载链接：{fileUrl}")
        
        cookies = {item['name']:item['value'] for item in driver.get_cookies()}
        
        dataXlsx = request.downloadExcel(fileUrl,{"cookies": cookies})
        # 请求ID
        request_id = str(uuid.uuid4())
        data = {
            "type_id":options['type_id'],
            "task_id":options['task_id'],
            "account_id":options['account_id'],
            "response":json.dumps(dataXlsx,ensure_ascii=False),
            "request_id":request_id
        }
        
        # 保存数据
        taskRequest.save(data)
        
        print("订单账单结束")
