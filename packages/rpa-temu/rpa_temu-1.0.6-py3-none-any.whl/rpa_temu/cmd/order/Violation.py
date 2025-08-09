import json
import uuid
import undetected_chromedriver
from rpa_temu.api.shop import ShopApi
from rpa_temu.api.order import ViolationApi
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
violationApi = ViolationApi()
# 请求服务
request = Request()

class Violation():
    def __init__(self):
        pass

    def order_violation(self, driver:undetected_chromedriver.Chrome, shop_data:dict, options:dict):
        """ temu 订单违规 列表
        Author: 黄豪杰
        Args:
            driver: 驱动
            shop_data: 店铺数据
            options: 任务参数
        """        
        print("订单违规列表")

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
        options['pageNo'] = pageNo = 1
        options['pageSize'] = pageSize = 100
        options['targetType'] = 1
        while True:
            res = violationApi.getViolationList(driver, options)
            if 'success' not in res or not res['success']:
                raise ValueError(f"订单违规列表获取失败 - {res}")
                
            list_count = len(res['result']['pageData'] or [])
            total_count = res['result']['total']
            
            # 列表数量小于1
            if list_count < 1:
                # 当页面如果是第一页没有数据的话需要保存没有数据
                if pageNo == 1:
                    data = {
                        **data,
                        "response":json.dumps([],ensure_ascii=False),
                    }
                    # 保存数据
                    taskRequest.save(data)
                break
            
            print(f"当前第{pageNo}页,每页{pageSize} - 共{total_count}条数据")

            data = {
                **data,
                "response":json.dumps(res,ensure_ascii=False),
                "page_number":pageNo, # 页码
                "page_size":pageSize, # 每页数量
                "list_count":list_count, # 当前页数量
                "total_count":total_count # 总数量
            }
            # 保存数据
            taskRequest.save(data)
            
            # 下一页
            pageNo += 1
            options['pageNo'] = pageNo
        print("订单违规列表结束")
    
    def order_violation_detail(self, driver:undetected_chromedriver.Chrome, shop_data:dict, options:dict):
        """ temu 订单违规详情
        Author: 黄豪杰
        Args:
            driver: 驱动
            shop_data: 店铺数据
            options: 任务参数
        """        
        print("订单违规详情")

        # 站点登录
        temuService.authorize(driver, options)
        
        # 请求ID
        request_id = str(uuid.uuid4())
        data = {
            "request_id":request_id,
            "type_id":options['type_id'],
            "task_id":options['task_id'],
            "account_id":options['account_id'],            
        }
        
        res = violationApi.getViolationDetail(driver, options)
        if 'success' not in res or not res['success']:
            raise ValueError(f"订单违规详情获取失败 - {res}")
        
        data = {
            **data,
            "response":json.dumps(res,ensure_ascii=False),
        }
        
        # 保存数据
        taskRequest.save(data)
        
        print("订单违规详情结束")