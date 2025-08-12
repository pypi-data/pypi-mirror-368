from enum import IntEnum


class ResponseCodeEnum(IntEnum):
    # 登录验证失败
    LOGIN_VALIDATION_FAILED = 4001
    # 操作成功
    SUCCESS = 0
