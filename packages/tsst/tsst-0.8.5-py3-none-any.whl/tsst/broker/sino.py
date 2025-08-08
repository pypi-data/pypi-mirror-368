import shioaji as sj

from typing import Dict, Any

import tsst
from tsst.broker import BaseBroker
import tsst.error
from tsst.system_code import SuccessCode, ErrorCode
from tsst.constant import OperationType, OrderCond, OrderLot, OrderType, PriceType, OCType

class SinoMixin(BaseBroker):
    """針對永豐 API 的 Mixin
    """
    def make_sino_contract_object(self, code: str, market_type: str) -> sj.contracts.Contract:
        """建立永豐用的商品物件

        Args:
            code (str): 商品代碼
            market_type (str): 市場別

        Returns:
            sj.contracts.Contract: 永豐商品物件
        """
        market_type = "Stocks" if market_type == "Stock" else "Futures"

        try:
            return getattr(self.api.Contracts, market_type)[code]
        except Exception:
            raise tsst.error.ProductCodeNotFound(code)
    
    def normalize_stock_order_response(self, data: Dict) -> Dict[str, Any]:
        """格式化永豐回傳的委託回報格式

        Args:
            data (Dict): 永豐的委託回報資料
        
        Returns:
            Dict[str, Any]: 格式化後的委託回報格式
        """
        op_code = SuccessCode.CreateOrderSuccess.code if data["operation"]["op_code"] == "00" else ErrorCode.ReceiveStockOrderError.code

        return {
            "operation_type": OperationType.from_value(data["operation"]["op_type"]),
            "operation_status_code": op_code,
            "operation_message": data["operation"]["op_msg"],
            "order": {
                "id": data["order"]["id"],
                "seqno": data["order"]["seqno"],
                "ordno": data["order"]["ordno"],
                "account": data["order"]["account"]["account_id"],
                "code": data["contract"]["code"],
                "action": data["order"]["action"],
                "price": data["order"]["price"],
                "quantity": data["order"]["quantity"],
                "order_type": OrderType.from_value(data["order"]["order_type"]),
                "order_cond": OrderCond.from_value(data["order"]["order_cond"]),
                "order_lot": OrderLot.from_value(data["order"]["order_lot"]),
                "price_type": PriceType.from_value(data["order"]["price_type"]),
            },
            "trade_status": {
                "id": data["status"]["id"],
                "exchange": data["contract"]["exchange"],
                "exchange_ts": data["status"]["exchange_ts"]
            },
        }

    def normalize_future_order_response(self, data: Dict) -> Dict[str, Any]:
        """格式化永豐回傳的期貨委託回報格式

        Args:
            data (Dict): 永豐的委託回報資料
        
        Returns:
            Dict[str, Any]: 格式化後的委託回報格式
        """
        op_code = SuccessCode.CreateOrderSuccess.code if data["operation"]["op_code"] == "00" else ErrorCode.ReceiveStockOrderError.code

        # @TODO combo 是否為組合單 等群益做好後再看怎麼加上
        return {
            "operation_type": OperationType.from_value(data["operation"]["op_type"]),
            "operation_status_code": op_code,
            "operation_message": data["operation"]["op_msg"],
            "order": {
                "id": data["order"]["id"],
                "seqno": data["order"]["seqno"],
                "ordno": data["order"]["ordno"],
                "account": data["order"]["account"]["account_id"],
                "code": data["contract"]["code"],
                "action": data["order"]["action"],
                "price": data["order"]["price"],
                "quantity": data["order"]["quantity"],
                "order_type": OrderType.from_value(data["order"]["order_type"]),
                "oc_type": OCType.from_value(data["order"]["oc_type"]),
                "price_type": PriceType.from_value(data["order"]["price_type"]),
            },
            "trade_status": {
                "id": data["status"]["id"],
                "exchange": data["contract"]["exchange"],
                "exchange_ts": data["status"]["exchange_ts"]
            },
        }

    def normalize_stock_deal_response(self, data: Dict) -> Dict[str, Any]:
        """格式化永豐回傳的證券成交回報格式

        Args:
            data (Dict): 永豐的成交回報資料
        
        Returns:
            Dict[str, Any]: 格式化後的成交回報格式
        """
        return {
            "id": data["trade_id"],
            "seqno": data["seqno"],
            "ordno": data["ordno"],
            "exchange_seqno": data["exchange_seq"],
            "broker_id": data["broker_id"],
            "account": data["account_id"],
            "action": data["action"],
            "code": data["code"],
            "quantity": data["quantity"],
            "price": data["price"],
            "order_cond": OrderCond.from_value(data["order_cond"]),
            "order_lot": OrderLot.from_value(data["order_lot"]),
            "exchange_ts": data["ts"]
        }

    def normalize_future_deal_response(self, data: Dict) -> Dict[str, Any]:
        """格式化永豐回傳的期貨成交回報格式

        Args:
            data (Dict): 永豐的成交回報資料
        
        Returns:
            Dict[str, Any]: 格式化後的成交回報格式
        """
        return {
            "id": data["trade_id"],
            "seqno": data["seqno"],
            "ordno": data["ordno"],
            "exchange_seqno": data["exchange_seq"],
            "broker_id": data["broker_id"],
            "account": data["account_id"],
            "action": data["action"],
            "code": data["code"],
            "quantity": data["quantity"],
            "price": data["price"],
            "exchange_ts": data["ts"]
        }

