from datetime import datetime
import time
from rpa_common import Env as env
from urllib.parse import ParseResultBytes, urlparse

class BaseApi:
    def __init__(self):
        self.host = env().get().get('api','')
        self.home_url = "https://seller.kuajingmaihuo.com"
        self.site_url = {
            'eu': "https://agentseller-eu.temu.com",
            'us': "https://agentseller-us.temu.com",
        }
    
    def date_to_timestamp(self,date_str:str, milliseconds:bool=True) -> int:
        """date_to_timestamp 将y-m-d格式日期字符串转换为时间戳

        :param date_str:  日期字符串，格式如"2025-07-22"
        :param milliseconds: 是否返回毫秒级时间戳
        :return: 时间戳(秒级或毫秒级)
        """
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            timestamp = time.mktime(dt.timetuple())
            return int(timestamp * 1000) if milliseconds else int(timestamp)
        except ValueError as e:
            raise ValueError("日期格式错误，请使用'YYYY-MM-DD'格式") from e
    
    def is_same_domain(self,url1:str, url2:str) -> bool:
        """is_same_domain 判断两个链接是否属于同一个域名

        :param url1: 链接
        :param url2: 链接
        :return: bool
        """        
        # 解析两个 URL
        parsed_url1 = urlparse(url1)
        parsed_url2 = urlparse(url2)
        
        # 比较域名部分
        return parsed_url1.netloc == parsed_url2.netloc
    def get_path_and_query(self,url):
        """get_path_and_query 获取链接中没有域名的部分

        :param url: 链接
        :return: 地址
        """        
        # 解析 URL
        parsed_url:ParseResultBytes = urlparse(url)
        
        # 获取路径、查询参数和片段部分（不包括域名）
        return parsed_url.path + parsed_url.query + parsed_url.fragment