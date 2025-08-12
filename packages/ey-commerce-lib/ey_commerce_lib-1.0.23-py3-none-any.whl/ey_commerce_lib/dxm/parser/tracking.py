from lxml import html

from ey_commerce_lib.dxm.schemas.tracking import TrackingPageListItem
from ey_commerce_lib.utils.list_util import get_str_list_first_not_blank_or_none


def parse_tracking_page(html_content: str):
    tree = html.fromstring(html_content)
    # 物流追踪节点列表
    tracking_element_list = tree.xpath('//tbody[@id="dhSysMsg"]/tr[@class="content"]')
    tracking_list = []
    for tracking_element in tracking_element_list:
        # 获取包裹号
        package_number = tracking_element.xpath('@data-tracknum')[0].strip()
        # 获取订单id
        order_id = tracking_element.xpath('@data-orderid')[0].strip()
        # 获取收件人姓名
        receiver_name = tracking_element.xpath('./td[3]/text()')[0].strip()
        # 获取国家
        country = get_str_list_first_not_blank_or_none(tracking_element.xpath('./td[3]/span/text()'))
        # 获取物流方式
        logistics_method = tracking_element.xpath('./td[4]/text()')[0].strip()
        # 物流状态
        logistics_status = tracking_element.xpath('./td[4]/span/@title')[0].replace('「', '').replace('」', '')
        # 物流单号
        logistics_number = tracking_element.xpath('./td[4]//span[@class="limingcentUrlpic"]/text()')[0].strip()
        # carrierCode
        carrier_code = get_str_list_first_not_blank_or_none(tracking_element.xpath('./td[5]/a/@data-carriercode'))
        # 最新消息
        latest_message = get_str_list_first_not_blank_or_none(tracking_element.xpath('./td[5]/text()'))
        # 运输信息
        transport_info = tracking_element.xpath('./td[6]/text()')[0].strip()
        # 平台和店铺
        platform, shop = tracking_element.xpath('./td[7]')[0].text_content().split('：')
        time_list = []
        # 获取时间
        for time in tracking_element.xpath('./td[8]')[0].text_content().strip().split('\n'):
            time_list.append(time.strip())
        platform = platform.strip()
        shop = shop.strip()
        tracking_list.append(TrackingPageListItem(
            package_number=package_number,
            order_id=order_id,
            receiver_name=receiver_name,
            country=country,
            logistics_method=logistics_method,
            logistics_status=logistics_status,
            logistics_number=logistics_number,
            latest_message=latest_message,
            transport_info=transport_info,
            platform=platform,
            shop=shop,
            time_list=time_list,
            carrier_code=carrier_code
        ))
    return tracking_list
