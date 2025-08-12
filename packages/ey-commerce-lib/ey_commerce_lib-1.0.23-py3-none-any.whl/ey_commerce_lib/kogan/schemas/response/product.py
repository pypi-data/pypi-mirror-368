from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class OfferDetail(BaseModel):
    # 价格
    price: str = Field(..., alias="price")
    # Kogan First 价格
    kogan_first_price: Optional[str] = Field(None, alias="kogan_first_price")
    # 是否免税
    tax_exempt: bool = Field(..., alias="tax_exempt")
    # 运费
    shipping: str = Field(..., alias="shipping")
    # 处理天数
    handling_days: int = Field(..., alias="handling_days")
    # 建议零售价
    rrp: Optional[str] = Field(None, alias="rrp")

    model_config = ConfigDict(
        populate_by_name=True
    )


class StoreUrl(BaseModel):
    # 商店链接
    url: str = Field(..., alias="url")
    # 商店名称
    store_name: str = Field(..., alias="store_name")
    # 组织名称
    organisation: str = Field(..., alias="organisation")

    model_config = ConfigDict(
        populate_by_name=True
    )


class Product(BaseModel):
    # 产品标题
    product_title: str = Field(..., alias="product_title")
    # 产品SKU
    product_sku: str = Field(..., alias="product_sku")
    # 产品副标题
    product_subtitle: str = Field(..., alias="product_subtitle")
    # 产品 GTIN
    product_gtin: str = Field(..., alias="product_gtin")
    # 图片链接列表
    images: list[str] = Field(..., alias="images")
    # 品牌
    brand: Optional[str] = Field(None, alias="brand")
    # 类别
    category: str = Field(..., alias="category")
    # 类别标识
    category_slug: str = Field(..., alias="category_slug")
    # 报价数据
    offer_data: dict[str, OfferDetail] = Field(..., alias="offer_data")
    # 库存数量
    stock: int = Field(..., alias="stock")
    # 是否启用
    enabled: bool = Field(..., alias="enabled")
    # 创建时间
    created: str = Field(..., alias="created")
    # 商店地址列表
    store_urls: list[StoreUrl] = Field(..., alias="store_urls")
    # 标签
    tags: list[str] = Field(..., alias="tags")

    model_config = ConfigDict(
        populate_by_name=True
    )


class Body(BaseModel):
    # 下一页链接
    next: Optional[str] = Field(None, alias="next")
    # 产品列表
    results: list[Product] = Field(..., alias="results")

    model_config = ConfigDict(
        populate_by_name=True
    )


class ProductResponse(BaseModel):
    # 状态
    status: str = Field(..., alias="status")
    # 待处理URL
    pending_url: Optional[str] = Field(None, alias="pending_url")
    # 错误信息
    error: Optional[str] = Field(None, alias="error")
    # 响应主体
    body: Body = Field(..., alias="body")

    model_config = ConfigDict(
        populate_by_name=True
    )

