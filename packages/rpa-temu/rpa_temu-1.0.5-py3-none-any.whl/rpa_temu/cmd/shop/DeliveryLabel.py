import json
import time
import uuid
import undetected_chromedriver
from rpa_temu.api.shop import ShopApi,DeliveryLabelApi
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
shopDeliveryLabelApi = DeliveryLabelApi()
# 请求服务
request = Request()

class DeliveryLabel():
    def __init__(self):
        pass
    
    def shop_delivery_label(self, driver:undetected_chromedriver.Chrome, shop_data:dict, options:dict):
        """ temu 发货面单 
        Author: 黄豪杰
        Args:
            driver: 驱动
            shop_data: 店铺数据
            options: 任务参数
        """
        print("发货面单")

        # 站点登录
        temuService.authorize(driver, options)
        
        # 测试固定时间
        if 'start_time' not in options and 'end_time' not in options:
            options['start_time'] = '2025-06-01'
            options['end_time'] = '2025-06-30'
        
        # 请求ID
        request_id = str(uuid.uuid4())
        data = {
            "request_id":request_id,
            "type_id":options['type_id'],
            "task_id":options['task_id'],
            "account_id":options['account_id'],            
        }
        statuss = [1,2]
        for status in statuss:
            page_number = 1
            options['rowCount'] = rowCount = 100
            options['settleStatus'] = status
            while True:
                # 获取发货面单列表
                res = shopDeliveryLabelApi.getList(driver, options)
                if 'success' not in res or not res['success']:
                    raise ValueError(f"发货面单列表获取失败 - {res}")
                
                key = options['site'].lower() == 'us' and 'sellerBillList' or 'list'
                list_count = len(res['result'][key])
                total_count = res['result']['total']
                
                # 列表数量小于1
                if list_count < 1:
                    # 当页面如果是第一页没有数据的话需要保存没有数据
                    if page_number == 1:
                        data = {
                            **data,
                            "response":json.dumps([],ensure_ascii=False),
                        }
                        # 保存数据
                        taskRequest.save(data)
                    break
                
                options['scrollContext'] = res['result']['scrollContext']
                
                title = status == 1 and "已出账" or "待出账"
                print(f"当前{title} - 第{page_number}页,每页{rowCount} - 共{total_count}条数据")
                
                data = {
                    **data,
                    "response":json.dumps(res,ensure_ascii=False),
                    "page_number":page_number, # 页码
                    "page_size":rowCount, # 每页数量
                    "list_count":list_count, # 当前页数量
                    "total_count":total_count # 总数量
                }
                # 保存数据
                taskRequest.save(data)
                
                page_number += 1
        
        print("发货面单结束")
        
        