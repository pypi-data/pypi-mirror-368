from lxml import html

from ey_commerce_lib.dxm.schemas.warehouse import WarehouseProduct


def __get_warehouse_product_by_xpath_element(warehouse_product_element: html.HtmlElement) -> WarehouseProduct:
    proid = warehouse_product_element.xpath('.//input[@iptid="selectSingle"]/@data-proid')[0].strip()
    sku = warehouse_product_element.xpath('.//span[contains(@class, "productSku")]/text()')[0].strip()
    name_list = warehouse_product_element.xpath('.//p[contains(@class, "name")]/text()')
    name = name_list[0].strip() if len(name_list) > 0 else ''
    sku_code = warehouse_product_element.xpath('.//div[contains(@class, "skuCode")]/span/text()')[0].strip()
    img = warehouse_product_element.xpath('.//img/@src')[0].strip()
    shelf_position = warehouse_product_element.xpath('.//td[3]/text()')[0].strip()
    # 库存详情元素
    warehouse_product_stock_element = warehouse_product_element.xpath('.//td[4]//tbody/tr')[0]
    # 安全库存
    try:
        safe_stock = int(warehouse_product_stock_element.xpath('./td[1]/span/text()')[0])
    except:
        safe_stock = None
    try:
        # # 在途库存
        on_the_way_stock = int(warehouse_product_stock_element.xpath('./td[2]/span/text()')[0])
    except:
        on_the_way_stock = None
    # 未发库存
    try:
        not_shipped_stock = int(warehouse_product_stock_element.xpath('./td[3]/span/text()')[0])
    except:
        not_shipped_stock = None
    try:
        # # 占用库存
        occupy_stock = int(warehouse_product_stock_element.xpath('./td[4]/span/text()')[0])
    except:
        occupy_stock = None
    # # 可用库存
    try:
        available_stock = int(warehouse_product_stock_element.xpath('./td[5]/span/text()')[0])
    except:
        available_stock = None
    # 总量库存
    try:
        total_stock = int(warehouse_product_stock_element.xpath('./td[6]/span/text()')[0])
    except:
        total_stock = None
    # 单价
    price = float(warehouse_product_element.xpath('./td[5]/text()')[0])
    # 总价
    total_price = float(warehouse_product_element.xpath('./td[6]/text()')[0])
    # 更新时间
    update_time = warehouse_product_element.xpath('./td[7]/div[1]/text()')[0]
    # 创建时间
    create_time = warehouse_product_element.xpath('./td[7]/div[2]/text()')[0]
    return WarehouseProduct(proid=proid, sku=sku, name=name, sku_code=sku_code, img=img, shelf_position=shelf_position,
                            safe_stock=safe_stock, on_the_way_stock=on_the_way_stock,
                            not_shipped_stock=not_shipped_stock, occupy_stock=occupy_stock,
                            available_stock=available_stock, total_stock=total_stock, price=price,
                            total_price=total_price, update_time=update_time, create_time=create_time)


def list_warehouse_product(html_content: str) -> list[WarehouseProduct]:
    tree = html.fromstring(html_content)
    warehouse_product_element_list = tree.xpath('//tbody/tr[@class="content"]')
    warehouse_product_list = list()
    for warehouse_product_element in warehouse_product_element_list:
        warehouse_product_list.append(__get_warehouse_product_by_xpath_element(warehouse_product_element))
    return warehouse_product_list
