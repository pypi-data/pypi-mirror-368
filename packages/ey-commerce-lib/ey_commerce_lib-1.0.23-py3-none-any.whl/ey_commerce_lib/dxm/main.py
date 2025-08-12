import asyncio
import traceback

from httpx import AsyncClient, Timeout
from playwright.async_api import async_playwright

from ey_commerce_lib.dxm.constant.order import DxmOrderRuleType
from ey_commerce_lib.dxm.parser.common import get_page_info, get_purchase_pagination_info, get_tracking_page_info
from ey_commerce_lib.dxm.parser.count import parse_count
from ey_commerce_lib.dxm.parser.export_template import parse_list_export_template
from ey_commerce_lib.dxm.parser.order import list_order_base_by_html, list_order_rule, get_rule_detail, \
    get_order_detail_by_html, parse_comm_search_list_html_get_authid_dict
from ey_commerce_lib.dxm.parser.purchase import list_purchasing_all, list_1688_purchase_order_number, \
    list_wait_pay_page_purchase_order_number
from ey_commerce_lib.dxm.parser.tracking import parse_tracking_page
from ey_commerce_lib.dxm.parser.warehouse import list_warehouse_product
from ey_commerce_lib.dxm.schemas.common import Page
from ey_commerce_lib.dxm.schemas.dxm_commodity_product import ViewDxmCommodityProductResponse
from ey_commerce_lib.dxm.schemas.ebay_product import DxmEbayProductModel
from ey_commerce_lib.dxm.schemas.export_package import ExportPackageOrderModel
from ey_commerce_lib.dxm.schemas.order import DxmOrderSearchForm, DxmJsonResponse, DxmCheckProcessResponse, DxmOrderRule
from ey_commerce_lib.dxm.schemas.tracking import TrackingPageListQuery, TrackingPageListItem
from ey_commerce_lib.dxm.schemas.warehouse import WarehouseProduct, WarehouseProductQuery, PurchasingAllQuery


