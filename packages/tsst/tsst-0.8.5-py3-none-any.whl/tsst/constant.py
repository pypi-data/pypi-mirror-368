from enum import Enum

class BaseConstant(str, Enum):
    def __str__(self):
        return self.value  # 返回字串值

    def __format__(self, format_spec):
        return self.value  # 返回字串值
    
    @classmethod
    def from_value(cls, value):
        """允許根據 value 找到對應的 Enum 成員"""
        for member in cls:
            if member.value == value:
                return member.value
        raise ValueError(f"Invalid value: {value}")

class OperationType(BaseConstant):
    """操作類型
    """
    NEW = "New"
    CANCEL = "Cancel"
    UPDATE_PRICE = "UpdatePrice"
    UPDATE_QTY = "UpdateQty"
    DEAL = "Deal"
    UPDATE_PRICE_QTY = "UpdatePriceQty"
    DYNAMIC_CANCEL = "DynamicCancel"

class Action(BaseConstant):
    """買賣類型
    """
    BUY = "BUY"
    SELL = "SELL"

class PriceType(BaseConstant):
    """價格類型
    """
    LMT = "LMT"
    MKT = "MKT"
    MKP = "MKP"

class OrderType(BaseConstant):
    """委託類型
    """
    ROD = "ROD"
    IOC = "IOC"
    FOK = "FOK"

class OrderCond(BaseConstant):
    """委託條件
    """
    CASH = "Cash"
    MARGIN_T = "MarginTrading" # 融資
    SHORT_S = "ShortSelling" # 融券

class OrderLot(BaseConstant):
    """委託方式
    """
    COMMON = "Common" # 整股
    FIXING = "Fixing" # 盤後定盤
    ODD = "Odd" # 盤後零股
    INTRADAY_ODD = "IntradayOdd" # 盤中零股

class OCType(BaseConstant):
    """開倉或平倉類型
    """
    AUTO = "Auto"
    NEW = "New"
    COVER = "Cover"
    DAY_TRADE = "DayTrade"
