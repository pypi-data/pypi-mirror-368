from httpx import AsyncClient, Timeout

from ey_commerce_lib.kogan.schemas.query.order import KoganOrderQuery
from ey_commerce_lib.kogan.schemas.query.product import KoganProductQuery
from ey_commerce_lib.kogan.schemas.response.order import OrderResponseModel
from ey_commerce_lib.kogan.schemas.response.product import ProductResponse


class KoganClient:

    def __init__(self, seller_id: str, seller_token: str):
        self.seller_id = seller_id
        self.seller_token = seller_token
        timeout = Timeout(connect=60.0, read=60.0, write=60.0, pool=30.0)

        # 异步客户端
        self.__async_client = AsyncClient(base_url="https://nimda.kogan.com",
                                          headers={
                                              'Accept': 'application/json',
                                              'SellerId': self.seller_id,
                                              'SellerToken': self.seller_token
                                          },
                                          timeout=timeout
                                          )

    async def orders(self, query_params: KoganOrderQuery):
        # 设置查询参数
        orders_res = await self.__async_client.get('/api/marketplace/v2/orders/',
                                                   params=query_params.model_dump(by_alias=True,
                                                                                  exclude_none=True))
        return OrderResponseModel(**orders_res.json())

    async def products(self, query_params: KoganProductQuery):
        products_res = await self.__async_client.get('/api/marketplace/v2/products/',
                                                     params=query_params.model_dump(by_alias=True,
                                                                                    exclude_none=True
                                                                                    ))

        return ProductResponse(**products_res.json())

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.__async_client.aclose()
