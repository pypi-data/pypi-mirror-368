from pydantic import BaseModel, Field
from typing import Literal

class BaseCreateOrder(BaseModel):
    price: float = Field(..., gt=0, description="價格")
    quantity: float = Field(..., gt=0, description="數量")
    action: Literal["Buy", "Sell"] = Field(..., description="買賣方向")
    price_type: Literal["LMT", "MKT", "MKP"] = Field(..., description="價格類型")
    order_type: Literal["ROD", "IOC", "FOK"] = Field(..., description="委託類型")
    account: str = Field(None, description="下單帳戶")
