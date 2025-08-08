import shioaji as sj

from typing import Dict, Literal, Any
from tsst.broker.sino import SinoMixin
from tsst.trade.order.base import BaseOrder
from tsst.trade.order.sino.validate import SinoCreateStockOrder, SinoCreateFutureOrder
from tsst.system_code import SuccessCode, ErrorCode
from tsst.event import get_event, Event, TradeEventListener
from tsst.error import MarketCodeNotFound
from tsst.utils import get_response, log_message

SYSTEM_EVENT = get_event("system")
TRADE_EVENT = get_event("trade")

class SinoOrder(BaseOrder, SinoMixin, TradeEventListener):
    """永豐下單模組
    """
    def __init__(self, obj, **kwargs):
        """初始化永豐下單模組

        Args:
            obj (SinoLogin): TSST Login
        """
        super().__init__(**kwargs)
        self.login_obj = obj
        self.api = obj.api

        # 用來記錄 trade_id 與 Trade 物件的對應關係
        self.trade_mapper = {}

        self.__bind_event()
    
    def __bind_event(self):
        """綁定事件
        """
        self.api.set_order_callback(self.__on_order_callback)

        TRADE_EVENT.connect_via(Event.ON_ORDER, self.on_order)
        TRADE_EVENT.connect_via(Event.ON_DEAL, self.on_deal)
    
    def __make_order(self, market: Literal["Stock", "Future"], params: Dict):
        """建立永豐下單物件

        Args:
            market (Literal["Stock", "Future"]): 市場別
            params (Dict): 下單參數

        Returns:
            sj.orders.Order: 永豐下單物件
        """
        __params = {}

        if market == "Stock":
            model = SinoCreateStockOrder(**params)
            
            __params["daytrade_short"] = model.daytrade_short
            __params["price_type"] = sj.constant.StockPriceType[model.price_type]
            __params["order_cond"] = sj.constant.StockOrderCond[model.order_cond]
            __params["order_lot"] = sj.constant.StockOrderLot[model.order_lot]
        elif market == "Future":
            model = SinoCreateFutureOrder(**params)

            __params["price_type"]  = sj.constant.FuturesPriceType[model.price_type]
            __params["octype"] = sj.constant.FuturesOCType[model.octype]
        else:
            raise MarketCodeNotFound(market)
        
        __params["action"] = sj.constant.Action[model.action]
        __params["order_type"] = sj.constant.OrderType[model.order_type]
        __params["quantity"] = model.quantity
        __params["price"] = model.price

        # 如果有指定下單帳戶, 則查詢對應的帳務物件
        if model.account:
            use_source_account = self.login_obj.get_source_account(model.account, market)

            __params["account"] = use_source_account

        try:
            order = self.api.Order(**__params)
        except Exception as e:
            log_message(f"永豐下單失敗 {str(e)}", "broker", "error")
            raise e

        return order
    
    def __on_order_callback(self, stat, msg):
        """接收永豐委託或成交回報

        Args:
            stat (sj.constant.OrderState, sj.constant.OrderState.StockDeal): 委託或成交回報
            msg (_type_): 交易訊息
        """
        if stat == sj.constant.OrderState.StockOrder:
            TRADE_EVENT.send(Event.ON_ORDER, response=self.to_standard_stock_order_response(msg))
        elif stat == sj.constant.OrderState.FuturesOrder:
            TRADE_EVENT.send(Event.ON_ORDER, response=self.to_standard_future_order_response(msg))
        elif stat == sj.constant.OrderState.StockDeal:
            TRADE_EVENT.send(Event.ON_DEAL, response=self.to_standard_stock_deal_response(msg))
        elif stat == sj.constant.OrderState.FuturesDeal:
            TRADE_EVENT.send(Event.ON_DEAL, response=self.to_standard_future_deal_response(msg))

    def create_order(self, code: str, product_type: Literal["Stock", "Future"], params: Dict) -> Dict[str, Any]:
        """下單

        Args:
            code (str): 商品代號
            product_type (Literal["Stock", "Future"]): 商品類型
            params (Dict): 下單參數
        
        Returns:
            Dict[str, Any]: 回傳結果
        """
        order = self.__make_order(product_type, params)
        contract = self.make_sino_contract_object(code, product_type)
        
        # @NOTE: 之前跑期貨策略時, 因為主動回報的關係, 這樣的做法會遇到資料來不及儲存, 導致在其他部分會需要先取得 Trade 的操作會失效
        # 之後可能要注意看看這邊的寫法是否會有問題
        try:
            trade = self.api.place_order(contract, order)
        except Exception as e:
            log_message(f"永豐下單失敗 {str(e)}", "broker", "error")
            raise e
        
        self.trade_mapper[trade.order.id] = trade

        return get_response(
            status_code=SuccessCode.CreateOrderSuccess.code,
            message="下單成功",
        )

    def modify_order(self, id: str, price: float = None, quantity: int = None, **kwargs) -> Dict[str, Any]:
        """改單

        Args:
            id (str): 交易編號
            price (float): 要修改的價格, default=None
            quantity (int): 要刪除的數量, default=None

        Returns:
            Dict[str, Any]: 改單操作結果
        """
        # 從 trade_mapper 中取得 Trade 物件
        trade = self.trade_mapper.get(id)

        if trade is None:
            return get_response(
                status_code=ErrorCode.TradeNotFound.code,
                message="交易編號不存在",
            )
        
        try:
            params = {}

            if price is not None:
                params["price"] = price
            
            if quantity is not None:
                params["qty"] = quantity

            trade = self.api.update_order(
                trade = trade,
                **params
            )
        except Exception as e:
            log_message(f"永豐改單失敗 {str(e)}", "broker", "error")
            raise e

        # 更新 trade_mapper
        self.trade_mapper[trade.order.id] = trade

        return get_response(
            status_code=SuccessCode.ModifyOrderSuccess.code,
            message="改單成功",
        )
    
    def cancel_order(self, id: str, **kwargs) -> Dict[str, Any]:
        """刪單
        
        Args:
            id (str): 交易編號
        
        Returns:
            Dict[str, Any]: 刪單操作結果
        """
        trade = self.trade_mapper.get(id)

        if trade is None:
            return get_response(
                status_code=ErrorCode.TradeNotFound.code,
                message="交易編號不存在",
            )
        
        try:
            trade = self.api.cancel_order(trade)
        except Exception as e:
            log_message(f"永豐刪單失敗 {str(e)}", "broker", "error")
            raise e

        # 更新 trade_mapper
        del self.trade_mapper[id]

        return get_response(
            status_code=SuccessCode.CancelOrderSuccess.code,
            message="刪單成功",
        )

