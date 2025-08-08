from typing import Dict, Literal, Any
from tsst.broker.capital import handler
from tsst.trade.order.base import BaseOrder
from tsst.trade.order.capital.validate import CapitalCreateStockOrder, CapitalCreateFutureOrder
from tsst.system_code import SuccessCode, ErrorCode
from tsst.event import get_event, Event, SystemEventListener
from tsst.error import MarketCodeNotFound
from tsst.utils import get_response, log_message

SYSTEM_EVENT = get_event("system")
TRADE_EVENT = get_event("trade")

class CapitalOrder(BaseOrder, SystemEventListener):
    """群益下單模組
    """
    def __init__(self, obj, **kwargs):
        """初始化群益下單模組

        Args:
            obj (CapitalLogin): TSST Login
        """
        super().__init__(**kwargs)
        self.api = obj

        self.__bind_event()

    def __bind_event(self):
        """綁定事件
        """
        SYSTEM_EVENT.connect_via(Event.ON_SYSTEM)(self.on_system)

    def __make_order(self, code: str, market: Literal["Stock", "Future"], params: Dict):
        """
            建立群益下單物件

            Args:
                code (str): 商品代號
                market (Literal["Stock", "Future"]): 市場別
                params (Dict): 下單參數

            Returns:
                sk.STOCKORDER: 群益下單物件
        """
        if market == "Stock":
            model = CapitalCreateStockOrder(**params)
            
            try:
                account = self.api.main_stock_account
            except Exception as e:
                log_message(f"群益失敗 {str(e)}", "broker", "error")
                raise e
            
        elif market == "Future":
            model = CapitalCreateFutureOrder(**params)

            try:
                account = self.api.main_future_account
            except Exception as e:
                log_message(f"群益失敗 {str(e)}", "broker", "error")
                raise e
        else:
            raise MarketCodeNotFound(market)

        __params = model.to_capital_dict()
        __params["bstrFullAccount"] = account.source["account"]
        __params["bstrStockNo"] = code

        if market == "Stock":
            pOrder = handler.sk.STOCKORDER()
        else:
            pOrder = handler.sk.FUTUREORDER()

        for key, value in __params.items():
            setattr(pOrder, key, value)
        
        return pOrder
    
    def create_order(self, code: str, product_type: Literal["Stock", "Future"], params: Dict) -> Dict[str, Any]:
        """下單

        Args:
            code (str): 商品代號
            product_type (Literal["Stock", "Future"]): 商品類型
            params (Dict): 下單參數
        
        Returns:
            Dict[str, Any]: 回傳結果
        """
        pOrder = self.__make_order(code, product_type, params)
        
        async_mode = False

        if product_type == "Stock":
            try:
                bstrLoginId = self.api.main_stock_account.source["login_id"]
            except Exception as e:
                log_message(f"群益失敗 {str(e)}", "broker", "error")
                raise e
            
            bstrMessage, nCode = handler.m_pSKOrder.SendStockOrder(bstrLoginId, async_mode, pOrder)

        elif product_type == "Future":
            try:
                bstrLoginId = self.api.main_future_account.source["login_id"]
            except Exception as e:
                log_message(f"群益失敗 {str(e)}", "broker", "error")
                raise e
            
            bstrMessage, nCode = handler.m_pSKOrder.SendFutureOrderCLR(bstrLoginId, async_mode, pOrder)
        
        else:
            MarketCodeNotFound(product_type)

        msg = "【SendStockOrder】" + handler.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode) + bstrMessage
        
        SYSTEM_EVENT.send(Event.ON_SYSTEM, response=msg)

        if nCode == 0:
            # 設定要傳回回報的帳號
            handler.m_pSKReply.SKReplyLib_ConnectByID(bstrLoginId)
            return get_response(SuccessCode.CreateOrderSuccess.code)
        else:
            return get_response(ErrorCode.CreateOrderError.code, msg)

    def modify_order(self, id: str, product_type: Literal["Stock", "Future"], price: float = None, quantity: int = None, **kwargs) -> Dict[str, Any]:
        """改單

        Args:
            id (str): 交易編號
            product_type (Literal["Stock", "Future"]): 商品類型
            price (float): 要修改的價格, default=None
            quantity (int): 要刪除的數量, default=None

        Returns:
            Dict[str, Any]: 改單操作結果
        """
        async_mode = False

        if product_type == "Stock":

            try:
                bstrLoginId = self.api.main_stock_account.source["login_id"]
                account = self.api.main_stock_account.source["account"]
            except Exception as e:
                log_message(f"群益失敗 {str(e)}", "broker", "error")
                raise e
            
        elif product_type == "Future":

            try:
                bstrLoginId = self.api.main_future_account.source["login_id"]
                account = self.api.main_future_account.source["account"]
            except Exception as e:
                log_message(f"群益失敗 {str(e)}", "broker", "error")
                raise e
            
        else:
            raise MarketCodeNotFound(product_type)

        if price is not None:
            capital_response = handler.m_pSKOrder.CorrectPriceBySeqNo(
                bAsyncOrder=async_mode,
                bstrLogInID=bstrLoginId,
                bstrAccount=account,
                bstrSeqNo=id,
                bstrPrice=str(price),
                nTradeType=0
            )

            if capital_response != 0:
                return get_response(ErrorCode.ModifyPriceError.code, "改價錯誤")
        
        if quantity is not None:
            capital_response = handler.m_pSKOrder.DecreaseOrderBySeqNo(
                bAsyncOrder=async_mode,
                bstrLogInID=bstrLoginId,
                bstrAccount=account,
                bstrSeqNo=id,
                nDecreaseQty=str(quantity)
            )

            if capital_response != 0:
                return get_response(ErrorCode.ModifyQuantityError.code, "改量錯誤")
        
        return get_response(SuccessCode.ModifyOrderSuccess.code)
    
    def cancel_order(self, id: str, product_type: Literal["Stock", "Future"], **kwargs) -> Dict[str, Any]:
        """刪單

        Args:
            id (str): 交易編號
            product_type (Literal["Stock", "Future"]): 商品類型

        Returns:
            Dict[str, Any]: 刪單操作結果
        """
        async_mode = False

        if product_type == "Stock":

            try:
                bstrLoginId = self.api.main_stock_account.source["login_id"]
                account = self.api.main_stock_account.source["account"]
            except Exception as e:
                log_message(f"群益失敗 {str(e)}", "broker", "error")
                raise e
            
        elif product_type == "Future":

            try:
                bstrLoginId = self.api.main_future_account.source["login_id"]
                account = self.api.main_future_account.source["account"]
            except Exception as e:
                log_message(f"群益失敗 {str(e)}", "broker", "error")
                raise e

        else:
            raise MarketCodeNotFound(product_type)
        
        capital_response = handler.m_pSKOrder.CancelOrderBySeqNo(
            bAsyncOrder=async_mode,
            bstrLogInID=bstrLoginId,
            bstrAccount=account,
            bstrSeqNo=id
        )

        if capital_response != 0:
            return get_response(ErrorCode.CancelOrderError.code, "刪單錯誤")
        
        return get_response(SuccessCode.CancelOrderSuccess.code)




