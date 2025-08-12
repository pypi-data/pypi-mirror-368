from lxml import html


def parse_count(html_content: str):
    tree = html.fromstring(html_content)
    data_list = tree.xpath("//tr[@class='content']")
    result = []
    for data in data_list:
        date = data.xpath('./td/text()')[0].strip()
        order_number = data.xpath('./td/text()')[1].strip()
        # 订单总金额
        total_amount = data.xpath('./td/text()')[2].strip()
        # 订单手续费
        fee = data.xpath('./td/text()')[3].strip()
        # 物流费用
        logistics = data.xpath('./td/text()')[4].strip()
        # 利润
        profit = data.xpath('./td/text()')[5].strip()
        # 退单数量
        return_number = data.xpath('./td/text()')[6].strip()
        # 退单金额
        return_amount = data.xpath('./td/text()')[7].strip()
        # 退款率
        return_rate = data.xpath('./td/text()')[8].strip()
        # 成本利润
        cost_profit = data.xpath('./td/text()')[9].strip()
        # 销售利润
        sale_profit = data.xpath('./td/text()')[10].strip()
        # 添加数据
        result.append({
            'date': date,
            'order_number': order_number,
            'total_amount': total_amount,
            'fee': fee,
            'logistics': logistics,
            'profit': profit,
            'return_number': return_number,
            'return_amount': return_amount,
            'return_rate': return_rate,
            'cost_profit': cost_profit,
            'sale_profit': sale_profit
        })
    return result
