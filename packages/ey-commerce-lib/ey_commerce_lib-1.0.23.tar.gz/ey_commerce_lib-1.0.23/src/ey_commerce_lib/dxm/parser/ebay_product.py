from lxml import html


def parse_ebay_product_page(page_html: str):
    tree = html.fromstring(page_html)
    # 获取eBay产【
    ebay_product_items = tree.xpath('//tbody[@id="ebaySysMsg"]/tr')
    for ebay_product_item in ebay_product_items:
        ebay_id = ebay_product_item.xpath('@data-id')
        sku = ebay_product_item.xpath('./td[4]/text()')
        # 获取子表
        sub_table = ebay_product_item.xpath('.//table[@class="in-table-in"]//tr')
        # 获取proId
        pro_id = sub_table[0].xpath('./td[1]/text()')
        # TODO 获取后续逻辑

