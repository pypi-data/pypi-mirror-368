from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ExportPackageOrderModel(BaseModel):
    template_id: str = Field(alias="templateId", description="模板ID")
    package_ids: str = Field("", alias="packageIds", description="packageId使用,号连接")
    export_keys: str = Field(alias="exportKeys", description="导出字段, 需要使用urllib.parse.quote编码")
    order_field: str = Field('order_create_time', alias="orderField", description="固定值不用管")
    state: str = Field("", alias="state", description="订单状态")
    start_time: str = Field("", alias="startTime", description="开始时间")
    end_time: str = Field("", alias="endTime", description="结束时间")
    time_type: str = Field("", alias="timeType", description="时间类型 2(发货时间) 0(付款时间) 1(下单时间)")
    export_style: str = Field("1", alias="exportStyle", description="按包裹导出(1) 按订单导出(0) 按产品导出(2)")
    history: str = Field("", alias="history", description="120天订单('') 历史订单('all')")
    is_voided: str = Field("-1", alias="isVoided")
    rule_id: str = Field("-1", alias="ruleId")
    sysrule: str = Field("", alias="sysrule")
    request_location: str = Field('0', alias="requestLocation", description="页面上pageTag的值(一般不用管0)")
    is_search: str = Field('1', alias="isSearch")

    model_config = ConfigDict(populate_by_name=True)
