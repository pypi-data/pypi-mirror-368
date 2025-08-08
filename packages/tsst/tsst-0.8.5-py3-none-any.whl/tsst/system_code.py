from enum import Enum

# 0000      : 成功

# 1000~1999 : 系統錯誤 last:1005
# 2000~2999 : 網路錯誤 last:--
# 3000~3999 : 資料庫錯誤 last:--
# 4000~4999 : 用戶輸入錯誤 last:4000

class BaseCode(Enum):
    @property
    def code(self):
        return self.value["code"]

    @property
    def message(self):
        return self.value["message"]


class SuccessCode(BaseCode):
    Success = {"code": "0000", "message": "Success"}
    LoginSuccess = {"code": "0000", "message": "登入成功"}
    FetchMarketLiveSuccess = {"code": "0000", "message": "已訂閱報價資料"}
    CancelMarketLiveSuccess = {"code": "0000", "message": "已取消訂閱報價資料"}
    CreateOrderSuccess = {"code": "0000", "message": "下單成功"}
    CreateFileSuccess = {"code": "0000", "message": "建立檔案成功"}
    ModifyOrderSuccess = {"code": "0000", "message": "改單成功"}
    CancelOrderSuccess = {"code": "0000", "message": "刪單成功"}
    BackFillingSuccess = {"code": "0000", "message": "回補即時資料成功"}
    FetchAccountBalanceSuccess = {"code": "0000", "message": "取得帳戶餘額成功"}
    FetchMarginSuccess = {"code": "0000", "message": "取得保證金成功"}

class ErrorCode(BaseCode):

    # SingIn相關(A1000-A1999)
    # =================================
    # 登入錯誤
    SignInError = {"code": "A1000", "message": "無法登入"}

    # Balance相關(A2000-A2999)
    # =================================
    # 取得帳戶餘額錯誤
    FetchAccountBalanceError = {"code": "A2000", "message": "無法取得帳戶餘額"}
    # 回傳帳戶餘額錯誤
    ReceiveAccountBalanceError = 2001

    # Portfolio相關(A3000-A3999)
    # =================================
    # 取得投資組合錯誤
    FetchPortfolioError = {"code": "A3000", "message": "無法取得投資組合"}
    # 回傳投資組合錯誤
    ReceivePortfolioError = 3001

    # Market相關(A4000-A4999)
    # =================================
    # 訂閱市場資訊錯誤
    GetInstantQuotesError = {"code": "A4000", "message": "無法訂閱即時資料"}
    # 取消訂閱市場資訊錯誤
    CancelMarketLiveError = {"code": "A4001", "message": "無法取消訂閱即時資料"}
    # 取得歷史資料錯誤
    FetchMarketHistoryError = {"code": "A4002", "message": "無法取得歷史資料"}

    # Order相關(A5000-A5999)
    # =================================
    # 下單錯誤
    CreateOrderError = {"code": "A5000", "message": "無法下單"}
    # 判斷下單狀態錯誤
    JudgeOrderStatusError = {"code": "A5001", "message": "取得委託或成交回報時發生錯誤"}
    # 取得交易帳號錯誤
    TradeAccountError = {"code": "A5002", "message": "無法取得交易帳號"}
    # 委託回報錯誤
    ReceiveStockOrderError = {"code": "A5003", "message": "無法取得委託回報"}
    # 成交回報錯誤
    ReceiveStockDealError = {"code": "A5004", "message": "無法取得成交回報"}
    # 找不到交易物件(永豐才會發生這個狀況, 因為永豐的改單, 刪單需要透過 Trade 物件)
    TradeNotFound = {"code": "A5005", "message": "找不到交易物件(永豐)"}
    # 改價錯誤
    ModifyPriceError = {"code": "A5006", "message": "改價發生問題"}
    # 改量錯誤
    ModifyQuantityError = {"code": "A5007", "message": "改量發生問題"}
    # 刪單錯誤
    CancelOrderError = {"code": "A5008", "message": "刪單發生問題"}

    # kBar相關(A6000-A6999)
    # =================================
    GetInstantKBarError = {"code": "A6000", "message": "無法取得即時kBar資料"}
    GetHistoryKBarError = {"code": "A6001", "message": "無法取得歷史kBar資料"}
    CalculateDelayTimeError = {"code": "A6002", "message": "計算延遲時間錯誤"}
    GetNowTimeError = {"code": "A6003", "message": "取得現在時間時發生錯誤"}

    # 計算相關(B7000-B7999)
    # =================================
    FeesAndTaxArgError = {"code": "B7000", "message": "計算手續費時發生參數錯誤"}
    FeesAndTaxCalculateError = {"code": "B7001", "message": "計算手續費時發生計算錯誤"}

    # 回測模擬相關(B8000-B8999)
    # =================================
    CheckOrderIdError = {"code": "B8000", "message": "生產新委託單號時發生錯誤"}
    CheckPriceTypeArgError = {"code": "B8001", "message": "檢查價格類型時發生參數錯誤"}
    CapitalNotEnoughError = {"code": "B8002", "message": "判斷資金是否充足時發生錯誤"}

    # 驗證參數相關(A9000-)
    # =================================
    PydanticError = {"code": "A9000", "message": "參數錯誤"}
    ProductTypeError = {"code": "A9001", "message": "產品類型錯誤"}

class TsstErrorCode(BaseCode):
    """TSST 錯誤代碼
    """
    # 縮寫說明
    # BT: 回測模組相關相關
    # SYS: 系統問題相關
    # AUTH: 身分驗證相關
    BackTestInitError = {"code": "BT-10000", "message": "回測模組初始化錯誤，請確認回測模組是否正常啟動"}
    BacktestTimeout = {"code": "BT-10001", "message": "回測模組連線超時，請確認連線狀態"}
    BacktestLoginFailed = {"code": "BT-10002", "message": "回測模組登入失敗，請確認登入參數是否正確"}
    BacktestMethodNotFound = {"code": "BT-10003", "message": "回測模組找不到指定方法，請確認方法名稱是否正確或者回測模組是否正常啟動"}
    
    ProductCodeNotFound = {"code": "SYS-10000", "message": "找不到商品代碼: %s"}
    MarketCodeNotFound = {"code": "SYS-10001", "message": "找不到市場代碼: %s"}
    SubscribeFailed = {"code": "SYS-10002", "message": "訂閱失敗"}
    UnsubscribeFailed = {"code": "SYS-10003", "message": "取消訂閱失敗"}
    BrokerNotSupport = {"code": "SYS-10004", "message": "不支援的券商代號: %s"}
    BackFillingFailed = {"code": "SYS-10005", "message": "回補即時失敗"}
    SubscribeNotSupport = {"code": "SYS-10006", "message": "不支援訂閱功能"}
    BackFillingNotSupport = {"code": "SYS-10007", "message": "不支援回補功能"}
    OrderFailed = {"code": "SYS-10008", "message": "下單失敗"}
    ModifyOrderFailed = {"code": "SYS-10009", "message": "改單失敗"}
    CancelOrderFailed = {"code": "SYS-10010", "message": "刪單失敗"}
    
    LoginFailed = {"code": "AUTH-10000", "message": "登入失敗"}