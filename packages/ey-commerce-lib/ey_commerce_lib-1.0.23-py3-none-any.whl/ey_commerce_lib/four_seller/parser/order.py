import math

from ey_commerce_lib.four_seller.schemas.vo.order import FourSellerOrderVO
from ey_commerce_lib.model import Page


def parse_order(data: dict) -> Page[FourSellerOrderVO]:
    # 计算total_page
    page_size = data.get('pageSize')
    total = data.get('total')
    page_number = data.get('pageCurrent')
    total_page = math.ceil(total / page_size) if total > 0 else 0
    return Page(
        records=[FourSellerOrderVO(**record) for record in data.get('records')],
        total=total,
        page_size=page_size,
        page_number=page_number,
        total_page=total_page
    )
