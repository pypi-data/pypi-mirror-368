from typing import Optional

from pydantic import BaseModel, ConfigDict

from ey_commerce_lib.utils.str import to_camel


class WarehouseProductQuery(BaseModel):
    refresh_flag: str = ''
    # 8(全部区)6(次品区)0(拣货区)
    zone_type: int = 0
    # 页码
    page_no: int = 1
    # 每页条数
    page_size: int = 100
    # 搜索类型1(商品sku)4(商品编码)2(商品名称)3(货架位)4(识别码)
    search_type: int = 1
    # 搜索内容
    search_value: str = ''
    # 匹配方式1(精确匹配)0(模糊匹配)2(完全匹配)
    product_search_type: int = 1
    # 仓库id
    warehouse_id: str = '7167025'
    is_transit: str = ''
    # 筛选排序 1(按照创建时间)2(按更新时间)3(按sku)4(按库存总量)5(按单价)6(按采购在途)7(按总价)8(按货架位)9(按可用库存)10(按未发)
    order_by: str = '1'
    # 排序方式 1(降序)0(升序)
    order_by_val: str = '1'
    # 分类路径用-分隔最后以-结尾 例如1379550-1379554-1379559-
    full_cid: str = ''
    # 类型 全部('')单个sku(0)组合sku(1)加工sku(2)
    group_or_not: str = ''
    # 商品单价开始
    price_min: str = ''
    # 商品单价结束
    price_max: str = ''
    # 总库存起始
    stock_min: str = ''
    # 总库存结束
    stock_max: str = ''
    # 可用库存起始
    available_min: str = ''
    # 可用库存结束
    available_max: str = ''
    # 安全库存开始
    safe_min: str = ''
    # 安全库存结束
    safe_max: str = ''
    # 采购在途开始
    on_pass_min: str = ''
    # 采购在途结束
    on_pass_max: str = ''
    # 预售数量起始
    lock_min: str = ''
    # 预售数量结束
    lock_max: str = ''
    # 未发数量起始
    un_billed_order_min: str = ''
    # 未发数量结束
    un_billed_order_max: str = ''
    # 仓库商品状态 -1(全部)0(在售)1(热销)2(新品)3(清仓)4(停售)5(滞销)
    product_status: str = '-1'

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True  # 对应旧版的 allow_population_by_field_name
    )


class WarehouseProduct(BaseModel):
    proid: str
    sku: str
    name: Optional[str] = None
    sku_code: str
    shelf_position: str
    # 安全库存
    safe_stock: Optional[int] = None
    # 在途库存
    on_the_way_stock: Optional[int] = None
    # 未发库存
    not_shipped_stock: Optional[int] = None
    # 占用库存
    occupy_stock: Optional[int] = None
    # 可用库存
    available_stock: Optional[int] = None
    # 总库存
    total_stock: Optional[int] = None
    # 更新时间
    update_time: str
    # 创建时间
    create_time: str


class PurchasingAllQuery(BaseModel):
    """
    采购订单全部查询参数
    """
    page_no: int = 1
    page_size: int = 300
    # 搜索类型0(采购单号)1(供货商)2(商品sku)6(商品编码)5(商品名称)4(1688单号)3(运单号)7(关联单号)8(采购单备注)9(商品备注)
    search_type: int = 0
    # 搜索内容
    search_value: str = ''
    # 搜索模式1(精确匹配)0(模糊匹配)2(完全匹配)
    search_mode: int = 1
    # 评论颜色使用,分隔
    comment_colors: str = ''
    # 仓库id
    warehouse_id: str = ''

    # 店铺id(或者1688账号)
    authorization_id: str = ''
    # 排序方式: 1(按创建时间) 2(按更新时间) 4(按照采购单号)5(按照供货商名)
    purchasing_px: int = 2
    # 排序方式: asc(升序) desc(降序)
    purchasing_px_val: str = 'desc'
    is_advance_search: str = 'Y'
    # 采购金额起始
    price_left: str = ''
    # 采购金额结束
    price_right: str = ''
    # 采购数量起始
    quantity_left: str = ''
    # 采购数量结束
    quantity_right: str = ''
    # 创建时间开始
    create_start_time: str = ''
    # 创建时间结束
    create_end_time: str = ''
    # 快递签收时间开始
    end_time_start: str = ''
    # 快递签收时间结束
    end_time_end: str = ''
    # 到货时间开始
    arrive_start_time: str = ''
    # 到货时间结束
    arrive_end_time: str = ''
    # 供货商id
    supplier_id: str = ''
    # 采购员id
    agent_id: str = ''
    # 结算方式 1(款到发货)2(货到付款)3(账期付款)4(其它)5(账期付款周结)6(账期付款半月结)7(账期付款月结)
    settlement_method: str = ''
    # 订单状态
    cur_states: str = ''
    # 付款状态
    submit_states: str = ''
    # 到货状态
    arrive_state: str = ''
    # 消息标记-有留言(勾选是Y)
    has_comment: str = ''
    # 消息标记-有备注(勾选是Y)
    has_remark: str = ''
    # 无备注
    no_has_comment: str = ''
    # 下单类型2(1688采购)3(手工采购)''(全部)
    is_alibaba: str = ''
    # 物流信息 ''(全部)2(有运单号)3(无运单号)
    is_have_identify_no: str = ''

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )
