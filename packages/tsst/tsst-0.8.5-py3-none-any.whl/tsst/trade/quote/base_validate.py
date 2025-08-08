from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from typing import List, Dict

class BaseQuote(BaseModel):
    codes: List[Dict[str, str]] = Field(..., title="List of stock codes")
    
    @model_validator(mode='before')
    def check_codes(cls, values):
        codes = values.get('codes', [])
        for code_dict in codes:
            # 確認每個元素是否為字典
            if not isinstance(code_dict, dict):
                raise ValueError("每個元素必須是字典")
            
            # 確認字典中是否包含 'code' 和 'market' 兩個鍵
            if "code" not in code_dict or "market" not in code_dict:
                raise ValueError("每個字典必須包含 'code' 和 'market' 兩個鍵")
            
            # 確認 'code' 和 'market' 是否為字串
            if not isinstance(code_dict["code"], str) or not isinstance(code_dict["market"], str):
                raise ValueError("`code` 和 `market` 必須是字串")
            
            # 確認 'market' 的值是否為 'Stock' 或 'Future'
            if code_dict["market"] not in ["Stock", "Future"]:
                raise ValueError("`market` 必須是 'Stock' 或 'Future'")
        
        return values

class BaseBackfilling(BaseQuote):
    """回補即時行情基本資料
    """
    backfill_start_from: str = Field(..., title="回補起始時間")
    backfill_end_to: str = Field(..., title="回補結束時間")

    @model_validator(mode='before')
    def set_default(cls, values):
        if values.get("backfill_start_from") and values.get("backfill_end_to"):
            return values
        elif not values.get("backfill_start_from") and not values.get("backfill_end_to"):
            values["backfill_start_from"] = datetime.now().strftime("%Y-%m-%d")
            values["backfill_end_to"] = datetime.now().strftime("%Y-%m-%d")
        else:
            new_start_from = values.get("backfill_start_from") or values.get("backfill_end_to")
            new_end_to = values.get("backfill_end_to") or values.get("backfill_start_from")
            
            values["backfill_start_from"] = new_start_from
            values["backfill_end_to"] = new_end_to
        
        return values