from tsst.system_code import TsstErrorCode

class BaseTsstException(Exception):
    """TSST 基底錯誤類別
    """
    def __init__(self, code: str, message: str):
        """
        Args:
            code (str): 錯誤代碼
            message (str): 錯誤訊息
        """
        self.code = code
        self.message = message

    def __str__(self):
        return f"[{self.code}]: {self.message}"

class SystemException(BaseTsstException):
    """TSST 系統相關錯誤類別
    """
    def __init__(self, code: str, message: str):
        """
        Args:
            code (str): 錯誤代碼
            message (str): 錯誤訊息
        """
        super().__init__(code, message)

class ProductCodeNotFound(SystemException):
    """找不到商品代碼
    """
    def __init__(self, code: str):
        """
        Args:
            code (str): 商品代碼
        """
        super().__init__(
            code = TsstErrorCode.ProductCodeNotFound.code,
            message = TsstErrorCode.ProductCodeNotFound.message.format(code)
        )

class MarketCodeNotFound(SystemException):
    """找不到市場代碼
    """
    def __init__(self, code: str):
        """
        Args:
            code (str): 市場代碼
        """
        super().__init__(
            code = TsstErrorCode.MarketCodeNotFound.code,
            message = TsstErrorCode.MarketCodeNotFound.message.format(code)
        )

class LoginFailed(SystemException):
    """登入失敗
    """
    def __init__(self):
        super().__init__(
            code = TsstErrorCode.LoginFailed.code,
            message = TsstErrorCode.LoginFailed.message
        )

class SubscribeFailed(SystemException):
    """訂閱失敗
    """
    def __init__(self):
        super().__init__(
            code = TsstErrorCode.SubscribeFailed.code,
            message = TsstErrorCode.SubscribeFailed.message
        )

class SubscribeNotSupport(SystemException):
    """不支援訂閱功能
    """
    def __init__(self):
        super().__init__(
            code = TsstErrorCode.SubscribeNotSupport.code,
            message = TsstErrorCode.SubscribeNotSupport.message
        )

class BackFillingNotSupport(SystemException):
    """不支援回補功能
    """
    def __init__(self):
        super().__init__(
            code = TsstErrorCode.BackFillingNotSupport.code,
            message = TsstErrorCode.BackFillingNotSupport.message
        )

class BrokerNotSupport(SystemException):
    """券商不支援
    """
    def __init__(self, broker_code: str):
        """
        Args:
            broker_code (str): 券商代號
        """
        super().__init__(
            code = TsstErrorCode.BrokerNotSupport.code,
            message = TsstErrorCode.BrokerNotSupport.message.format(broker_code)
        )

class BackFillingFailed(SystemException):
    """回補失敗
    """
    def __init__(self):
        super().__init__(
            code = TsstErrorCode.BackFillingFailed.code,
            message = TsstErrorCode.BackFillingFailed.message
        )

class ExternalException(BaseTsstException):
    """TSST 外部相關錯誤類別
    """
    def __init__(self, code: str, message: str):
        """
        Args:
            code (str): 錯誤代碼
            message (str): 錯誤訊息
        """
        super().__init__(code, message)

class BackTestInitError(ExternalException):
    """回測模組初始化錯誤
    """
    def __init__(self):
        super().__init__(
            code = TsstErrorCode.BackTestInitError.code,
            message = TsstErrorCode.BackTestInitError.message
        )

class BacktestTimeout(ExternalException):
    """回測模組連線超時
    """
    def __init__(self):
        super().__init__(
            code = TsstErrorCode.BacktestTimeout.code,
            message = TsstErrorCode.BacktestTimeout.message
        )

class BacktestLoginFailed(ExternalException):
    """回測模組登入失敗
    """
    def __init__(self):
        super().__init__(
            code = TsstErrorCode.BacktestLoginFailed.code,
            message = TsstErrorCode.BacktestLoginFailed.message
       )

class BacktestMethodNotFound(ExternalException):
    """回測模組方法不存在
    """
    def __init__(self):
        super().__init__(
            code = TsstErrorCode.BacktestMethodNotFound.code,
            message = TsstErrorCode.BacktestMethodNotFound.message
        )