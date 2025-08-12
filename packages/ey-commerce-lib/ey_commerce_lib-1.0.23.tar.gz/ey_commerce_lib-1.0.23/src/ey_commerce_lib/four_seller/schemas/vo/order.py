from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class FourSellerOrderAddressVo(BaseModel):
    # 地址 ID
    id: int

    # 收件人姓名
    name: str

    # 城市
    city: str

    # 邮编
    postal_code: Optional[str] = Field(..., alias="postalCode")

    # 完整地址
    address: str

    # 电话
    phone: str

    # 邮箱
    email: str

    # 国家代码
    country_code: str = Field(..., alias="countryCode")

    # 区/县
    county: Optional[str]

    # 地址行1
    address1: str

    # 地址行2
    address2: Optional[str]

    # 地址行3
    address3: Optional[str] = Field(None)

    # 州/省
    state: Optional[str] = Field(None)

    # 地址备注
    msg: Optional[str] = Field(None)

    # 地址备注映射
    msg_map: Optional[dict] = Field(None, alias="msgMap")

    # 是否住宅
    residential: Optional[bool]

    # 是否检查地址
    check_address: bool = Field(..., alias="checkAddress")

    model_config = ConfigDict(
        populate_by_name=True
    )


class FourSellerTimeInfoVO(BaseModel):
    # 订单支付时间
    order_paid_time: Optional[str] = Field(..., alias="orderPaidTime")

    # 订单创建时间
    order_create_time: str = Field(..., alias="orderCreateTime")

    # 最晚发货日期
    latest_ship_date: Optional[str] = Field(..., alias="latestShipDate")

    # 发货时间
    order_shipped_time: Optional[str] = Field(..., alias="orderShippedTime")

    # 最晚送达日期
    latest_delivery_date: Optional[str] = Field(..., alias="latestDeliveryDate")

    # 取消时间
    cancel_time: Optional[str] = Field(..., alias="cancelTime")

    # 剩余天数
    leave_day: int = Field(..., alias="leaveDay")

    model_config = ConfigDict(
        populate_by_name=True
    )


class FourSellerPackageInfoVO(BaseModel):
    # 重量
    weight: Optional[float]

    # 重量单位
    weight_unit: Optional[str] = Field(None, alias="weightUnit")

    # 包裹 ID
    package_id: Optional[int] = Field(None, alias="packageId")

    # 包裹类型
    package_type: Optional[str] = Field(None, alias="packageType")

    # 包裹名称
    package_name: Optional[str] = Field(None, alias="packageName")

    # 平台包裹类型
    platform_package_type: Optional[str] = Field(None, alias="platformPackageType")

    # 长度
    length: Optional[float]

    # 宽度
    width: Optional[float]

    # 高度
    height: Optional[float]

    # 尺寸单位
    dimension_unit: Optional[str] = Field(None, alias="dimensionUnit")

    model_config = ConfigDict(
        populate_by_name=True
    )


class FourSellerShippingServiceInfoVO(BaseModel):
    # 保险金额
    insurance_amount: Optional[float] = Field(None, alias="insuranceAmount")

    # 保险币种
    insurance_currency: Optional[str] = Field(None, alias="insuranceCurrency")

    # 物流服务
    shipping_service: Optional[str] = Field(None, alias="shippingService")

    # 承运商
    carrier: Optional[str]

    # 运费
    shipping_fee: Optional[float] = Field(None, alias="shippingFee")

    # 币种
    currency: Optional[str]

    # 预估送达天数
    estimated_delivery_days: Optional[int] = Field(None, alias="estimatedDeliveryDays")

    # 物流授权 ID
    logistics_auth_id: Optional[int] = Field(None, alias="logisticsAuthId")

    # 物流承运商 ID
    logistics_carrier_id: Optional[int] = Field(None, alias="logisticsCarrierId")

    # 物流承运商代码
    logistics_carrier_code: Optional[str] = Field(None, alias="logisticsCarrierCode")

    # 物流承运商名称
    logistics_carrier_name: Optional[str] = Field(None, alias="logisticsCarrierName")

    # 物流平台
    logistics_platform: Optional[str] = Field(None, alias="logisticsPlatform")

    # 物流服务 ID
    logistics_service_id: Optional[int] = Field(None, alias="logisticsServiceId")

    # 物流服务代码
    logistics_service_code: Optional[str] = Field(None, alias="logisticsServiceCode")

    # 物流服务类型
    logistics_service_type: Optional[str] = Field(None, alias="logisticsServiceType")

    # 物流服务名称
    logistics_service_name: Optional[str] = Field(None, alias="logisticsServiceName")

    # 平台物流服务 ID
    platform_shipping_service_id: Optional[int] = Field(None, alias="platformShippingServiceId")

    # 空白箱
    blank_box: Optional[int] = Field(None, alias="blankBox")

    # 阻止 AMZL
    block_amzl: Optional[int] = Field(None, alias="blockAmzl")

    # ERP 预估发货日期
    erp_estimated_shipping_date: Optional[str] = Field(None, alias="erpEstimatedShippingDate")

    # 配送确认类型
    delivery_confirmation_type: Optional[str] = Field(None, alias="deliveryConfirmationType")

    # 标签价格
    label_price: Optional[float] = Field(None, alias="labelPrice")

    # 预估运费
    estimated_shipping_price: Optional[float] = Field(None, alias="estimatedShippingPrice")

    model_config = ConfigDict(
        populate_by_name=True
    )


