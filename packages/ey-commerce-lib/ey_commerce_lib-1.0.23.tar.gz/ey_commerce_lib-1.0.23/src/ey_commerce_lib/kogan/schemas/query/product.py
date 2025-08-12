from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class KoganProductQuery(BaseModel):
    enabled: Optional[bool] = Field(
        None,
        alias="enabled",
        description="启用状态过滤（True/true/1 表示启用，False/false/0 表示禁用）"
    )
    category: Optional[str] = Field(
        None,
        alias="category",
        description="按 Kogan.com 类别名称筛选（不区分大小写，可多选）"
    )
    brand: Optional[str] = Field(
        None,
        alias="brand",
        description="按品牌筛选（不区分大小写，可多选，标题中逗号需要转义，例如 '\\,'）"
    )
    created: Optional[str] = Field(
        None,
        alias="created",
        description="创建时间"
    )
    ebay_category: Optional[int] = Field(
        None,
        alias="ebay_category",
        description="按 eBay 类别 ID 筛选"
    )
    sku: Optional[str] = Field(
        None,
        alias="sku",
        description="按 SKU 精确匹配（支持多选）"
    )
    search: Optional[str] = Field(
        None,
        alias="search",
        description="搜索商品标题"
    )
    ordering: Optional[str] = Field(
        None,
        alias="ordering",
        description="结果排序字段"
    )
    cursor: Optional[str] = Field(
        None,
        alias="cursor",
        description="用于分页的游标（续接 'next' URL 的分页查询）"
    )
    size: Optional[int] = Field(
        None,
        alias="size",
        description="每页返回结果数量"
    )
    created_after: Optional[str] = Field(
        None,
        alias="created_after",
        description="筛选创建日期 >= 指定日期（AEST/AEDT 格式 YYYY-MM-DD）"
    )
    created_before: Optional[str] = Field(
        None,
        alias="created_before",
        description="筛选创建日期 <= 指定日期（AEST/AEDT 格式 YYYY-MM-DD）"
    )
    detail: Optional[bool] = Field(
        None,
        alias="detail",
        description="是否启用响应中所有字段（True/true/1 表示启用）"
    )

    model_config = ConfigDict(
        # 支持别名
        populate_by_name=True
    )
