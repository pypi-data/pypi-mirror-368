import math
from typing import TypedDict


class RemainingShipTime(TypedDict):
    day: int
    hour: int
    minute: int
    second: int


def get_remaining_ship_time(time_int) -> RemainingShipTime:
    """
    获取剩余发货时间
    :return:
    """
    d = math.floor(time_int / 86400)
    h = math.floor((time_int % 86400) / 3600)
    m = math.floor(((time_int % 86400) % 3600) / 60)
    s = math.floor(((time_int % 86400) % 3600) % 60)
    return {
        "day": d,
        "hour": h,
        "minute": m,
        "second": s
    }


def get_data_custom_mark_to_str(custom_mark: str) -> str:
    mark_list = custom_mark.split(',')
    color_str_list = list()
    mark_color_list = ['isGreen', 'isYellow', 'isOrange', 'isRed', 'isViolet', 'isBlue', 'cornflowerBlue', 'pink',
                       'teal',
                       'turquoise']

    for index in range(len(mark_list)):
        if index >= len(mark_list):
            break
        # print(mark_list[index])
        if mark_list[index] == '0':
            continue
        color_str_list.append(f'{mark_color_list[index]}_{mark_list[index]}')
    return '&'.join(color_str_list)