class FourSellerOrderItemInfoVO(BaseModel):
    # 订单商品 ID
    order_item_id: int = Field(..., alias="orderItemId")

    # 订单 ID
    order_id: int = Field(..., alias="orderId")

    # 卖家 SKU
    seller_sku: Optional[str] = Field(..., alias="sellerSku")

    # 商品标题
    title: str

    # 图片 URL
    img_url: Optional[str] = Field(None, alias="imgUrl")

    # 列表 URL
    listing_url: Optional[str] = Field(None, alias="listingUrl")

    # SKU ID
    sku_id: Optional[int] = Field(..., alias="skuId")

    # SKU
    sku: Optional[str] = Field(None)

    # 数量
    quantity: int

    # 变体属性
    variant_attr: Optional[str] = Field(None, alias="variantAttr")

    # 单价
    item_price: Optional[float] = Field(..., alias="itemPrice")

    # 币种
    currency: Optional[str] = Field(None)

    # 是否占用库存
    occupy: Optional[bool] = Field(None)

    # 商品是否未找到
    product_not_found: bool = Field(..., alias="productNotFound")

    # 地址是否有效
    address_valid: bool = Field(..., alias="addressValid")

    # 地址错误信息
    address_error_msg: Optional[str] = Field(None, alias="addressErrorMsg")

    # 来源 URL
    source_url: Optional[str] = Field(None, alias="sourceUrl")

    # 是否预售
    pre_sale: int = Field(..., alias="preSale")

    model_config = ConfigDict(
        populate_by_name=True
    )


