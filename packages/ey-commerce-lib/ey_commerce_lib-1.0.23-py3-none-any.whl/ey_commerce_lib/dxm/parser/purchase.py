from lxml import html

from ey_commerce_lib.utils.list_util import get_str_list_first_not_blank_or_none


def list_1688_purchase_order_number(html_str: str) -> list[str]:
    """
    根据1688采购页面html获取1688采购页面采购单号列表
    :param html_str:
    :return:
    """
    tree = html.fromstring(html_str)
    good_element_list: list[html.HtmlElement] = tree.xpath('//tr[contains(@class, "goodsId")]')
    purchase_order_number_list = list()
    for good_element in good_element_list:
        purchase_order_number_list.append(get_str_list_first_not_blank_or_none(
            good_element.xpath('.//span[@class="limingcentUrlpic"]/text()')))
    return purchase_order_number_list


def list_wait_pay_page_purchase_order_number(html_str: str) -> list[str]:
    """
    根据采购wait_pay_pag这个请求返回html代码获取采购单号列表
    :param html_str:
    :return:
    """
    tree = html.fromstring(html_str)
    good_element_list: list[html.HtmlElement] = tree.xpath('//tr[contains(@class, "goodsId")]')
    purchase_order_number_list = list()
    for good_element in good_element_list:
        purchase_order_number = get_str_list_first_not_blank_or_none(
            good_element.xpath('.//a[@class="limingcentUrlpic"]/text()'))
        purchase_order_number_list.append(purchase_order_number)
    return purchase_order_number_list


def list_purchasing_all(html_str: str) -> list[dict]:
    """
       根据采购全部页面html，获取采购页面详细数据列表
       :param html_str:
       :return:
       """
    tree = html.fromstring(html_str)
    good_element_list: list[html.HtmlElement] = tree.xpath('//tr[contains(@class, "goodsId")]')
    purchase_result = list()
    for good_element in good_element_list:
        purchase_id = get_str_list_first_not_blank_or_none(good_element.xpath('@id'))
        purchase_order_number = get_str_list_first_not_blank_or_none(
            good_element.xpath('.//a[@class="limingcentUrlpic"]/text()'))
        ghs_id = get_str_list_first_not_blank_or_none(
            good_element.xpath('.//span[contains(@class, "ghsHoverPrompt")]/@data-ghsid'))
        ghs_name = get_str_list_first_not_blank_or_none(
            good_element.xpath('.//span[contains(@class, "ghsHoverPrompt")]/span/text()'))
        warehouse_name, purchase_info = good_element.xpath('.//td[4]/span/text()')[0].strip().split('|')
        agent_name = purchase_info.split('：')[1]
        # 获取兄弟元素
        content_element = good_element.getnext()
        # 获取商品信息
        img = get_str_list_first_not_blank_or_none(content_element.xpath('.//img/@data-original'))
        content_number_info = content_element.xpath('./td[2]/text()')
        product_zl_number = None
        purchase_number = None
        for content_number in content_number_info:
            content_number = content_number.strip()
            if content_number.split('：')[0] == '商品种类':
                product_zl_number = content_number.split('：')[1].strip()
            elif content_number.split('：')[0] == '采购数量':
                purchase_number = content_number.split('：')[1].strip()
        # 解析出货款
        total_amount = get_str_list_first_not_blank_or_none(content_element.xpath('./td[3]//input/@data-totalamount'))
        # 运费
        shipping_amount = get_str_list_first_not_blank_or_none(content_element.xpath('./td[3]//input/@value'))
        source = None
        source_list = content_element.xpath('./td[4]/span[1]')
        if len(source_list) == 0:
            # 说明不是淘供销
            source_list = content_element.xpath('./td[4]/div[1]')

        if len(source_list) > 0:
            try:
                source = source_list[0].text_content()
                source = source.strip()
                platform, source_str = source.split("：")
                source = platform.strip() + ":" + source_str.strip()
            except:
                source = None
        # 获取物流信息
        track_element_list = content_element.xpath('./td[4]//a[@class="getLogisticsMsgBox"]')
        track_list = list()
        for track_element in track_element_list:
            tracking_id = get_str_list_first_not_blank_or_none(track_element.xpath("@trackingid"))
            tracking_number = get_str_list_first_not_blank_or_none(track_element.xpath("@data-trackingnumber"))
            tracking_code = get_str_list_first_not_blank_or_none(track_element.xpath("@data-trackingcode"))
            track_status = get_str_list_first_not_blank_or_none(
                track_element.xpath('./span[contains(@class, "iconfont")]/@data-original-title'))
            track_list.append({
                "tracking_id": tracking_id,
                "tracking_number": tracking_number,
                "tracking_code": tracking_code,
                "track_status": track_status
            })

        # 状态
        status = get_str_list_first_not_blank_or_none(content_element.xpath('./td[6]/div[@class="mBottom3"]/text()'))
        purchase_result.append({
            "purchase_id": purchase_id,
            "purchase_order_number": purchase_order_number,
            "ghs_id": ghs_id,
            "ghs_name": ghs_name,
            "agent_name": agent_name,
            "img": img,
            "product_zl_number": product_zl_number,
            "purchase_number": purchase_number,
            "total_amount": total_amount,
            "shipping_amount": shipping_amount,
            "source": source,
            "status": status,
            'track_list': track_list
        })

    return purchase_result
