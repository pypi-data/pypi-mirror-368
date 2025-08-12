def get_power_indices(n: int) -> list:
    """
    输入一个整数 n，返回一个列表，列表中的每个数字代表 n 的二进制表示中对应为1的位的幂次（从0开始计数）

    例如：
      - n = 5（二进制 101），返回 [0, 2]
      - n = 32（二进制 100000），返回 [5]
    """
    result = []
    power = 0
    while n:
        # 判断当前最低位是否为1
        if n & 1:
            result.append(power)
        n >>= 1  # 右移一位，相当于除以2
        power += 1
    return result


# 定义店小秘的标记颜色
CUSTOMER_ORDER_MARK_COLORS = ['isGreen', 'isYellow', 'isOrange', 'isRed', 'isViolet', 'isBlue', 'cornflowerBlue',
                              'pink', 'teal', 'turquoise']


def get_custom_mark_content_list_by_data_custom_mark(data_custom_mark: str, custom_mark_config: list):
    """
    根据店小秘订单标记数据，返回一个列表，列表中的每个元素代表一个标记的内容
    :param custom_mark_config: 标记配置
    :param data_custom_mark: 店小秘订单标记数据，html中data_custom_mark的值
    :return:
    """
    mark_content_list = []
    for index, mkv in enumerate(data_custom_mark.split(',')):
        color_value = int(mkv)
        # 根据CUSTOMER_ORDER_MARK_COLORS的位置一一判断
        for color_number in get_power_indices(color_value):
            # 拿到运算后颜色序号值 列入isGreen_1 的序号值
            # 自定义标记的key
            mark_key = f'{CUSTOMER_ORDER_MARK_COLORS[index]}_{color_number}'
            for config in custom_mark_config:
                if config['key'] == mark_key:
                    mark_content_list.append(config['content'])
                    break
    return mark_content_list


def lowercase_first_letter(s):
    if not s:
        return s
    return s[0].lower() + s[1:]


def generate_add_or_update_user_comment_data_by_content_list(package_id: str, content_list: list,
                                                             custom_mark_config: list,
                                                             history: str = ''
                                                             ):
    """
    根据内容列表生成店小秘新增或者修改自定义标志的接口数据
    :param history: 是否为历史订单 默认值不是
    :param package_id: 店小秘包裹id
    :param custom_mark_config: 自定义标注配置
    :param content_list: 标注内容列表
    :return:
    """
    data = {}
    # 先对content_list去重,防止生成重复标记
    content_list = list(set(content_list))
    #============================================================
    # 计算标记颜色值start
    #============================================================
    # 准备计算标记的颜色值字典
    ready_calc_color_dict = {}
    # 在根据内容列表去计算颜色值
    for content in content_list:
        for config in custom_mark_config:
            # 内容匹配上并且颜色是要带生成最终计算数值的二进制索引的key
            mark_key_list = config['key'].split('_')
            # 设置标注的内容匹配上了，并且是带有计算二进制位数的
            if config['content'] == content and len(mark_key_list) == 2:
                color = config['color']
                if ready_calc_color_dict.get(color) is None:
                    ready_calc_color_dict[color] = []
                # 添加颜色对应的索引值
                ready_calc_color_dict[color].append(int(mark_key_list[1]))
                break
    # 计算颜色值
    for index, color in enumerate(CUSTOMER_ORDER_MARK_COLORS):
        color_keys = ready_calc_color_dict.keys()
        if color in color_keys:
            # 计算索引位置的二进制值
            data[color] = sum([2 ** i for i in ready_calc_color_dict[color]])
        else:
            # 没有设置颜色值取0
            data[color] = 0
    # ============================================================
    # 计算标记颜色值end
    # ============================================================

    #生成颜色对应内容
    for color in CUSTOMER_ORDER_MARK_COLORS:
        for config in custom_mark_config:
            # 如果标记值和颜色常量匹配上
            if config['key'] == color:
                color_content_key = f"{lowercase_first_letter(color.replace('is', ''))}Content"
                data[color_content_key] = config['content']
                break
    data['history'] = history
    data['orderId'] = package_id
    return data