class DxmClient:

    def __init__(self, cookies: dict, headers: dict, sem: int = 10):
        self.__cookies = cookies
        self.__headers = headers
        self.__sem = asyncio.Semaphore(sem)
        timeout = Timeout(connect=60.0, read=60.0, write=60.0, pool=30.0)
        self.__base_url = 'https://www.dianxiaomi.com'
        self.__async_client = AsyncClient(base_url=self.__base_url, cookies=cookies, headers=headers,
                                          timeout=timeout)

    async def page_order_base_async(self, query: DxmOrderSearchForm):
        """
        条件分页查询订单基础信息
        :param query:
        :return:
        """
        # 查询分页数据
        data = await self.__async_client.post("/package/advancedSearch.htm", data=query.model_dump(by_alias=True))
        # 获取分页信息
        page_info = get_page_info(data.text)
        data = list_order_base_by_html(data.text)
        return {
            **page_info,
            'data': data
        }

    async def list_order_base_async(self, query: DxmOrderSearchForm):
        """
        条件查询订单信息列表
        :return:
        """
        query.page_no = 1
        data = await self.page_order_base_async(query)
        total_page = data['total_page']
        result = data['data']
        for page_number in range(2, total_page + 1):
            query.page_no = page_number
            data = await self.page_order_base_async(query)
            result.extend(data['data'])
        return result

    async def page_order_detail_async(self, query: DxmOrderSearchForm):
        async def set_detail(order_base: dict):
            """
            设置详情
            :param order_base:
            :return:
            """
            order_base['detail'] = await self.package_detail(order_base['package_id'])

        # 获取基本分页数据信息
        page_base_order = await self.page_order_base_async(query)
        # 获取并设置详情信息
        await asyncio.gather(*[
            set_detail(item)
            for item in page_base_order['data']])

        return page_base_order

    async def list_order_detail_async(self, query: DxmOrderSearchForm):
        query.page_no = 1
        data = await self.page_order_detail_async(query)
        total_page = data['total_page']
        result = data['data']
        for page_number in range(2, total_page + 1):
            query.page_no = page_number
            data = await self.page_order_detail_async(query)
            result.extend(data['data'])
        return result

    async def package_detail(self, package_id: str):
        """
        获取包裹的详情数据
        :param package_id:
        :return:
        """
        async with self.__sem:
            package_detail_res = await self.__async_client.post('/package/detail.htm', data={
                'packageId': package_id,
                'history': ''
            })
            return get_order_detail_by_html(package_detail_res.text)

    async def move_process(self, package_id: str) -> DxmJsonResponse:
        """
        申请运单号
        :return:
        """
        async with self.__sem:
            move_processed_json = await self.__async_client.post("/package/moveProcessed.json", data={
                "packageId": package_id
            })
            return move_processed_json.json()

    async def move_allocated(self, package_id: str) -> DxmJsonResponse:
        """
        移入待打单
        :param package_id:
        :return:
        """
        async with self.__sem:
            move_allocated_json = await self.__async_client.post("/package/moveAllocated.json", data={
                "packageId": package_id
            })
            return move_allocated_json.json()

    async def upload_track_num(self, package_id: str, track_num: str, auth_id) -> DxmJsonResponse:
        """
        上传运单号
        :param package_id: package_id
        :param track_num:  运单号
        :param auth_id: 物流方式id
        :return:
        """
        async with self.__sem:
            upload_track_num_json = await self.__async_client.post("/package/uploadTrackNum.json", data={
                "packageId": package_id,
                "trackNum": track_num,
                "authId": auth_id
            })
            return upload_track_num_json.json()

    async def get_warehouse_dict(self):
        """
        获取仓库字典映射
        :return:
        """
        warehouse_info_res = await self.__async_client.get("/dxmWarehoseCon/getWarehoseInfo.json")
        warehouse_info_dict = warehouse_info_res.json()
        result = dict()
        for item in warehouse_info_dict.items():
            result[item[1]['name']] = item[0]
        return result

    async def commit_platform(self, package_id: str):
        """
        虚拟发货
        :param package_id: 包裹id
        :return:
        """
        async with self.__sem:
            commit_platform_res = await self.__async_client.post("/package/commitPlatform.json", data={
                'packageId': package_id
            })
            return commit_platform_res.json()

    async def save_storage_id_for_order(self, package_id: str, storage_id: str):
        """
        订单详情修改订单仓库
        :param package_id:
        :param storage_id:
        :return:
        """
        async with self.__sem:
            save_storage_id_for_order_res = await self.__async_client.post("/package/saveStorageIdForOrder.json", data={
                'packageId': package_id,
                'storageId': storage_id,
                'pids': ''
            })
            return save_storage_id_for_order_res.json()

    async def __refresh_logistics_rule(self, uri: str, all_refresh: int):
        async with self.__sem:
            refresh_logistics_rule_res = await self.__async_client.post(f'/order/{uri}.json', data={
                'shopId': '-1',
                'platform': '',
                'allRefresh': f'{all_refresh}',
            })
            uuid = refresh_logistics_rule_res.json().get('uuid')
            check_process_res = await self.__check_process(uuid)
            # 任务没有完成就一直监测直到任务完成为止
            while int(check_process_res['processMsg']['num']) < int(check_process_res['processMsg']['totalNum']):
                check_process_res = await self.__check_process(uuid)
                await asyncio.sleep(1)
            return check_process_res

    async def refresh_logistics_rule_no_select_logistics_method(self) -> DxmCheckProcessResponse:
        """
        刷新物流规则(待处理中的未选择物流方式的订单)
        :return:
        """
        return await self.__refresh_logistics_rule(uri='refreshLogisticRule', all_refresh=0)

    async def refresh_logistics_rule_all(self) -> DxmCheckProcessResponse:
        """
        刷新物流规则(待处理中的所有订单)
        :return:
        """
        return await self.__refresh_logistics_rule(uri='refreshLogisticRule', all_refresh=1)

    async def refresh_rule_all(self):
        """
        刷新物流规则(待审核中的所有订单)
        :return:
        """
        return await self.__refresh_logistics_rule(uri='refreshRule', all_refresh=1)

    async def refresh_no_select_logistics_method_rule(self):
        """
        刷新物流规则(待审核未选择物流方式的订单)
        :return:
        """
        return await self.__refresh_logistics_rule(uri='refreshRule', all_refresh=0)

    async def __check_process(self, uuid: str) -> DxmCheckProcessResponse:
        """
        检测任务的进度
        :param uuid: 任务id
        :return:
        """
        async with self.__sem:
            check_process_res = await self.__async_client.post("/checkProcess.json", data={
                'uuid': uuid
            })
            return check_process_res.json()

    async def ship_goods(self, package_id: str):
        """
        发货
        :param package_id:
        :return:
        """
        async with self.__sem:
            ship_goods_res = await self.__async_client.post("/package/shipGoods.json", data={
                "packageId": package_id
            })
            return ship_goods_res.json()

    async def batch_ship_goods(self, package_ids: list):
        """
        批量发货
        :param package_ids: package_id列表
        :return:
        """
        async with self.__sem:
            batch_ship_goods_res = await self.__async_client.post("/package/batchShipGoods.json", data={
                "packageIds": ','.join(package_ids)
            })
            return batch_ship_goods_res.json()

    async def list_rule(self, rule_type: DxmOrderRuleType) -> dict:
        """
        获取审单规则列表
        :return:
        """
        async with self.__sem:
            list_rule_res = await self.__async_client.get("/rule/index.htm", params={
                'type': rule_type
            })
            list_rule_html = list_rule_res.text
            data = list_order_rule(list_rule_html)
            # 遍历设置Type
            for item in data:
                item['type'] = rule_type.value
            return data

    async def get_rule_id_by_name(self, rule_name: str, rule_type: DxmOrderRuleType) -> str:
        """
        根据规则名称获取规则
        :param rule_name:
        :param rule_type:
        :return:
        """
        data = await self.list_rule(rule_type)
        for item in data:
            if item['rule_name'] == rule_name:
                return item['rule_id']

    async def rule_detail(self, rule_id: str, rule_type: int):
        """
        获取审单规则详情
        :param rule_id:
        :param rule_type:
        :return:
        """
        async with self.__sem:
            rule_detail_res = await self.__async_client.get("/rule/detail.htm", params={
                'id': rule_id,
                'type': rule_type,
                'isCopy': '0'
            })
            rule_detail_html = rule_detail_res.text
            return get_rule_detail(rule_detail_html)

    async def update_rule(self, dxm_rule_order: DxmOrderRule):
        """
        更新审单规则
        :param dxm_rule_order:
        :return:
        """
        data = dxm_rule_order.to_update_rule_data()
        async with self.__sem:
            update_rule_res = await self.__async_client.post("/rule/update.json", content=data)
            return update_rule_res.json()

    async def edit_rule_state(self, rule_id: str, state: int):
        """
        编辑规则状态
        :param rule_id: 规则id
        :param state: 1启用 0禁用
        :return:
        """
        async with self.__sem:
            edit_rule_state_res = await self.__async_client.post("/rule/editRuleState.json", data={
                'id': rule_id,
                'state': state
            })
            return edit_rule_state_res.json()

    async def enable_rule(self, rule_id: str):
        """
        启用规则
        :param rule_id:
        :return:
        """
        return await self.edit_rule_state(rule_id, 1)

    async def disable_rule(self, rule_id: str):
        """
        禁用规则
        :param rule_id:
        :return:
        """
        return await self.edit_rule_state(rule_id, 0)

    async def batch_enable_rule(self, rule_id_list: list):
        """
        批量启用规则
        :param rule_id_list:
        :return:
        """
        await asyncio.gather(*[self.enable_rule(rule_id) for rule_id in rule_id_list])

    async def batch_disable_rule(self, rule_id_list: list):
        """
        批量禁用规则
        :param rule_id_list:
        :return:
        """
        await asyncio.gather(*[self.disable_rule(rule_id) for rule_id in rule_id_list])

    async def page_warehouse_product(self, query: WarehouseProductQuery) -> Page[WarehouseProduct]:
        """
        分页查询仓库商品
        :param query: 查询条件
        :return:
        """
        async with self.__sem:
            page_warehouse_product_res = await self.__async_client.post("/warehouseProduct/pageList.htm",
                                                                        data=query.model_dump(by_alias=True))
            return Page(data=list_warehouse_product(page_warehouse_product_res.text),
                        **get_page_info(page_warehouse_product_res.text))

    async def list_warehouse_product(self, query: WarehouseProductQuery) -> list[WarehouseProduct]:
        """
        查询仓库商品
        :param query:
        :return:
        """
        data = await self.page_warehouse_product(query)
        total_page = data.total_page
        result = data.data
        for page_number in range(2, total_page + 1):
            query.page_no = page_number
            data = await self.page_warehouse_product(query)
            result.extend(data.data)
        return result

    async def page_purchasing_all(self, query: PurchasingAllQuery):
        """
        分页查询采购单全部
        :return:
        """
        async with self.__sem:
            page_purchasing_all_pageList_res = await self.__async_client.post(
                "/dxmPurchasingNote/purchasingAllPageList.htm",
                data=query.model_dump(by_alias=True))
            page_info = get_purchase_pagination_info(page_purchasing_all_pageList_res.text)
            return {
                **page_info,
                'data': list_purchasing_all(page_purchasing_all_pageList_res.text)
            }

    async def list_purchasing_all(self, query: PurchasingAllQuery):
        """
        查询采购单全部列表
        :param query:
        :return:
        """
        query.page_no = 1
        data = await self.page_purchasing_all(query)
        total_page = data['total_page']
        result = data['data']
        for page_number in range(2, total_page + 1):
            query.page_no = page_number
            data = await self.page_purchasing_all(query)
            result.extend(data['data'])
        return result

    async def wait_pay_page_list(self, data: dict):
        """
        采购分页
        :return:
        """
        async with self.__sem:
            page_purchasing_all_pageList_res = await self.__async_client.post(
                "/dxmPurchasingNote/waitPayPageList.htm",
                data=data)
            page_info = get_page_info(page_purchasing_all_pageList_res.text)
            purchase_order_number_list = list_wait_pay_page_purchase_order_number(page_purchasing_all_pageList_res.text)
            # 200个200个一批进行处理
            page_data = list()
            for i in range(0, len(purchase_order_number_list), 200):
                search_value = ','.join(purchase_order_number_list[i:i + 200])
                data = await self.list_purchasing_all(PurchasingAllQuery(search_value=search_value
                                                                         , search_type=0))
                page_data.extend(data)
            return {
                **page_info,
                'data': page_data
            }

    async def wait_pay_list(self, data: dict):
        """
        采购订单其它查询列表
        :param data:
        :return:
        """
        async with self.__sem:
            data['pageNo'] = 1
            wait_pay_page_list_res = await self.wait_pay_page_list(data)
            total_page = wait_pay_page_list_res['total_page']
            result = wait_pay_page_list_res['data']
            for page_number in range(2, total_page + 1):
                data['pageNo'] = page_number
                wait_pay_page_list_res = await self.wait_pay_page_list(data)
                result.extend(wait_pay_page_list_res['data'])
            return result

    async def wait_pay_alibaba_page_list(self, data: dict):
        """
        采购订单1688采购分页
        :return:
        """
        wait_pay_alibaba_page_list_res = await self.__async_client.post('/dxmPurchasingNote/waitPayAliBabaPageList.htm',
                                                                        data=data)
        page_info = get_page_info(wait_pay_alibaba_page_list_res.text)
        purchase_order_number_list = list_1688_purchase_order_number(wait_pay_alibaba_page_list_res.text)
        # 分页数据
        page_data = list()
        # 200个一批进行搜索
        for i in range(0, len(purchase_order_number_list), 200):
            search_value = ','.join(purchase_order_number_list[i:i + 200])
            data = await self.list_purchasing_all(PurchasingAllQuery(search_value=search_value
                                                                     , search_type=0))
            page_data.extend(data)
        return {
            **page_info,
            'data': page_data
        }

    async def wait_pay_alibaba_list(self, data: dict):
        """
        采购订单1688采购列表
        :param data:
        :return:
        """
        data['pageNo'] = 1
        wait_pay_alibaba_page_list_res = await self.wait_pay_alibaba_page_list(data)
        total_page = wait_pay_alibaba_page_list_res['total_page']
        result = wait_pay_alibaba_page_list_res['data']
        for page_number in range(2, total_page + 1):
            data['pageNo'] = page_number
            wait_pay_alibaba_page_list_res = await self.wait_pay_alibaba_page_list(data)
            result.extend(wait_pay_alibaba_page_list_res['data'])
        return result

    async def __sync_alibaba_order(self):
        """
        采购全部同步订单
        :return:
        """
        async with self.__sem:
            sync_alibaba_order_response = await self.__async_client.post("/dxmPurchasingNote/syncAliBabaOrder.json")
            return sync_alibaba_order_response.json()

    async def sync_alibaba_order(self):
        """
        同步采购全部订单
        :return:
        """
        sync_alibaba_order_data = await self.__sync_alibaba_order()
        process_uuid = sync_alibaba_order_data.get('uuid')
        while True:
            # 查询同步进度
            check_process_res = await self.__check_process(process_uuid)
            process_code = check_process_res.get('processMsg').get('code')
            if process_code:
                # 同步完成结束监测
                break
            await asyncio.sleep(1)

    async def validate_price(self, ids: str):
        """
        采购校验价格
        :param ids: purchase_id 多个,分隔
        :return:
        """
        validate_price_res = await self.__async_client.post("/dxmPurchasingNote/validatePrice.json", data={
            'ids': ids
        })
        return validate_price_res.json()

    async def wait_pay_pay_money(self, purchase_id: str):
        """
        采购订单支付(通过审核)
        :param purchase_id:
        :return:
        """
        async with self.__sem:
            wait_pay_pay_money_res = await self.__async_client.post("/dxmPurchasingNote/waitPayPayMoney.json", data={
                'id': purchase_id,
                'auditResult': '1',
            })
            return wait_pay_pay_money_res.json()

    async def submit_audit(self, purchase_id: str):
        """
        提交审核
        :param purchase_id:
        :return:
        """
        async with self.__sem:
            submit_audit_res = await self.__async_client.post("/dxmPurchasingNote/submitAudit.json", data={
                'id': purchase_id
            })
            return submit_audit_res.json()

    async def get_order_mark_content(self):
        """
        获取订单标记内容列表
        :return: 订单标记内容列表
        """
        async with self.__sem:
            get_order_mark_content_res = await self.__async_client.get('/package/getOrderMarkContent.json')
            get_order_mark_content_data = get_order_mark_content_res.json()
            if get_order_mark_content_data.get('code') != 0:
                raise Exception(f'获取订单标记数据失败错误原因{get_order_mark_content_data.get('msg')}')
            data = get_order_mark_content_data.get('data', {})
            result = []
            for key in data.keys():
                val = data.get(key)
                val['key'] = key
                result.append(val)
            return result

    async def add_or_update_user_comment(self, data):
        """
        添加或修改订单自定义标记
        :param data:
        :return:
        """
        async with self.__sem:
            add_or_update_user_comment_res = await self.__async_client.post('/package/addOrUpdateUserComment.json',
                                                                            data=data)
            return add_or_update_user_comment_res.json()

    async def get_picking_comment_by_pack_id(self, package_id: str):
        """
        获取订单备注(只有拣货说明)
        :param package_id:
        :return: 没有返回None 有返回字典数据
        """
        async with self.__sem:
            data = {
                'packageId': package_id,
            }
            get_comment_by_pack_id_res = await self.__async_client.post('/dxmPackageComment/getByPackId.json',
                                                                        data=data)
            data = get_comment_by_pack_id_res.json()
            if data.get('code') != 0:
                raise Exception(f'获取订单标记数据失败错误原因{data.get("msg")}')
            return data.get('dxmPackageComment')

    async def add_comment(self, pacakge_id: str, comment_type: str, content: str, color: str, comment_id: str = '',
                          history: str = ''):
        """
        添加订单标记
        :param pacakge_id:
        :param comment_type: 备注类型 sys_picking(拣货备注)  sys_service(客服v备注)
        :param content: 备注内容
        :param color: 颜色值
        :param comment_id: 备注id(只有)
        :param history:
        :return:
        """
        if comment_type not in ['sys_picking', 'sys_service']:
            raise Exception(f'备注类型只能是拣货说明和客服备注，当前是{comment_type}')
        data = {
            'packageId': pacakge_id,
            'commentType': comment_type,
            'content': content,
            'color': color,
            'history': history
        }
        if comment_type == 'sys_service':
            if str(comment_id).strip() == '':
                raise Exception(f'客服备注必须指定备注id')
            # 修改客服备注要指定备注id
            data['commentId'] = comment_id
        async with self.__sem:
            add_comment_res = await self.__async_client.post('/dxmPackageComment/add.json', data=data)
            data = add_comment_res.json()
            if data.get('code') != 0:
                raise Exception(f'添加订单标记数据失败错误原因{add_comment_res.json().get("msg")}')
            return data

    async def get_state_count_api(self):
        """
        获取订单各个状态统计api
        :return:
        """
        async with self.__sem:
            get_state_res = await self.__async_client.post('/package/getStateCount.json')
            return get_state_res.json()

    async def __stat_index(self):
        """
        获取店小秘订单统计页api
        :return:
        """
        async with self.__sem:
            params = {
                'shopIds': 'all',
                'isIndex': '1',
                'currency': 'USD',
            }
            stat_index_res = await self.__async_client.get('/stat/order/orderPerform.htm', params=params)
            stat_index_html = stat_index_res.text

            return parse_count(stat_index_html)

    async def list_order_count(self):
        """
        获取店小秘订单统计
        :return:
        """

        return await self.__stat_index()

    async def ebay_product_page_list(self, query_params: DxmEbayProductModel):
        """
        ebay在线产品列表
        :param query_params: 查询参数
        :return:
        """
        query_data = query_params.model_dump(by_alias=True)
        async with self.__sem:
            ebay_product_page_res = await self.__async_client.post('/ebayProduct/pageList.htm', data=query_data)
            ebay_product_page_text = ebay_product_page_res.text
            # TODO 完成后续的逻辑

    async def view_dxm_commodity_product(self, proid: str):
        """
        仓库管理-商品管理-查看店小秘商品
        :param proid:
        :return:
        """
        data = {
            'id': proid,
        }
        async with self.__sem:
            view_dxm_commodity_product_res = await self.__async_client.post(
                '/dxmCommodityProduct/viewDxmCommodityProduct.json',
                data=data)
            return ViewDxmCommodityProductResponse.model_validate(view_dxm_commodity_product_res.json())

    async def update_dxm_commodity_front_sku(self, proid: str, front_sku: str):
        """
        更新店小秘 仓库-商品详情中的平台sku
        :param proid:
        :param front_sku:
        :return:
        """
        # 打开浏览器
        # 打开浏览器
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--start-maximized',
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage'
                    ]
                )
                context = await browser.new_context()
                # 设置cookie和headers
                await context.add_cookies([
                    {
                        "name": name,  # cookie 名称
                        "value": value,  # cookie 值
                        "domain": ".dianxiaomi.com",  # 替换为你的目标域名
                        "path": "/",  # cookie 路径
                    }
                    for name, value in self.__cookies.items()
                ])
                page = await context.new_page()
                # 访问
                await page.goto(f'{self.__base_url}/dxmCommodityProduct/openEditModal.htm?id={proid}&editOrCopy=0',
                                timeout=60000)
                # 关闭模态框
                try:
                    await page.locator(
                        '#theNewestModalLabel > div.modal-dialog > div > div.modal-header > button').click()
                except:
                    pass
                # 输入sku
                await page.locator('input.variationValue.ui-autocomplete-input').fill(front_sku)
                # 失去焦点
                await page.locator('input.variationValue.ui-autocomplete-input').press('Tab')
                try:
                    # 休眠两秒
                    error_text = await page.text_content(selector='div.alert-dangerRed span', timeout=2000)
                    return {
                        'code': 500,
                        'msg': error_text
                    }
                except Exception as e:
                    # 创建监听任务
                    async def wait_for_api1():
                        async with page.expect_response(
                                f"{self.__base_url}/dxmCommodityProduct/editCommodityProduct.json") as response_info:
                            pass
                        return await response_info.value

                    async def wait_for_api2():
                        async with page.expect_response(
                                f"{self.__base_url}/dxmCommodityProduct/editCommodityProductGroup.json") as response_info:
                            pass
                        return await response_info.value

                    # 创建并发任务
                    task1 = asyncio.create_task(wait_for_api1())
                    task2 = asyncio.create_task(wait_for_api2())
                    # 点击保存按钮
                    await page.locator('.button.btn-orange.m-left10').first.click()
                    # 等待任何一个请求完成
                    done, pending = await asyncio.wait(
                        [task1, task2],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    # 取消其他未完成的任务
                    for task in pending:
                        task.cancel()
                    # 获取完成的请求结果
                    completed_task = list(done)[0]
                    response = await completed_task
                    return await response.json()
        except Exception as e:
            return {
                'code': 500,
                'msg': traceback.format_exc()
            }

    async def tracking_page_list(self, query: TrackingPageListQuery) -> Page[TrackingPageListItem]:
        """
        分页查询物流追踪页表
        :param query:
        :return:
        """
        async with self.__sem:
            tracking_page_list_response = await self.__async_client.post('/tracking/pageList.htm',
                                                                         data=query.model_dump(by_alias=True))
            tracking_page_list_html = tracking_page_list_response.text
            page = get_tracking_page_info(tracking_page_list_html)
            page.records = parse_tracking_page(tracking_page_list_html)
            return page

    async def tracking_list(self, query: TrackingPageListQuery) -> list[TrackingPageListItem]:
        async with self.__sem:
            query.page_no = '1'
            tracking_page_list_response = await self.__async_client.post('/tracking/pageList.htm',
                                                                         data=query.model_dump(by_alias=True))
            tracking_page_list_html = tracking_page_list_response.text
            # 获取分页数据
            page = get_tracking_page_info(tracking_page_list_html)
            # 获取总页数
            total_page = page.total_page
            # 最终记录
            result = parse_tracking_page(tracking_page_list_html)
            for page_num in range(2, total_page + 1):
                query.page_no = str(page_num)
                # 获取分页数据
                page_data = await self.tracking_page_list(query)
                result.extend(page_data.records)
            return result

    async def tracking_show_detail(self, tracking_number: str, carrier_code: str):
        """
        物流追踪详情信息
        """
        async with self.__sem:
            tracking_show_detail_response = await self.__async_client.post('/tracking/showDetail.json', data={
                "trackingNumber": tracking_number,
                "carrierCode": carrier_code
            })
            return tracking_show_detail_response.json()

    async def order_prior_or_ban_ship(self, package_id: str, type_value: str):
        """
        禁运或优先发货
        :param package_id:
        :param type_value:
        :return:
        """
        async with self.__sem:
            order_prior_or_ban_ship_response = await self.__async_client.post('/order/orderPriorOrBanShip.json', data={
                'packageId': package_id,
                'type': type_value,
            })
            return order_prior_or_ban_ship_response.json()

    async def reply_msg(self, package_id: str, content: str):
        """
        回复消息
        """
        data = f'packageId={package_id}&content={content}'
        async with self.__sem:
            reply_msg_response = await self.__async_client.post('/replyMsg/reply.json', content=data)
            return reply_msg_response.json()

    async def get_authid_like_keyword(self, keyword: str) -> dict:
        """
        获取店小秘物流方式id,通过关键字模糊查询
        :param keyword: 关键字
        :return:
        """
        async with self.__sem:
            data = {
                'state': '',
                'isVoided': '-1',
                'isOversea': '-1',
                'commitPlatform': '',
                'prefixCount': '200',
                'newVersion': '0',
                'history': '',
                'isBatch': '-1',
                'isFree': '-1',
            }

            response = await self.__async_client.post('/package/commSearchList.htm', data=data)
            comm_search_list_html = response.text
            return parse_comm_search_list_html_get_authid_dict(comm_search_list_html, keyword)

    async def export_template_get_by_id_json(self, id_str: str):
        """
        根据id获取导出模板配置
        :param id_str: 模板id
        :return:
        """
        async with self.__sem:
            response = await self.__async_client.post('/exportTemplate/getById.json', data={
                'id': id_str
            })
            return response.json()

    async def list_export_template(self):
        """
        获取导出模板的列表
        :return:
        """
        async with self.__sem:
            response = await self.__async_client.post('/exportTemplate/index.htm')
            return parse_list_export_template(response.text)

    async def export_package_order(self, data: ExportPackageOrderModel):
        """
        导出包裹订单
        :param data: 导出参数模型类
        :return:
        """
        async with self.__sem:
            response = await self.__async_client.post('order/exportPackageOrder.json',
                                                      data=data.model_dump(by_alias=True))
            uuid = response.json().get('uuid')
            if not uuid:
                raise Exception('导出失败')
            code = 0
            msg = ''
            # 如果导出状态没有完成就一直循环
            while code == 0:
                check_process_res = await self.__check_process(uuid)
                code = check_process_res.get('processMsg').get('code')
                msg = check_process_res.get('processMsg').get('msg')
                print(f'导出中,{check_process_res}')
                await asyncio.sleep(5)
            # code为1代表导出成功
            if code != 1:
                raise Exception(f'导出失败，失败原因:{msg}')
            return msg

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.__async_client.aclose()
