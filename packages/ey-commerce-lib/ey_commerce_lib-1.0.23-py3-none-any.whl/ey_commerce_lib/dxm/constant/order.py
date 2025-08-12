# 待审核搜索配置
from enum import StrEnum

from ey_commerce_lib.dxm.schemas.order import DxmOrderSearchForm

# 待审核搜索基础配置
ORDER_SEARCH_APPROVAL_BASE_FORM = DxmOrderSearchForm(**{
    'state': 'paid',
    'is_voided': '0',
    'is_removed': '0',
    'order_field': 'order_pay_time',
    'is_desc': '0'
})
# 待处理搜索基础配置
ORDER_SEARCH_PENDING_PROCESSING_BASE_FORM = DxmOrderSearchForm(**{
    'state': 'approved',
    'is_voided': '0',
    'is_removed': '0',
    'order_field': 'order_pay_time',
    'is_desc': '0',
})
# 自营仓库搜索配置（非海外仓）
ORDER_SEARCH_SELF_WAREHOUSE_BASE_FORM = DxmOrderSearchForm(**{
    'search_types': 'packageNum',
    'state': 'processed',
    'is_voided': '0',
    'is_removed': '0',
    'is_oversea': '0',
    'order_field': 'order_pay_time',
    'is_desc': '0',
})
# 海外仓库搜索配置（海外仓）
ORDER_SEARCH_OVERSEA_WAREHOUSE_BASE_FORM = DxmOrderSearchForm(**{
    'state': 'processed',
    'is_voided': '0',
    'is_removed': '0',
    'is_oversea': '1',
    'order_field': 'order_pay_time',
    'is_desc': '0',
})
# 有货搜索配置
ORDER_SEARCH_HAVE_GOODS_BASE_FORM = DxmOrderSearchForm(**{
    'state': 'allocated_has',
    'is_voided': '0',
    'is_removed': '0',
    'order_field': 'order_pay_time',
    'is_desc': '0',
})
# 缺货搜索配置
ORDER_SEARCH_OUT_OF_STOCK_BASE_FORM = DxmOrderSearchForm(**{
    'state': 'allocated_out',
    'is_voided': '0',
    'is_removed': '0',
    'order_field': 'order_pay_time',
    'is_desc': '0',
})
# 发货失败搜索配置
ORDER_SEARCH_DELIVERY_FAILURE_BASE_FORM = DxmOrderSearchForm(**{
    'state': 'fail',
    'is_voided': '0',
    'is_removed': '0',
    'order_field': 'order_pay_time',
    'is_desc': '0'
})
# 发货成功搜索配置
ORDER_SEARCH_DELIVERY_SUCCESS_BASE_FORM = DxmOrderSearchForm(**{
    'state': 'shipped',
    'is_voided': '0',
    'is_removed': '0',
    'commit_platforms': 'success',
    'order_field': 'shipped_time',
    'is_desc': '0'}
)


class DxmOrderRuleType(StrEnum):
    # 审单规则
    ORDER_APPROVAL = '1'
    # 物流规则
    LOGISTICS = '2'