class FourSellerOrderVO(BaseModel):
    # 订单 ID
    order_id: int = Field(..., alias="orderId")

    # 金额
    amount: Optional[float] = Field(None)

    # 币种
    currency: Optional[str] = Field(None)

    # 仓库 ID
    warehouse_id: int = Field(..., alias="warehouseId")

    # 仓库类型
    warehouse_type: str = Field(..., alias="warehouseType")

    # 仓库代码
    warehouse_code: Optional[str] = Field(None, alias="warehouseCode")

    # 平台仓名称
    platform_warehouse_name: Optional[str] = Field(None, alias="platformWarehouseName")

    # 平台物流方式
    platform_shipment_method: Optional[str] = Field(None, alias="platformShipmentMethod")

    # 支付状态
    paid_status: Optional[str] = Field(None, alias="paidStatus")

    # 订单状态
    order_status: str = Field(..., alias="orderStatus")

    # 平台订单状态
    platform_order_status: str = Field(..., alias="platformOrderStatus")

    # 取消原因
    cancel_reason: Optional[str] = Field(None, alias="cancelReason")

    # 平台
    platform: str

    # 平台订单号
    platform_order_id: str = Field(..., alias="platformOrderId")

    # 平台订单编号
    platform_order_no: str = Field(..., alias="platformOrderNo")

    # 店铺 ID
    shop_id: int = Field(..., alias="shopId")

    # 店铺名称
    shop_name: Optional[str] = Field(None, alias="shopName")

    # 包裹名称
    package_name: Optional[str] = Field(None, alias="packageName")

    # 买家备注
    buyer_memo: Optional[str] = Field(None, alias="buyerMemo")

    # 卖家备注
    seller_memo: Optional[str] = Field(None, alias="sellerMemo")

    # 内部备注
    internal_memo: Optional[str] = Field(None, alias="internalMemo")

    # 发货单号
    shipment_no: Optional[str] = Field(None, alias="shipmentNo")

    # 是否三方仓
    third_party: bool = Field(..., alias="thirdParty")

    # 是否打印标签
    print_label: bool = Field(..., alias="printLabel")

    # 是否打印装箱单
    print_packing_slip: bool = Field(..., alias="printPackingSlip")

    # 是否打印拣货单
    print_pick: bool = Field(..., alias="printPick")

    # 配送选项
    delivery_option_type: Optional[int] = Field(None, alias="deliveryOptionType")

    # 买标状态
    buy_label_process_status: str = Field(..., alias="buyLabelProcessStatus")

    # 错误信息
    error_message: Optional[str] = Field(None, alias="errorMessage")

    # 发货类型
    shipment_type: Optional[str] = Field(..., alias="shipmentType")

    # 用户设置发货类型
    user_setting_shipment_type: str = Field(..., alias="userSettingShipmentType")

    # 发货地址 ID
    ship_from_address_id: Optional[int] = Field(None, alias="shipFromAddressId")

    # 是否可拆分
    can_split: Optional[bool] = Field(..., alias="canSplit")

    # 追踪号
    tracking_no: Optional[str] = Field(None, alias="trackingNo")

    # 物流方式
    shipping_method: str = Field(..., alias="shippingMethod")

    # 标签列表
    tag_list: Optional[list[str]] = Field(None, alias="tagList")

    # 新标签列表
    new_tag_list: Optional[list[dict]] = Field(None, alias="newTagList")

    # 拆单编号
    split_no: int = Field(..., alias="splitNo")

    # 是否拆单
    is_split: int = Field(..., alias="isSplit")

    # ERP 是否标记发货
    is_erp_mark_ship: int = Field(..., alias="isErpMarkShip")

    # 标签地址
    shipping_label_url: Optional[str] = Field(None, alias="shippingLabelUrl")

    # 配送渠道类型
    fulfillment_channel_type: int = Field(..., alias="fulfillmentChannelType")

    # 标签打印时间
    print_label_time: Optional[str] = Field(None, alias="printLabelTime")

    # 拣货单打印时间
    print_pick_time: Optional[str] = Field(None, alias="printPickTime")

    # 装箱单打印时间
    print_packing_slip_time: Optional[str] = Field(None, alias="printPackingSlipTime")

    # 是否 17 物流挂号
    is_register17: int = Field(..., alias="isRegister17")

    # 第三方仓状态
    third_party_warehouse_status: Optional[str] = Field(None, alias="thirdPartyWarehouseStatus")

    # 订单类型
    order_type: int = Field(..., alias="orderType")

    # 被合并订单列表
    be_merged_order_list: Optional[list[dict]] = Field(None, alias="beMergedOrderList")

    # 买家申请取消
    is_buyer_requested_cancel: int = Field(..., alias="isBuyerRequestedCancel")

    # 是否作废
    is_voided: int = Field(..., alias="isVoided")

    # 地址信息
    order_address_vo: Optional[FourSellerOrderAddressVo] = Field(..., alias="orderAddressVo")

    # 时间信息
    time_info: FourSellerTimeInfoVO = Field(..., alias="timeInfo")

    # 包裹信息
    package_info: FourSellerPackageInfoVO = Field(..., alias="packageInfo")

    # 物流服务信息
    shipping_service_info: FourSellerShippingServiceInfoVO = Field(..., alias="shippingServiceInfo")

    # 商品列表
    order_item_info_list: list[FourSellerOrderItemInfoVO] = Field(..., alias="orderItemInfoList")

    # 是否样品订单
    is_sample_order: int = Field(..., alias="isSampleOrder")

    # 是否预售
    pre_sale: Optional[int] = Field(..., alias="preSale")

    model_config = ConfigDict(
        populate_by_name=True
    )
