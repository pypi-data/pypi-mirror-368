import json
import urllib.parse

import pytest

from ey_commerce_lib.dxm.constant.order import ORDER_SEARCH_APPROVAL_BASE_FORM, \
    ORDER_SEARCH_PENDING_PROCESSING_BASE_FORM, ORDER_SEARCH_SELF_WAREHOUSE_BASE_FORM, \
    ORDER_SEARCH_OUT_OF_STOCK_BASE_FORM, ORDER_SEARCH_HAVE_GOODS_BASE_FORM
from ey_commerce_lib.dxm.main import DxmClient
from ey_commerce_lib.dxm.schemas.export_package import ExportPackageOrderModel
from ey_commerce_lib.dxm.schemas.order import DxmOrderSearchForm
from ey_commerce_lib.dxm.schemas.tracking import TrackingPageListQuery
from ey_commerce_lib.dxm.schemas.warehouse import WarehouseProductQuery
from ey_commerce_lib.dxm.utils.mark import get_custom_mark_content_list_by_data_custom_mark, \
    generate_add_or_update_user_comment_data_by_content_list
from ey_commerce_lib.four_seller.main import FourSellerClient
from ey_commerce_lib.four_seller.schemas.query.order import FourSellerOrderQueryModel
from ey_commerce_lib.takesend.main import TakeSendClient
import ey_commerce_lib.dxm.utils.dxm_commodity_product as dxm_commodity_product_util


async def login_success(user_token: str):
    print(f'user_token: {user_token}')
    pass


@pytest.mark.asyncio
async def test_auto_login_4seller():
    # print(user_token)
    async with FourSellerClient(
            user_name="xxxxx",
            password="xxxxxx",
            login_success_call_back=login_success,
            user_token="xxxxxx") as four_seller_client:
        await four_seller_client.list_history_order(FourSellerOrderQueryModel())


cookies = {

}

headers = {

}


@pytest.mark.asyncio
async def test_dxm_api():
    async with (DxmClient(headers=headers, cookies=cookies) as dxm_client):
        # data = await dxm_client.list_order_detail_async(query=ORDER_SEARCH_HAVE_GOODS_BASE_FORM)
        # for order in data:
        #     for pair_info in order.get('detail').get('pair_info_list'):
        #         print(pair_info.get('proid'))
        # data = await dxm_client.update_dxm_commodity_front_sku('17773195771232287', 'fuck112')
        # data = await dxm_client.get_authid_like_keyword('泰嘉')
        data = await dxm_client.list_export_template()
        for item in data:
            if item.get('template_name') == '周报订单导出模板':
                template_json = await dxm_client.export_template_get_by_id_json(id_str=item.get('template_id'))
                template_id = template_json.get('template').get('id')
                template_field = template_json.get('template').get('templateField')
                url = await dxm_client.export_package_order(ExportPackageOrderModel(
                    # 模板id
                    template_id=f'{template_id}',
                    # 导出字段
                    export_keys=urllib.parse.quote(template_field),
                    # 按包裹导出
                    export_type='1',
                    # 发货时间
                    time_type='2',
                    # 已发货
                    state='shipped',
                    start_time='2025-08-06 00:00:00',
                    end_time='2025-08-12 23:59:59'
                ))
                print(f'导出成功,url={url}')


@pytest.mark.asyncio
async def test_warehouse():
    async with (DxmClient(headers=headers, cookies=cookies) as dxm_client):
        print(await dxm_client.page_warehouse_product(WarehouseProductQuery()))


@pytest.mark.asyncio
async def test_tasksend_api():
    async with (TakeSendClient(username="", password="") as tasksend_client):
        await tasksend_client.login()
