"""自定义异常类型"""

class QQAPIException(Exception):
    """QQ服务异常"""

    def __init__(self,err='QQ服务器错误', *args, **kwargs):
        # super().__init__(*args, **kwargs)
       self.err = err

