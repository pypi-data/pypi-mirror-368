from ey_commerce_lib.dxm.schemas.dxm_commodity_product import ViewDxmCommodityProductResponse, EditObj
from ey_commerce_lib.utils.float import truncate_decimal_str


def get_edit_commodity_product_by_view_dxm_response(data: ViewDxmCommodityProductResponse):
    """
    根据查看店小秘接口的响应
    :return:
    """
    dxm_commodity_product = data.product_dto.dxm_commodity_product
    dxm_product_customs = data.product_dto.dxm_product_customs

    product_id = dxm_commodity_product.id
    name = dxm_commodity_product.name
    name_en = dxm_commodity_product.name_en
    sku_code = dxm_commodity_product.sku_code
    sku = dxm_commodity_product.sku
    product_variation_str = ','.join(dxm_commodity_product.product_variation_str_list)
    sbm_id = dxm_commodity_product.sbm_id
    agent_id = dxm_commodity_product.agent_id
    development_id = dxm_commodity_product.development_id
    sales_id = dxm_commodity_product.sales_id
    weight = dxm_commodity_product.weight
    allow_weight_error = dxm_commodity_product.allow_weight_error
    price = dxm_commodity_product.price
    source_url = dxm_commodity_product.source_url
    img_url = dxm_commodity_product.img_url
    is_used = dxm_commodity_product.is_used
    full_cid = dxm_commodity_product.full_cid
    product_type = dxm_commodity_product.product_type
    length = dxm_commodity_product.length
    width = dxm_commodity_product.width
    height = dxm_commodity_product.height
    qc_type = dxm_commodity_product.qc_type
    product_status = dxm_commodity_product.product_status
    child_ids = dxm_commodity_product.child_ids
    child_nums = dxm_commodity_product.child_nums
    process_fee = dxm_commodity_product.process_fee
    qc_content = dxm_commodity_product.qc_content
    qc_img_num = dxm_commodity_product.qc_img_num
    group_state = dxm_commodity_product.group_state
    ncm = dxm_commodity_product.ncm
    cest = dxm_commodity_product.cest
    unit = dxm_commodity_product.unit
    origin = dxm_commodity_product.origin

    name_cn_bg = dxm_product_customs.name_cn
    name_en_bg = dxm_product_customs.name_en
    weight_bg = dxm_product_customs.weight
    price_bg = dxm_product_customs.price
    material_bg = dxm_commodity_product.material_bg
    purpose_bg = dxm_commodity_product.purpose_bg
    hgbm_bg = dxm_commodity_product.hgbm_bg
    danger_des_bg = dxm_commodity_product.danger_des_bg

    warehouse_id_list = data.product_dto.warehouse_id_list

    supplier_product_relation_map_list = data.product_dto.supplier_product_relation_map_list or []
    new_supplier_product_relation_map_list = []
    for supplier_product_relation_map in supplier_product_relation_map_list:
        supplier_id = supplier_product_relation_map.supplier_id
        is_main = supplier_product_relation_map.is_main
        new_supplier_product_relation_map_list.append({
            'supplierId': supplier_id,
            'isMain': is_main
        })

    dxm_product_packs = data.product_dto.dxm_product_packs
    # sbmId 必须为字符串
    return EditObj.model_validate({
        'dxmCommodityProduct': {
            'productId': str(product_id),
            'name': name,
            'nameEn': name_en,
            'skuCode': sku_code,
            'sku': sku,
            'productVariationStr': product_variation_str,
            'sbmId': sbm_id if sbm_id is not None else '',
            'agentId': str(agent_id),
            'developmentId': str(development_id),
            'salesId': str(sales_id),
            'weight': truncate_decimal_str(weight),
            'allowWeightError': '',
            'price': truncate_decimal_str(price),
            'sourceUrl': source_url,
            'imgUrl': img_url,
            'isUsed': is_used,
            'fullCid': full_cid,
            'productType': product_type,
            'length': length,
            'width': width,
            'height': height,
            'qcType': qc_type,
            'productStatus': 1,
            'childIds': child_ids if child_ids is not None else '',
            'childNums': child_nums if child_nums is not None else '',
            'processFee': process_fee,
            'qcContent': qc_content if qc_content is not None else '',
            'qcImgNum': qc_img_num,
            'groupState': str(group_state),
            'ncm': ncm if ncm is not None else '',
            'cest': cest if cest is not None else '',
            'unit': unit if unit is not None else '',
            'origin': origin if origin is not None else '0'
        },
        'dxmProductCustoms': {
            'nameCnBg': name_cn_bg,
            'nameEnBg': name_en_bg,
            'weightBg': truncate_decimal_str(weight_bg),
            'priceBg': truncate_decimal_str(price_bg, 4),
            'materialBg': material_bg if material_bg is not None else '',
            'purposeBg': purpose_bg if purpose_bg is not None else '',
            'hgbmBg': hgbm_bg if hgbm_bg is not None else '',
            'dangerDesBg': danger_des_bg if danger_des_bg is not None else '0'
        },
        'warehouseIdList': warehouse_id_list if warehouse_id_list is not None else '',
        'supplierProductRelationMapList': new_supplier_product_relation_map_list,
        'dxmProductPacks': dxm_product_packs
    }).model_dump_json(by_alias=True)

