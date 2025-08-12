import re

from lxml import html

from ey_commerce_lib.dxm.schemas.order import DxmOrderRule, DxmOrderRuleCond, DxmOrderReviewRule, DxmOrderLogisticsRule
from ey_commerce_lib.utils.dxm import get_remaining_ship_time, get_data_custom_mark_to_str
from ey_commerce_lib.utils.list_util import get_str_list_first_not_blank_or_none


def get_single_order_item_list(order_element: html.HtmlElement):
    """
    获取单个订单项的订单列表
    :return:
    """
    sku_list = list()
    sku_element_list = order_element.xpath('.//tr[contains(@class, "pairProInfo")]')
    for sku_element in sku_element_list:
        sku = sku_element.xpath('.//a[contains(@class, "pairProInfoSku")]/text()')[0]
        img = get_str_list_first_not_blank_or_none(sku_element.xpath('.//img/@data-original'))
        quantity = sku_element.xpath('.//span[@class="limingcentUrlpicson"]/following-sibling::span[1]/text()')[0]
        # 价格
        currency, price = \
            sku_element.xpath('.//span[@class="limingcentUrlpicson"]/parent::*/following-sibling::p[1]/text()')[
                0].split(' ')
        # 变种
        variants = sku_element.xpath(
            './/p[@class="pairProInfoName orderPairNameIsOverlength"]/span[@class="isOverLengThHide"]/text()')
        variant_list = list()
        # 原来的变种
        origin_variants = []
        for variant in variants:
            if len(variant.split('：')) == 2:
                variant_list.append({
                    'name': variant.split('：')[0].strip(),
                    'value': variant.split('：')[1].strip()
                })
            else:
                origin_variants.append(variant)
        # 获取来源数据
        source_presentation_element_list = (sku_element.
                                            xpath('.//ul[@id="dropSourceUrl"]/li[@role="presentation"]/a/text()'))
        source_presentation_element_list = [source_presentation_element.strip().split('：')[1]
                                            for source_presentation_element in source_presentation_element_list]
        try:
            price = float(price.replace(',', ''))
        except Exception:
            price = None
        sku_list.append({
            'sku': sku,
            'quantity': int(quantity),
            'price': price,
            'currency': currency,
            'img': img,
            'variants': variant_list,
            'origin_variants': origin_variants,
            'source_list': source_presentation_element_list
        })
    # 订单金额
    currency, price = order_element.xpath('./td[2]/text()')[0].strip().split(' ')
    recipient = None
    country = None
    if order_element.xpath('.//td[3]/span/text()')[0] != '「」':
        # 收件人
        recipient = order_element.xpath('.//td[3]/span/text()')[0]
        country = order_element.xpath('.//td[3]/span/text()')[1].replace('「', '').replace('」', '')
    # 订单号
    order_id = order_element.xpath('.//td[4]//a[contains(@class, "limingcentUrlpic")]/text()')[0]
    # 备注
    remark = get_str_list_first_not_blank_or_none(
        order_element.xpath('.//td[4]//span[contains(@class, "buyerNotes")]/@data-content'))
    # 下单时间等信息
    time_element_list = order_element.xpath('.//td[5]/div')
    time_dict = dict()
    for time_element in time_element_list:
        # 如果存在id,说明是剩余发货时间需要动态计算
        if len(time_element.xpath('@id')) > 0:
            script_str = time_element.xpath('./script/text()')[0].strip()
            m = re.search(r'addTimer\(".*?",\s*(\d+),', script_str)
            remaining_ship_time = None
            if m:
                # 剩余发货时间
                remaining_ship_time = get_remaining_ship_time(int(m.group(1)))
            # 如果是None就代表已到期
            time_dict['remaining_ship_time'] = remaining_ship_time

        else:
            time_name, time_value = time_element.xpath('text()')[0].split("：")
            if time_name == '下单':
                time_dict['order_time'] = time_value
            elif time_name == '付款':
                time_dict['pay_time'] = time_value
            elif time_name == '发货':
                time_dict['ship_time'] = time_value
            elif time_name == '提交':
                time_dict['submit_time'] = time_value
            else:
                time_dict[time_name] = time_value
    return [{
        'sku_list': sku_list,
        'currency': currency,
        'price': float(price.replace(',', '')),
        'recipient': recipient,
        'country': country,
        'order_id': order_id,
        'remark': remark,
        'time': time_dict
    }]


def get_merge_order_item_list(order_element_list: list[html.HtmlElement]):
    """
    解析获取合并单的订单项列表
    :return:
    """
    order_item_list = list()
    for order_element in order_element_list:
        order_item_list.extend(get_single_order_item_list(order_element))
    return order_item_list


def get_order_buyer_select_provider(good_element: html.HtmlElement):
    """
    获取买家指定
    :return:
    """
    # 第一种情况
    buyer_select_provider_list = good_element.xpath('.//span[contains(@class, "buyerSelectProvider")]/text()')
    # 第二种情况
    buyer_select_provider_2_list = good_element.xpath('./td[3]/text()')[0].strip().split("：")
    if len(buyer_select_provider_list) > 0:
        buyer_select_provider = buyer_select_provider_list[0]
    elif len(buyer_select_provider_2_list) == 2:
        buyer_select_provider = buyer_select_provider_2_list[1].strip()
    else:
        buyer_select_provider = None
    return buyer_select_provider


def list_order_base_by_html(html_str: str) -> list[dict]:
    """
    获取基本的订单分页信息
    有三种情况:
        1. 合并单
        2. 一单多件
        3. 普通一单一件
    :param html_str:
    :return:
    """
    tree = html.fromstring(html_str)
    good_element_list = tree.xpath('//tbody[@class="xianshishujudate"]/tr[@class="goodsId"]')
    order_list = list()
    table_columns = tree.xpath('//table[@id="orderListTable"]/thead/tr/th/text()')
    # 是否又物流方式
    has_logistics = True if '物流方式' in table_columns else False
    for good_element in good_element_list:
        # 包裹号
        package_number = good_element.xpath('.//a[@class="limingcentUrlpic"]/text()')[0]
        # 包裹id
        package_id = good_element.xpath('.//input[@class="input1"]/@value')[0]
        # authid 物流方式的id
        auth_id = good_element.xpath(f'.//input[@id="dxmAuthId{package_id}"]/@value')[0]
        # data-custom-mark标记
        data_custom_mark = get_str_list_first_not_blank_or_none(good_element.xpath('@data-custom-mark'))
        buyer_select_provider = get_order_buyer_select_provider(good_element)
        order_form_source = good_element.xpath('.//span[contains(@class, "order-form-source")]/text()')[0]
        platform, shop = order_form_source.replace('「', '').replace('」', '').split('：')
        order_class = f"orderId_{package_id}"
        order_element_list = tree.xpath(f'//tr[@class="{order_class}"]')
        order_first_element = order_element_list[0]
        # 订单备注
        hover_prompt_content_list = good_element.xpath('.//span[contains(@class, "hoverPrompt")]/@data-content')
        # 物流方式, 要先检查是否包含物流方式这一列
        logistics_info = None
        if has_logistics:
            # 物流方式
            logistics_list = order_first_element.xpath('.//td[6]/span/a/text()')
            # 可能又不存在的物流方式情况发生
            if len(logistics_list) > 0:
                logistics_info = dict()
                logistics = logistics_list[0].strip()
                # 物流单号
                logistics_info['track_number'] = get_str_list_first_not_blank_or_none(
                    order_first_element.xpath('.//td[6]//span[contains(@class, "limingcentUrlpicson")]/a/text()'))
                logistics_info['logistics'] = logistics
                # 称重重量
                weight_element_list = order_first_element.xpath('.//td[6]//span[@class="gray-c"]/text()')
                weight = None
                for weight_element in weight_element_list:
                    if '称重重量' in weight_element:
                        # 如果包含了称重重量的话，获取完整的数字部分
                        weight = float(re.search(r'\d+(?:\.\d+)?', weight_element).group())
                # 设置重量部分
                logistics_info['weight'] = weight

        # 状态
        if has_logistics:
            status = get_str_list_first_not_blank_or_none(order_first_element.xpath('.//td[7]/text()'))
        else:
            status = get_str_list_first_not_blank_or_none(order_first_element.xpath('.//td[6]/text()'))
        # 整理订单
        if len(order_element_list) > 1:
            # 合并单
            order_item_list = get_merge_order_item_list(order_element_list)
        else:
            # 普通单
            order_item_list = get_single_order_item_list(order_element_list[0])
        order_list.append({
            'package_id': package_id,
            'auth_id': auth_id,
            'package_number': package_number,
            'data_custom_mark': data_custom_mark,
            'buyer_select_provider': buyer_select_provider,
            'platform': platform,
            'shop': shop,
            'hover_prompt_content_list': hover_prompt_content_list,
            'logistics_info': logistics_info,
            'status': status,
            'order_item_list': order_item_list
        })
    return order_list


def list_order_rule(html_str: str):
    """
    获取订单规则列表
    :return:
    """
    tree = html.fromstring(html_str)
    rule_element_list = tree.xpath('//tbody[@id="ruleTbody"]/tr[@class="content rulesTr"]')
    rule_list = list()
    for rule_element in rule_element_list:
        rule_id = rule_element.xpath('./td[1]/input/@data-id')[0]
        rule_name = rule_element.xpath('./td[2]/text()')[0]
        status = rule_element.xpath('./td[5]/span/text()')[0]
        rule_list.append({
            'rule_id': rule_id,
            'rule_name': rule_name,
            'status': status
        })
    return rule_list


def get_rule_detail(html_str: str) -> DxmOrderRule:
    """
    根据订单规则的html获取订单规则详情
    :param html_str:
    :return:
    """
    tree = html.fromstring(html_str)
    cond_element_list = tree.xpath('//ul[@id="chooseSelectUl"]/li')
    cond_list = list()
    # 获取规则的条件
    for cond_element in cond_element_list:
        cond_val = cond_element.xpath('.//input[@name="condVal"]/@value')[0]
        cond_id = cond_element.xpath('.//input[@name="condId"]/@value')[0]
        cond_name = cond_element.xpath('.//input[@name="condName"]/@value')[0]
        cond_unit = cond_element.xpath('.//input[@name="condUnit"]/@value')[0]
        cond_type = cond_element.xpath('.//input[@name="condType"]/@value')[0]
        cond_list.append(DxmOrderRuleCond(cond_val=cond_val,
                                          cond_id=cond_id,
                                          cond_name=cond_name,
                                          cond_unit=cond_unit,
                                          cond_type=cond_type))
    # 判断是物流规则还是审核规则
    modal_title = tree.xpath('//h4[@class="modal-title"]/text()')[0]
    rule_id = tree.xpath('//input[@name="id"]/@value')[0]
    rule_type = tree.xpath('//input[@name="type"]/@value')[0]
    rule_name = tree.xpath('//input[@id="ruleName"]/@value')[0]
    gift_doubly = tree.xpath('//input[@id="giftDoubly"]/@value')[0]

    kfbz = get_str_list_first_not_blank_or_none(tree.xpath('//textarea[@name="kfbz"]/text()')) or ''
    jhbz = get_str_list_first_not_blank_or_none(tree.xpath('//textarea[@name="jhbz"]/text()')) or ''
    jh_color = tree.xpath('//input[@id="jhColor"]/@value')[0]
    other_action_checked_list = tree.xpath('//input[@name="otherAction"]/@checked')
    other_action = 'on' if len(other_action_checked_list) > 0 else ''
    custom_mark = tree.xpath('//div[contains(@class, "customMarkRuleEl")]/@data-custom-mark')[0]

    if modal_title.count('物流') > 0:
        warehouse_element_list = tree.xpath('//select[@id="ruleWareIdSelect"]//option')
        warehouse_id = ''
        distribute_type = ''
        for warehouse_element in warehouse_element_list:
            if warehouse_element.get('selected') == 'selected':
                warehouse_id = warehouse_element.get('value')
        distribute_type_element_list = tree.xpath('//input[@name="distributeType"]')
        for distribute_type_element in distribute_type_element_list:
            if distribute_type_element.get('checked') == 'checked':
                distribute_type = distribute_type_element.get('value')
        auth_ids = tree.xpath('//input[@name="authIds"]/@value')[0]
        pattern = re.compile(r"if\s*\(\s*'(\d+)'\s*===\s*item\.idStr")
        auth_id = pattern.findall(html_str)[0]
        # 物流规则
        dxm_rule_order = DxmOrderLogisticsRule(gift_doubly=gift_doubly, dxm_cond_list=cond_list, id=rule_id,
                                               type=rule_type,
                                               rule_name=rule_name, kfbz=kfbz, jhbz=jhbz,
                                               jh_color=jh_color, other_action=other_action,
                                               custom_mark=get_data_custom_mark_to_str(custom_mark),
                                               ware_id=warehouse_id, auth_id=auth_id, distribute_type=distribute_type,
                                               auth_ids=auth_ids
                                               )
    else:
        action = tree.xpath('//input[@name="action"]/@value')[0]
        dxm_rule_order = DxmOrderReviewRule(gift_doubly=gift_doubly, dxm_cond_list=cond_list, id=rule_id,
                                            type=rule_type,
                                            rule_name=rule_name, kfbz=kfbz, jhbz=jhbz,
                                            jh_color=jh_color, other_action=other_action,
                                            custom_mark=get_data_custom_mark_to_str(custom_mark),
                                            action=action
                                            )

    return dxm_rule_order


def get_order_detail_by_html(html_str: str):
    tree = html.fromstring(html_str)
    recipient = get_str_list_first_not_blank_or_none(tree.xpath('//div[@id="detailContact1"]/@data-info'))
    phone = get_str_list_first_not_blank_or_none(tree.xpath('//div[@id="detailPhone1"]/@data-info'))
    mobile = get_str_list_first_not_blank_or_none(tree.xpath('//div[@id="detailMobile1"]/@data-info'))
    country = get_str_list_first_not_blank_or_none(tree.xpath('//div[@id="detailCountry1"]/@data-country'))
    province = get_str_list_first_not_blank_or_none(tree.xpath('//div[@id="detailProvince1"]/text()'))
    city = get_str_list_first_not_blank_or_none(tree.xpath('//div[@id="detailCity1"]/text()'))
    addr1 = get_str_list_first_not_blank_or_none(tree.xpath('//div[@id="detailAddr11"]/@data-info'))
    addr2 = get_str_list_first_not_blank_or_none(tree.xpath('//div[@id="detailAddress21"]/@data-info'))
    company = get_str_list_first_not_blank_or_none(tree.xpath('//div[@id="companyName1"]/text()'))
    apartment = get_str_list_first_not_blank_or_none(tree.xpath('//div[@id="apartmentNumber1"]/text()'))
    zip_code = get_str_list_first_not_blank_or_none(tree.xpath('//div[@id="detailZip1"]/text()'))
    tax_number = get_str_list_first_not_blank_or_none(tree.xpath('//div[@id="taxNumber1"]/text()'))

    pair_info_element_list = tree.xpath('//tr[@class="orderInfoCon pairProInfoBox"]')
    ids = re.findall(r"var\s+storageId\s*=\s*['\"](\d+)['\"]", html_str)
    # 有就取第一个，否则 None
    storage_id = ids[0] if ids else None
    pair_info_list = []
    for pair_info_element in pair_info_element_list:
        pair_info_sku = pair_info_element.xpath('.//span[@class="pairProInfoSku"]/text()')[0].split(' x')[0].strip()
        pair_info_sku_quantity = int(pair_info_element.xpath('.//span[@class="pairProInfoSku"]/span/text()')[0].strip())
        proid = get_str_list_first_not_blank_or_none(pair_info_element.xpath('.//input[@proid]/@proid'))
        warehouse_sku_info_list = pair_info_element.xpath('.//div[contains(@class, "normalDiv")]/p[1]/text()')
        warehouse_sku, warehouse_sku_quantity = None, None
        if len(warehouse_sku_info_list) > 0:
            warehouse_sku_info = warehouse_sku_info_list[0]
            warehouse_sku, warehouse_sku_quantity = warehouse_sku_info.split(' x ')

        # 获取可用库存
        warehouse_available_quantity_element_list = pair_info_element.xpath(
            './/div[contains(@class, "normalDiv")]/p[2]/span[2]/text()')
        warehouse_available_quantity_str = get_str_list_first_not_blank_or_none(
            warehouse_available_quantity_element_list)
        # 获取到可用库存节点
        if warehouse_available_quantity_str is not None:
            if warehouse_available_quantity_str.endswith('+'):
                warehouse_available_quantity_str = warehouse_available_quantity_str[:-1]
            warehouse_available_quantity = int(warehouse_available_quantity_str)
        else:
            warehouse_available_quantity = None
        pair_info_list.append({
            'pair_info_sku': pair_info_sku,
            'pair_info_sku_quantity': pair_info_sku_quantity,
            'proid': proid,
            'warehouse_sku': warehouse_sku,
            'warehouse_sku_quantity': warehouse_sku_quantity,
            'warehouse_available_quantity': warehouse_available_quantity
        })
    return {
        'recipient': recipient,
        'phone': phone,
        'mobile': mobile,
        'country': country,
        'province': province,
        'city': city,
        'addr1': addr1,
        'addr2': addr2,
        'company': company,
        'apartment': apartment,
        'zip_code': zip_code,
        'tax_number': tax_number,
        'pair_info_list': pair_info_list,
        'storage_id': storage_id
    }


def parse_comm_search_list_html_get_authid_dict(html_str: str, keyword: str):
    """
    解析网页获取物流方式id字典
    :param html_str:
    :param keyword:
    :return:
    """
    tree = html.fromstring(html_str)
    logistics_authid_dict = {}
    logistics_method_element_list = tree.xpath('//select[@id="advancedAuthSelect"]/option')
    for logistics_method in logistics_method_element_list:
        logistics_authid_text = str(logistics_method.xpath('text()')[0])
        logistics_authid_value = logistics_method.xpath('@value')[0]
        if keyword in logistics_authid_text:
            logistics_authid_dict[logistics_authid_text] = logistics_authid_value
    return logistics_authid_dict
