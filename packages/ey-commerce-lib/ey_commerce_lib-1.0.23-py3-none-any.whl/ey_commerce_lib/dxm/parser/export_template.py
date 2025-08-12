from lxml import html


def parse_list_export_template(html_content: str):
    tree = html.fromstring(html_content)
    export_template_element_list = tree.xpath('//div[@class="page-list no-page"]/table[@class="in-table"]/tbody/tr')
    export_template_list = []
    for export_template_element in export_template_element_list:
        template_id = export_template_element.xpath('@id')[0].replace('tr', '')
        template_name = export_template_element.xpath('./td[1]/text()')[0].strip()
        field_str = export_template_element.xpath('./td[2]/text()')[0].strip()
        export_template_list.append({
            'template_id': template_id,
            'template_name': template_name,
            'field_str': field_str
        })
    return export_template_list
