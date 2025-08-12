from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class KoganOrderQuery(BaseModel):
    # 订单状态  只能传入  ReleasedForShipment
    status: str = None
    # 数量  默认值不给为无限制
    limit: Optional[int] = None
    # 开始日期
    start_date_utc: Optional[str] = Field(default=None, alias="startDateUTC")
    # 结束日期
    end_date_utc: Optional[str] = Field(default=None, alias="endDateUTC")

    model_config = ConfigDict(
        # 允许使用别名
        populate_by_name=True
    )

