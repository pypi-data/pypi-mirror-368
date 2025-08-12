from decimal import Decimal, ROUND_DOWN


def truncate_decimal(number, digits=2):
    """
    截断保留指定位数的小数（不四舍五入），并保留末尾的 0
    :param number: 输入的数字（int/float）
    :param digits: 保留的小数位数（默认2位）
    :return: 返回字符串形式，确保末尾 0 不省略
    """
    if isinstance(number, int):
        return f"{number}.{'0' * digits}"

    decimal_num = Decimal(str(number))
    truncated = decimal_num.quantize(
        Decimal('0.' + '0' * digits),
        rounding=ROUND_DOWN
    )
    return format(truncated, f".{digits}f")  # 强制保留末尾 0


def truncate_decimal_str(number, digits=2):
    """
    使用decimal模块实现（最精确的方式）
    """
    return str(truncate_decimal(number, digits))


if __name__ == '__main__':
    print(truncate_decimal(200.000, 4))
