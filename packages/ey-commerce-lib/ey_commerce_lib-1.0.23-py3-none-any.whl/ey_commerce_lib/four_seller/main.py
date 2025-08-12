import asyncio
import base64
import logging
from typing import Callable

import ddddocr
from httpx import AsyncClient, ReadTimeout, Timeout
from playwright.async_api import async_playwright, TimeoutError

from ey_commerce_lib.four_seller.constant.response import ResponseCodeEnum
from ey_commerce_lib.four_seller.parser.order import parse_order
from ey_commerce_lib.four_seller.schemas.query.order import FourSellerOrderQueryModel
from ey_commerce_lib.four_seller.schemas.vo.order import FourSellerOrderVO
from ey_commerce_lib.model import Page
from ey_commerce_lib.utils.close import safe_close

logger = logging.getLogger(__name__)


class FourSellerClient:

    def __init__(self, user_name: str,
                 password: str,
                 user_token: str,
                 login_success_call_back: Callable,
                 sem: int = 10):
        self.user_name = user_name
        self.password = password
        self.user_token = user_token
        # 登录成功回调函数
        self.login_success_call_back = login_success_call_back
        # 信号量
        self.__sem = asyncio.Semaphore(sem)
        # 自动登录锁
        self.__login_lock = asyncio.Lock()
        # 当前登录任务的 future
        self.__login_in_progress = None
        # ddddocr实例
        self.__ocr = ddddocr.DdddOcr()
        timeout = Timeout(connect=60.0, read=60.0, write=60.0, pool=30.0)
        # 异步客户端
        self.__async_client = AsyncClient(base_url="https://www.4seller.com", cookies={"userToken": user_token},
                                          headers={
                                              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 "
                                                            "Safari/537.36"
                                          }, timeout=timeout)

    async def __auto_login_4seller(self) -> str:
        """
        自动登录4seller
        :return: 登录
        """
        browser = None
        context = None
        page = None
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--start-maximized',
                        '--disable-blink-features=AutomationControlled',
                    ]
                )

                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                               "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080},
                    locale='zh-CN',  # 中文环境
                    timezone_id='Asia/Shanghai',  # 中国时区
                    geolocation={"longitude": 116.4074, "latitude": 39.9042},  # 北京位置
                    permissions=["geolocation"]
                )
                page = await context.new_page()
                await page.goto('https://www.4seller.com/login.html')
                # 等待元素出现
                await page.locator('.el-input__inner').first.wait_for()
                input_locators = await page.locator('.el-input__inner').all()
                username_input_element = input_locators[0]
                password_input_element = input_locators[1]
                await username_input_element.fill(self.user_name)
                await password_input_element.fill(self.password)
                login_button_element = page.locator('.el-button.sign_up')
                await login_button_element.click()
                # 获取验证码图片
                capcha_code_img_element = page.locator('.el-input__wrapper img')
                await capcha_code_img_element.wait_for()
                captcha_code_input_element = page.locator('[autocomplete="new-password"]')
                login_count = 1
                # 只能允许一百次登录
                while login_count <= 100:
                    # 等图片 src 被赋值
                    max_attempts = 10
                    for attempt in range(max_attempts):
                        src = await capcha_code_img_element.get_attribute("src")
                        if src and src.strip() != "":
                            break
                        await page.wait_for_timeout(500)
                    else:
                        raise Exception("获取不到图片验证码")
                    # 识别验证码
                    # 如果有前缀 "data:image/xxx;base64,", 需要去掉
                    if ',' in src:
                        base64_str = src.split(',')[1]

                    # 解码 base64 为字节流
                    img_bytes = base64.b64decode(base64_str)
                    captcha_code = self.__ocr.classification(img_bytes)
                    # 回填验证码
                    await captcha_code_input_element.fill(captcha_code)
                    # 再次点击登录按钮
                    await login_button_element.click()
                    try:
                        await page.wait_for_selector(".el-message.el-message--error", timeout=10000)
                    except TimeoutError:
                        # 获取userToken的cookie
                        cookies = await context.cookies()
                        for cookie in cookies:
                            if cookie["name"] == "userToken":
                                userToken = cookie["value"]
                                # 返回token
                                return userToken
                    # 防止验证码切换过快
                    await page.wait_for_timeout(2000)
                    login_count += 1
        except Exception as e:
            raise e
        finally:
            # 不管成功与否函数都要关闭
            for close_obj in (page, context, browser):
                await safe_close(close_obj)

    async def __refresh_user_token(self):
        """
        刷新token
        :return:
        """
        # 如果有登录任务正在运行
        if self.__login_in_progress is not None:
            # 已有协程在处理登录，我们等待它完成
            await self.__login_in_progress
            return

        # 没有登录任务，当前协程负责登录
        self.__login_in_progress = asyncio.get_event_loop().create_future()
        # 检测锁，确保只有一个线程在登录
        async with self.__login_lock:
            try:
                user_token = await self.__auto_login_4seller()
            except Exception as e:
                # 如果future没有被终结掉手动设置终结future
                if not self.__login_in_progress.done():
                    self.__login_in_progress.set_exception(e)
                logger.error(f'FourSeller自动登录失败 {e}')
                raise Exception(f'FourSeller登录身份失效, 尝试自动登录失败 {e}')
            else:
                # 登录成功后重置token
                self.user_token = user_token
                # 清空原cookies
                self.__async_client.cookies.clear()
                # 重新设置客户端的cookie
                self.__async_client.cookies.set('userToken', self.user_token, domain='www.4seller.com', path='/')
                # 如果future没有被终结掉手动设置终结future,否则会抛出异常影响回调执行
                if not self.__login_in_progress.done():
                    self.__login_in_progress.set_result(True)
                # 回调函数可能会失败，但是不能影响其它协程操作
                try:
                    await self.login_success_call_back(user_token)
                except Exception as e:
                    logger.error(f'FourSeller登录成功回调函数执行失败 {e}')
                    pass
            finally:
                # 提示登录任务完成
                self.__login_in_progress = None

    async def __request(self, url, method, retry_count=0, **kwargs):
        """
        4seller基本请求
        :param url: url路径
        :param method: 请求方法
        :param kwargs: 请求参数
        :return:
        """
        try:
            async with self.__sem:
                response = await self.__async_client.request(method, url, **kwargs)
        except ReadTimeout:
            raise Exception(f'FourSeller请求接口超时')
        except Exception as e:
            logger.error(f'FourSeller请求接口失败{e}')
            raise Exception(f'FourSeller请求接口失败{e}')
        else:
            try:
                data = response.json()
            except Exception as e:
                logger.error(f'FourSeller请求,json序列化失败{e},原始数据{response.text}')
                raise Exception(f'FourSeller请求,json序列化失败{e},原始数据{response.text}')
            else:
                if data.get('code') == ResponseCodeEnum.LOGIN_VALIDATION_FAILED:
                    # 刷新token
                    await self.__refresh_user_token()
                    if retry_count < 1:
                        # 最多重试一次
                        return await self.__request(url, method, 1, **kwargs)
                    else:
                        raise Exception(f'FourSeller登录成功后,再次请求登录验证失败, 请求接口{url}，返回信息{data}')
                return data

    async def __get(self, url, **kwargs):
        return await self.__request(url, 'GET', **kwargs)

    async def __post(self, url, **kwargs):
        return await self.__request(url, 'POST', **kwargs)

    async def __put(self, url, **kwargs):
        return await self.__request(url, 'PUT', **kwargs)

    async def __delete(self, url, **kwargs):
        return await self.__request(url, 'DELETE', **kwargs)

    async def __order_page_api(self, query_params: FourSellerOrderQueryModel):
        return await self.__post('/api/v2/order/page', json=query_params.model_dump(by_alias=True))

    async def __order_page_history_api(self, query_params: FourSellerOrderQueryModel):
        return await self.__post('/api/v2/order/history/page', json=query_params.model_dump(by_alias=True))

    async def order_page(self, query_params: FourSellerOrderQueryModel) -> Page[FourSellerOrderVO]:
        page_data = await self.__order_page_api(query_params)
        # 能到这里说明登录验证什么的都没有问题，接口返回代码也是代表成功
        if page_data.get('code') != ResponseCodeEnum.SUCCESS:
            raise Exception(f'FourSeller请求接口失败, 请求接口{page_data}')
        return parse_order(page_data.get('data'))

    async def order_page_history(self, query_params: FourSellerOrderQueryModel) -> Page[FourSellerOrderVO]:
        page_data = await self.__order_page_history_api(query_params)
        # 能到这里说明登录验证什么的都没有问题，接口返回代码也是代表成功
        if page_data.get('code') != ResponseCodeEnum.SUCCESS:
            raise Exception(f'FourSeller拉取历史分页订单失败, 请求接口{page_data}')
        return parse_order(page_data.get('data'))

    async def list_order(self, query_params: FourSellerOrderQueryModel) -> list[FourSellerOrderVO]:
        # 获取分页信息
        order_list = list()
        page = await self.order_page(query_params)
        # 采用并发提高速度
        page_order_task_list = list()
        for page_number in range(1, page.total_page + 1):
            page_order_task_list.append(
                self.order_page(query_params.copy(update={"page_current": page_number}))
            )
        page_list = await asyncio.gather(*page_order_task_list)
        # 所有的数据
        for every_page in page_list:
            # 插入数据
            order_list.extend(every_page.records)
        return order_list

    async def list_history_order(self, query_params: FourSellerOrderQueryModel):
        # 获取分页信息
        order_history_list = list()
        page = await self.order_page_history(query_params)
        # 采用并发提高速度
        page_order_task_list = list()
        for page_number in range(1, page.total_page + 1):
            page_order_task_list.append(self.order_page_history(
                query_params.copy(update={"page_current": page_number})
            ))
        page_list = await asyncio.gather(*page_order_task_list)
        # 所有的数据
        for every_page in page_list:
            # 插入数据
            order_history_list.extend(every_page.records)
        return order_history_list

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.__async_client.aclose()
