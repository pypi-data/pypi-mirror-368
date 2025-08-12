from pydantic import BaseModel, ConfigDict

from ey_commerce_lib.utils.str import to_camel


class FourSellerOrderQueryModel(BaseModel):
    # 页码
    page_current: int = 1
    # 每页条数
    page_size: int = 100
    # 平台
    platform: str = ""
    # 店铺id列表
    shop_id_list: list[str] = []
    # 仓库id 页面未知来源
    warehouse_id: str = ""
    # 物流id 例如: 13554
    logistics_service_id: str = ""
    # 物流服务id映射关系父子id,id连接起来 例如: ["470", "13554"]
    logistics_service_map: list[str] = []
    # 单品单数: onlyOne 全部包裹类型: "" 单品多数: gtOne 多品: multiple
    item_type: str = ""
    """
    打印状态  全部: "" 面单已打印: labelPrinted   面单未打印: labelUnPrinted  装箱已打印: packingPrinted   装箱未打印: packingUnPrinted 
    拣货单已打印: pickPrinted  拣货单未打印: pickUnPrinted    
    """
    print_status: str = ""
    # 买家指定
    shipping_method: list[str] = []
    # 搜索类型  订单号: orderNo   物流跟踪号: trackNo  其余请参考页面
    search_type: str = "orderNo"
    # 搜索方式  模糊: like  精确: exact
    search_method: str = "exact"
    # 搜索内容
    search_value: str = ""
    # 商品总数最小
    item_min: str = ""
    # 商品总数最大
    item_max: str = ""
    # 重量最小
    weight_min: str = ""
    # 重量最大
    weight_max: str = ""
    # 重量单位 lb oz kg g
    weight_unit: str = "lb"
    # 到期时间 如果是数字就是小时  如果为空字符串是全部
    expires_hour: str | int = ""
    hours: str = ""
    # 平台状态 待发货: Awaiting_Shipment  待揽收: Awaiting_Collection 其它参考页面
    platform_status: str = ""
    # 发货地址id   如果为空字符串就是没有选择
    ship_from_address_id: str | int = ""
    # 国家编码 具体参考筛选页面
    country_code: str = ""
    # 国家名称 具体参考筛选页面
    country_name: str = ""
    # 省份或者洲
    state: str = ""
    # 买家备注 空字符串未选 有:1 无: 0
    buyer_note: str | int = ""
    # 卖家备注 空字符串未选 有:1 无: 0
    seller_note: str = ""
    # 系统备注: 空字符串未选 有:1 无: 0
    internal_note: str = ""
    # 平台标记 PRE_SALE: Temu预售
    platform_marker: str = ""
    # 下单时间 这个时间比上海时间要晚7个小时
    date_query_create_start_time: str = ""
    date_query_create_end_time: str = ""
    # 付款时间
    date_query_paid_start_time: str = ""
    date_query_paid_end_time: str = ""
    # 发货时间
    date_query_ship_start_time: str = ""
    date_query_ship_end_time: str = ""
    # 打印面单时间
    date_query_print_label_start_time: str = ""
    date_query_print_label_end_time: str = ""
    # 取消订单时间
    date_query_cancel_start_time: str = ""
    date_query_cancel_end_time: str = ""
    # 标签页 具体参考筛选页面
    tag_id_list: list[str] = []
    # 订单状态 全部: 空字符串  未付款: un_paid 已发货: shipped  待处理: to_ship  风控中: on_hold  处理中: in_process 已签收: delivered 参考页面
    all_order_status: str = ""
    # 订单状态: 全部: all 已发货: shipped
    order_status: str = "all"
    # 排序字段
    order_by: str = "orderPaidTime"
    # 排序方式 asc: 升序 desc: 降序
    desc: str = "asc"

    country: str = ""
    note_query: str = ""
    tag_query: str = ""
    exception_type: str = ""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )
