import re
from typing import TypedDict

from lxml import html

from ey_commerce_lib.dxm.exception.common import PageInfoNotFoundException
from ey_commerce_lib.model import Page


class PageInfo(TypedDict):
    page_size: int
    total_page: int
    total_size: int
    page_number: int


def get_page_info(html_str: str) -> PageInfo:
    """
    获取分页信息和分页数据
    :return:
    """
    tree = html.fromstring(html_str)
    page_size_list = tree.xpath('//input[@id="pageSize"]/@value')
    total_page_list = tree.xpath('//input[@id="totalPage"]/@value')
    total_size_list = tree.xpath('//input[@id="totalSize"]/@value')
    page_number_list = tree.xpath('//input[@id="pageNo"]/@value')
    if len(page_size_list) == 0 or len(total_page_list) == 0:
        raise PageInfoNotFoundException("分页信息获取失败")
    return {
        'page_size': int(page_size_list[0]),
        'total_page': int(total_page_list[0]),
        'total_size': int(total_size_list[0]),
        'page_number': int(page_number_list[0])
    }


def __parse_js_vals(js_snippet: str) -> dict[str, int]:
    """
    从一段包含 jQuery .val(...) 赋值语句的 JS 代码字符串中，
    提取所有 id 和对应的数值，并返回一个 {id: int} 形式的字典。

    参数
    ----
    js_snippet : str
        包含类似 `$('#pageNo').val('1');` 的 JavaScript 代码。

    返回
    ----
    Dict[str, int]
        键是每个 .val() 前的 id（如 'pageNo'），值是对应的整数。
    """
    pattern = r"\$\('#(?P<key>\w+)'\)\.val\('(?P<value>\d+)'\);"
    matches = re.findall(pattern, js_snippet)
    return {key: int(value) for key, value in matches}


def get_purchase_pagination_info(script: str) -> dict:
    # 定义要提取的字段及其对应的 key 名
    field_map = {
        'pageNo': 'page_number',
        'pageSize': 'page_size',
        'totalSize': 'total_size',
        'totalPage': 'total_page',
    }

    result = {}

    for field, key in field_map.items():
        pattern = rf"\$\('#{field}'\)\.val\('(\d+)'\);"
        match = re.search(pattern, script)
        if not match:
            raise ValueError(f"无法从字符串中提取字段：{field}")
        result[key] = int(match.group(1))

    return result


def get_purchasing_page_info(html_str: str):
    """
    获取分页信息和分页数据(店小秘->采购部分)
    :param html_str:
    :return:
    """
    page_number = __parse_js_vals(html_str).get('pageNo')
    page_size = __parse_js_vals(html_str).get('pageSize')
    total_page = __parse_js_vals(html_str).get('totalPage')
    total_size = __parse_js_vals(html_str).get('totalSize')
    if page_number is None or page_size is None or total_page is None or total_size is None:
        raise PageInfoNotFoundException("分页信息获取失败")
    return {
        'page_size': page_size,
        'total_page': total_page,
        'total_size': total_size,
        'page_number': page_number
    }


def get_tracking_page_info(html_str: str):
    tree = html.fromstring(html_str)
    total = int(tree.xpath('//input[@id="totalSizeOrder"]/@value')[0])
    page_size = int(tree.xpath('//input[@id="pageSizeOrder"]/@value')[0])
    page_number = int(tree.xpath('//input[@id="pageNoOrder"]/@value')[0])
    total_page = int(tree.xpath('//input[@id="totalPageOrder"]/@value')[0])
    return Page(
        total=total,
        page_size=page_size,
        page_number=page_number,
        total_page=total_page,
        records=[]
    )

