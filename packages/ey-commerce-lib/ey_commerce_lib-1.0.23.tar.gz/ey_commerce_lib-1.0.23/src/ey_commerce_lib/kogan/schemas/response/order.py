from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AddressModel(BaseModel):
    address_line1: str = Field(..., alias="AddressLine1")  # 地址行1
    address_line2: Optional[str] = Field(None, alias="AddressLine2")  # 地址行2
    city: str = Field(..., alias="City")  # 城市
    company_name: Optional[str] = Field(None, alias="CompanyName")  # 公司名称
    country: str = Field(..., alias="Country")  # 国家代码
    daytime_phone: Optional[str] = Field(None, alias="DaytimePhone")  # 白天联系电话
    email_address: Optional[str] = Field(None, alias="EmailAddress")  # 邮箱地址
    evening_phone: Optional[str] = Field(None, alias="EveningPhone")  # 夜间联系电话
    first_name: str = Field(..., alias="FirstName")  # 名
    last_name: str = Field(..., alias="LastName")  # 姓
    name_suffix: Optional[str] = Field(None, alias="NameSuffix")  # 姓名后缀
    postal_code: str = Field(..., alias="PostalCode")  # 邮政编码
    state_or_province: Optional[str] = Field(None, alias="StateOrProvince")  # 州或省
    location_id: Optional[str] = Field(None, alias="LocationId")  # 位置 ID
    location_id_source: Optional[str] = Field(None, alias="LocationIdSource")  # 位置 ID 来源


class ItemModel(BaseModel):
    id: str = Field(..., alias="ID")  # 商品 ID
    quantity: int = Field(..., alias="Quantity")  # 商品数量
    seller_sku: str = Field(..., alias="SellerSku")  # 卖家 SKU
    product_title: str = Field(..., alias="ProductTitle")  # 商品标题
    unit_price: float = Field(..., alias="UnitPrice")  # 单价


class OrderModel(BaseModel):
    id: str = Field(..., alias="ID")  # 订单 ID
    currency: str = Field(..., alias="Currency")  # 货币代码
    items: list[ItemModel] = Field(..., alias="Items")  # 商品列表
    order_date_utc: datetime = Field(..., alias="OrderDateUtc")  # 下单时间
    order_status: str = Field(..., alias="OrderStatus")  # 订单状态
    requested_shipping_method: str = Field(..., alias="RequestedShippingMethod")  # 请求的配送方式
    total_gift_option_price: float = Field(..., alias="TotalGiftOptionPrice")  # 礼品选项总价
    total_gift_option_tax_price: float = Field(..., alias="TotalGiftOptionTaxPrice")  # 礼品选项税费总价
    total_price: float = Field(..., alias="TotalPrice")  # 订单总价
    total_shipping_price: float = Field(..., alias="TotalShippingPrice")  # 运费总价
    total_shipping_tax_price: float = Field(..., alias="TotalShippingTaxPrice")  # 运费税费总价
    total_tax_price: float = Field(..., alias="TotalTaxPrice")  # 总税费
    vat_inclusive: bool = Field(..., alias="VatInclusive")  # 是否含税
    buyer_address: AddressModel = Field(..., alias="BuyerAddress")  # 买家地址
    deliver_by_date_utc: datetime = Field(..., alias="DeliverByDateUtc")  # 要求送达日期
    other_fees: float = Field(..., alias="OtherFees")  # 其他费用
    payment_method: Optional[str] = Field(None, alias="PaymentMethod")  # 支付方式
    payment_transaction_id: Optional[str] = Field(None, alias="PaymentTransactionID")  # 支付交易号
    private_notes: Optional[str] = Field(None, alias="PrivateNotes")  # 私有备注
    shipping_address: AddressModel = Field(..., alias="ShippingAddress")  # 收货地址
    shipping_label_url: Optional[str] = Field(None, alias="ShippingLabelURL")  # 运单 URL
    special_instructions: Optional[str] = Field(None, alias="SpecialInstructions")  # 特殊指示
    total_order_discount: float = Field(..., alias="TotalOrderDiscount")  # 订单折扣总额
    total_shipping_discount: float = Field(..., alias="TotalShippingDiscount")  # 运费折扣总额
    order_label: str = Field(..., alias="OrderLabel")  # 订单标签
    dispatched_items: Optional[list[str]] = Field(None, alias="DispatchedItems")  # 已发货商品 ID 列表
    cancelled_items: Optional[list[str]] = Field(None, alias="CancelledItems")  # 已取消商品 ID 列表
    customer_date_of_birth: Optional[str] = Field(None, alias="CustomerDateOfBirth")  # 客户生日
    web_store: Optional[str] = Field(None, alias="WebStore")  # 网店标识
    is_premium_subscription: Optional[bool] = Field(None, alias="IsPremiumSubscription")  # 是否高级会员订单


class OrderResponseModel(BaseModel):
    status: str = Field(..., alias="status")  # 响应状态
    error: Optional[str] = Field(None, alias="error")  # 错误信息
    pending_url: Optional[str] = Field(None, alias="pending_url")  # 挂起处理 URL
    body: list[OrderModel] = Field(..., alias="body")  # 订单数据列表
