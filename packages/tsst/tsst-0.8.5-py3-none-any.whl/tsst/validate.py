from typing import Literal, Union

from pydantic import BaseModel, Field


# K棒參數驗證模型
class KbarParams(BaseModel):
    ''' K棒參數驗證模型
    '''
    # 商品代號
    code: str = Field(strict=True)

    # K棒頻率
    freq: int = Field(strict=True)

    # K棒週期
    unit: Literal["m", "h", "d", "w", "mo", "q", "y"]

    # 額外運算式
    exprs: list = Field(strict=True)

    # 是否轉換為 pandas DataFrame
    to_pandas_df: bool

# Tick 參數驗證模型
class TickParams(BaseModel):
    ''' Tick 參數驗證模型
    '''
    # 市場類型
    market_type: str = Field(strict=True)

    # 時間戳記
    timestamp: Union[int, float]

    # 商品代號
    code: str = Field(strict=True)

    # 收盤價
    close: float = Field(strict=True)

    # 交易量
    qty:   int = Field(strict=True)

    # Tick 類型
    tick_type: int = Field(strict=True)