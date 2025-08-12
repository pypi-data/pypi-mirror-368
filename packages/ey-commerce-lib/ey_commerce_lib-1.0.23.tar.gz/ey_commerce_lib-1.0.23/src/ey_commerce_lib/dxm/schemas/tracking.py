from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TrackingPageListQuery(BaseModel):
    page_no: str = Field('1', alias='pageNo', description='页码')
    state_type: str = Field('all', alias='stateType', description='状态类型，默认 all(全部)')
    platform: str = Field('', alias='platform', description='平台渠道')
    shop_id: str = Field('-1', alias="shopId", description='店铺 ID')
    country: str = Field('', alias="country", description="国家")
    auth_id: str = Field('-1', alias="authId", description="物流方式")
    ship_start_time: str = Field('', alias="shipStartTime", description="发货开始时间")
    ship_end_time: str = Field('', alias="shipEndTime", description="发货结束时间")
    track_start_time: str = Field('-1', alias='trackStartTime', description='运输天数')
    track_end_time: str = Field('-1', alias='trackEndTime', description='运输天数')
    is_comm: str = Field('', alias='isComm', description='备注')
    order_field: str = Field('shipped_time', alias='orderField', description='排序方式')
    is_desc: str = Field('1', alias='isDesc', description='排序方式')
    search_type: str = Field('orderId', alias='searchType', description='搜索类型 orderId(订单id)')
    search_value: str = Field('', alias="searchValue", description="搜索关键字")
    is_del: str = Field('0', alias="isDel", description="是否删除，0 否 1 是")
    history: str = Field('', alias="history", description="历史记录标志")
    is_stop: str = Field('0', alias='isStop', description='是否暂停，0 正常追踪 1 暂停追踪')
    no_update_days: str = Field('0', alias="noUpdateDays", description="异常类型 无更新天数")

    model_config = ConfigDict(populate_by_name=True)


class TrackingPageListItem(BaseModel):
    package_number: str = Field(..., alias='packageNumber', description='包裹号')
    order_id: str = Field(..., alias='orderId', description='订单号')
    receiver_name: str = Field(..., alias='receiverName', description='收件人姓名')
    country: Optional[str] = Field(..., alias='country', description='国家')
    logistics_method: str = Field(..., alias='logisticsMethod', description='物流方式')
    logistics_status: str = Field(..., alias='logisticsStatus', description='物流状态')
    logistics_number: str = Field(..., alias='logisticsNumber', description='物流单号')
    carrier_code: Optional[str] = Field(..., alias='carrierCode', description='物流公司编码')
    latest_message: Optional[str] = Field(..., alias='latestMessage', description='最新物流信息')
    transport_info: str = Field(..., alias='transportInfo', description='运输信息')
    platform: str = Field(..., alias='platform', description='平台渠道')
    shop: str = Field(..., alias='shop', description='店铺')
    time_list: list[str] = Field([], alias='timeList', description='时间列表')

    model_config = ConfigDict(populate_by_name=True)
