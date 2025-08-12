from typing import Optional


def get_list_first_or_none(array: list) -> Optional[any]:
    """
    获取列表第一个元素没有则获取空
    :param array:
    :return:
    """
    if len(array) > 0:
        return array[0]
    return None


def get_str_list_first_not_blank_or_none(array: list) -> Optional[str]:
    """
    获取列表第一个元素(不能为'')没有则获取空
    :param array:
    :return:
    """
    if len(array) > 0 and array[0] != '':
        return array[0].strip()
    return None
