class PageInfoNotFoundException(Exception):
    """
    找不到分页参数异常
    """

    def __init__(self, msg):
        super().__init__(msg)
