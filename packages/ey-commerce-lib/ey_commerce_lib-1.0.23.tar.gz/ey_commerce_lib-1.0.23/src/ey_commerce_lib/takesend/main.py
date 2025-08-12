from httpx import AsyncClient, Timeout

from ey_commerce_lib.takesend.config import LOGIN_HEADERS, EDIT_HEADERS


class TakeSendClient(object):

    def __init__(self, username: str, password: str):
        timeout = Timeout(connect=60.0, read=60.0, write=60.0, pool=30.0)
        self.__async_client = AsyncClient(
            base_url="http://k5.takesend.com:8180",
            timeout=timeout,
            verify=False
        )
        self.__username = username
        self.__password = password

    async def login(self):
        """
        自动登录
        :return:
        """
        # 访问首页
        await self.__async_client.get("/c_index.jsp")
        # 登录
        params = {
            'action': 'logon'
        }
        data = {
            'userid': self.__username,
            'password': self.__password
        }
        # 请求登录接口
        await self.__async_client.post(".//client/Logon", params=params, data=data, headers=LOGIN_HEADERS)

    async def client_cc_order(self, excel_data: list | str):
        """
        修改泰嘉产品上传重量数据
        :param excel_data:
        :return:
        """

        params = {
            'action': 'updateDweight',
        }
        data = {
            'excel[]': excel_data,
        }

        response = await self.__async_client.post('/Client/CCOrder', params=params, data=data, headers=EDIT_HEADERS)
        return response.json()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.__async_client.aclose()
