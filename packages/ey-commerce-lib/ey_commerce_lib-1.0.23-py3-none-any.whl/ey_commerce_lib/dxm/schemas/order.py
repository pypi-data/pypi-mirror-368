from typing import TypedDict, Optional
from urllib.parse import urlencode

from pydantic import BaseModel, ConfigDict

from ey_commerce_lib.utils.str import to_camel


class DxmOrderSearchForm(BaseModel):
    """
    /package/advancedSearch.htm
    店小秘订单搜索接口参数约束
    """
    # 搜索类型(orderId订单号, packageNum包裹号)
    search_types: str = 'orderId'
    # 搜索内容
    contents: str = ''
    order_adv_search_type: str = '1'
    # 订单状态
    state: str = ''
    is_voided: str = '-1'
    is_removed: str = '-1'
    commit_platforms: str = ''
    # 是否为海外仓-1代表全部,1是0否
    is_oversea: str = '-1'
    # 店铺id
    shop_id: str = '-1'
    # 平台
    platform: str = ''
    # 历史订单(空字符串就是代表没有, all 代表历史记录)
    history: str = ''
    # 排序方式
    order_field: str = 'order_create_time'
    is_desc: str = '1'
    time_out: str = '0'
    warehouse_code: str = ''
    # 订单标记绿色
    is_green: str = '0'
    # 订单标记黄色
    is_yellow: str = '0'
    # 订单标记橙色
    is_orange: str = '0'
    # 订单标记红色
    is_red: str = '0'
    # 订单标记紫色
    is_violet: str = '0'
    # 订单标记蓝色
    is_blue: str = '0'
    # 订单标记青色
    corn_flower_blue: str = '0'
    # 订单标记粉色
    pink: str = '0'
    teal: str = '0'
    turquoise: str = '0'
    unmarked: str = '0'
    forbidden_status: str = '-1'
    forbidden_reason: str = '0'
    picking_instructions: str = ''
    # 订单金额起始
    price_start: str = ''
    # 订单金额结束
    price_end: str = ''
    # 下单时间
    order_create_start: str = ''
    order_create_end: str = ''
    # 付款时间
    order_pay_start: str = ''
    order_pay_end: str = ''
    # 发货时间
    shipped_start: str = ''
    shipped_end: str = ''
    # 退款时间
    refunded_start: str = ''
    refunded_end: str = ''
    # 面单打印时间
    md_sign_start: str = ''
    md_sign_end: str = ''
    # 拣货单打印时间
    jh_sign_start: str = ''
    jh_sign_end: str = ''
    # 剩余发货
    time_out_query: str = '-1'
    # 包裹类型
    product_status: str = ''
    # 订单商品数量
    product_count_start: str = ''
    product_count_end: str = ''
    # 发货仓库, 多个仓库用逗号隔开
    storage_ids: str = ''
    storage_id: str = '0'
    auth_id: str = '-1'
    days: str = '-1'
    # 国家区域
    country: str = ''
    # 拣货单打印（-1全部,1已打拣货单,2未打拣货单）
    is_print_jh: str = '-1'
    # 优先分配库存(-1全部,1是,2否)
    sign_prior_ship: str = '-1'
    # 面单打印(-1全部,1是,2否)
    is_print_md: str = '-1'
    # 提交单号(uncommit)
    commit_platform: str = ''
    # 买家留言(-1全部,1有留言,0没有留言)
    is_has_order_message: str = '-1'
    # 买家备注(-1全部,1有备注,0没有备注)
    is_has_order_comment: str = '-1'
    # 客服备注(-1全部,1有备注,0没有备注)
    is_has_service_comment: str = '-1'
    # 拣货备注(-1全部,1有备注,0没有备注)
    is_has_pick_comment: str = '-1'

    # 合并订单(1代表勾选)
    is_merge: str = ''
    # 拆分订单(1代表勾选)
    is_split: str = ''
    # 重发包裹(1代表勾选)
    is_re_ship: str = ''
    # 有退款
    is_refund: str = ''
    # 禁止处理(1代表勾选)
    sign_ban_ship: str = ''
    # 黑名单
    black_list: str = ''
    # 平台标识
    global_collection: str = '-1'
    # 分页
    page_no: int = 1
    page_size: int = 30

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True  # 对应旧版的 allow_population_by_field_name
    )


