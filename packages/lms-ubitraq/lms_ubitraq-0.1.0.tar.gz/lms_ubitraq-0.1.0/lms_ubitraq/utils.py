from django.core.cache import cache
import requests
import json
from urllib.parse import urljoin

# 常量定义
TOKEN_CACHE_KEY = "api_token_cache"
TOKEN_TIMEOUT = 3600  # 1小时
API_TIMEOUT = 5  # 请求超时时间


class APIClient:
    def __init__(self, host: str, account: str, password: str):
        """
        初始化对象
        :param host: 通信地址
        :param account: 账号
        :param password: 密码
        """
        self.host = host
        self.account = account
        self.password = password
        self.base_url = f"http://{host}/paas/api"

    def get_token(self):
        cached_token = cache.get(TOKEN_CACHE_KEY)
        if cached_token:
            return cached_token
        response = requests.post(
            url=f"{self.base_url}/user/login/",
            data={"loginCode": self.account, "loginPwd": self.password},
            timeout=API_TIMEOUT
        )
        result = response.json()
        if result.get("isOk") and result.get("entity", {}).get("api_token"):
            api_token = result["entity"]["api_token"]
            cache.set(TOKEN_CACHE_KEY, api_token, TOKEN_TIMEOUT)
            return api_token
        return ""

    def get_map(self):
        '''
        获取地图列表，从中摘取地图楼层参数，与业务系统的楼层对应
        :return:
        '''
        api_token = self.get_token()
        response = requests.get(
            url=f"{self.base_url}/super/map/list/",
            params={"api_token": api_token},
            timeout=API_TIMEOUT
        )
        return response.json()

    def get_product(self, name) -> list:
        """
        获取标签类型表
        :return:
        """
        api_token = self.get_token()
        response = requests.get(
            url=f"{self.base_url}/super/product/listByType?type={name}",
            params={"api_token": api_token},
            timeout=API_TIMEOUT
        )
        return response.json()

    def get_tag(self) -> list:
        '''
        获取标签列表
        :return:
        '''
        api_token = self.get_token()
        response = requests.get(
            url=f"{self.base_url}/project/tag/list",
            params={"api_token": api_token},
            timeout=API_TIMEOUT
        )
        return response.json()

    def get_tag_info(self, id) -> dict:
        """
        获取单一标签信息
        :param id:
        :return:
        """
        api_token = self.get_token()
        response = requests.get(
            url=f"{self.base_url}/project/tag/get?code={id}",
            params={"api_token": api_token},
            timeout=API_TIMEOUT
        )
        return response.json()

    def get_anchor(self) -> list:
        """
        获取基站列表
        :return:
        """
        api_token = self.get_token()
        response = requests.get(
            url=f"{self.base_url}/project/anchor/list",
            params={"api_token": api_token},
            timeout=API_TIMEOUT
        )
        return response.json()
