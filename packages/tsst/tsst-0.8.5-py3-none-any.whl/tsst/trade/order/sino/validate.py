from pydantic import Field
from typing import Literal, Optional
from tsst.trade.order.base_validate import BaseCreateOrder

class SinoCreateStockOrder(BaseCreateOrder):
    """永豐下單模組的股票訂單參數
    """
    order_cond: Literal["Cash", "MarginTrading", "ShortSelling"] = Field("Cash", description="委託條件")
    order_lot: Literal["Common", "Fixing", "Odd", "IntradayOdd"] = Field("Common", description="委託方式")
    daytrade_short: Optional[bool] = Field(False, description="先賣後買")

class SinoCreateFutureOrder(BaseCreateOrder):
    """永豐下單模組的期貨訂單參數
    """
    octype: Literal["Auto", "New", "Cover", "DayTrade"] = Field("Auto", description="開倉或平倉類型")