class DxmJsonResponse(TypedDict):
    """
    店小秘一般json返回响应
    """
    code: int
    msg: str


class DxmProcessMsg(TypedDict):
    code: int
    msg: str
    data: Optional[dict]
    num: int
    totalNum: int
    createDate: int


class DxmCheckProcessResponse(TypedDict):
    """
    店小秘检测进度返回参数类型
    """
    processMsg: DxmProcessMsg


class DxmOrderRuleCond(BaseModel):
    """
    店小秘订单规则参数项基类
    """
    # 条件值
    cond_val: str
    # 条件id
    cond_id: str
    # 条件名称
    cond_name: str
    # 条件单位
    cond_unit: str = ''
    # 条件类型
    cond_type: str = '1'


class DxmOrderRule(BaseModel):
    """
    店小秘订单规则参数基类
    """
    gift_doubly: str
    # 规则id
    id: str
    # 规则类型(1:审单规则，2:物流规则)
    type: str
    # 规则名称
    rule_name: str
    # 客服备注
    kfbz: str = ''
    # 拣货备足
    jhbz: str = ''
    # 拣货颜色
    jh_color: str = ''
    # 自定义备注
    custom_mark: str = ''
    # 附加规则(on勾选, ''未勾选)
    other_action: str = ''
    has_other_action: str = ''
    # 条件列表
    dxm_cond_list: list[DxmOrderRuleCond]

    def to_update_rule_data_before(self):
        data = list()
        data.append(('id', self.id))
        data.append(('type', self.type))
        data.append(('giftDoubly', self.gift_doubly))
        data.append(('ruleName', self.rule_name))
        # 装填规则内容
        for cond in self.dxm_cond_list:
            data.append(('condVal', cond.cond_val))
            data.append(('condId', cond.cond_id))
            data.append(('condName', cond.cond_name))
            data.append(('condUnit', cond.cond_unit))
            data.append(('condType', cond.cond_type))
        # 装填conditionId
        for cond in self.dxm_cond_list:
            data.append(('conditionId', cond.cond_id))
        return data

    def to_update_rule_data_after(self):
        data = list()
        data.append(('otherAction', self.other_action))
        data.append(('kfbz', self.kfbz))
        data.append(('jhbz', self.jhbz))
        data.append(('hasOtherAction', self.has_other_action))
        data.append(('customMark', self.custom_mark))
        data.append(('jhColor', self.jh_color))
        return data

    def to_update_rule_data(self):
        """
        转换成更新物流规则的参数数据,由子类实现
        :return:
        """
        pass


class DxmOrderReviewRule(DxmOrderRule):
    """
    店小秘审单规则参数
    """
    # 流程规则(paid: 待审核, approved: 待处理)
    action: str = 'paid'

    def to_update_rule_data(self):
        """
        转换成更新物流规则的参数数据
        :return:
        """
        data = super().to_update_rule_data_before()
        # 装填其他参数
        data.append(('action', self.action))
        data.extend(super().to_update_rule_data_after())
        return urlencode(data, encoding="utf-8")


class DxmOrderLogisticsRule(DxmOrderRule):
    """
    店小秘订单物流规则参数
    """
    ware_id: str
    # 物流方式id(物流规则使用, 必须要是distribute_type为0)
    auth_id: str
    # 分配方式(0:仅指定一个物流,1:指定多个物流)
    distribute_type: str
    # 物流方式ids(物流规则使用, 多个用逗号隔开, 必须要是distribute_type为1)
    auth_ids: str

    def to_update_rule_data(self):
        data = super().to_update_rule_data_before()
        # 装填其他参数
        data.append(('wareId', self.ware_id))
        data.append(('distributeType', self.distribute_type))
        data.append(('authId', self.auth_id))
        data.append(('authIds', self.auth_ids))
        data.extend(super().to_update_rule_data_after())
        return urlencode(data, encoding="utf-8")
