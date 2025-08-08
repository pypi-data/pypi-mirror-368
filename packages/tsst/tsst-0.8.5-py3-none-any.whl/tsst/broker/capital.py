import os
import polars as pl

import comtypes.client
comtypes.client.GetModule(os.getenv("SKCOM_DLL_PATH"))
import comtypes.gen.SKCOMLib as sk

from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Literal, List
from tsst.broker import BaseBroker, QuoteManager
from tsst.constant import Action, OperationType, OrderCond, OrderLot, OrderType, PriceType, OCType
from tsst.event import get_event, Event
from tsst.system_code import SuccessCode, ErrorCode
from tsst.utils import format_tick_data

SYSTEM_EVENT = get_event("system")
QUOTE_EVENT = get_event("quote")
TRADE_EVENT = get_event("trade")

def get_timestamp(lDate: int, lTimehms: int, lTimemillismicros: int) -> float:
    """
        取得時間戳

        Args:
            lDate (int): 日期
            lTimehms (int): 時間
            lTimemillismicros (int): 毫秒

        Returns:
            float: 時間戳
    """
    year = lDate // 10000
    month = (lDate % 10000) // 100
    day = lDate % 100

    hour = lTimehms // 10000
    minute = (lTimehms % 10000) // 100
    second = lTimehms % 100

    microsecond = lTimemillismicros

    dt = datetime(year, month, day, hour, minute, second, microsecond)

    return dt.timestamp()

class CapitalOrderResponseNormalizerMixin:
    """群益回報格式化的 Mixin
    """
    def normalize_operation_type(self, value: str) -> str:
        """格式化群益回傳的操作類型

        Args:
            value (str): 群益回傳的操作類型
        
        Returns:
            str: 格式化後的操作類型
        """
        if value == "N":
            return OperationType.NEW.value
        elif value == "C":
            return OperationType.CANCEL.value
        elif value == "U":
            return OperationType.UPDATE_QTY.value
        elif value == "P":
            return OperationType.UPDATE_PRICE.value
        elif value == "D":
            return OperationType.DEAL.value
        elif value == "B":
            return OperationType.UPDATE_PRICE_QTY.value
        elif value == "S":
            return OperationType.DYNAMIC_CANCEL.value
        else:
            return value

    def normalize_action(self, value: str) -> str:
        """格式化群益回傳的操作類型

        Args:
            value (str): 群益回傳的操作類型
        
        Returns:
            str: 格式化後的操作類型
        """
        if value == "B":
            return Action.BUY.value
        elif value == "S":
            return Action.SELL.value
        else:
            return value

    def normalize_order_type(self, value: str) -> str:
        """格式化群益回傳的委託類型

        Args:
            value (str): 群益回傳的委託類型
        
        Returns:
            str: 格式化後的委託類型
        """
        if value == "R":
            return OrderType.ROD.value
        elif value == "I":
            return OrderType.IOC.value
        elif value == "F":
            return OrderType.FOK.value
        else:
            return value

    def normalize_order_cond(self, value: str) -> str:
        """格式化群益回傳的委託條件

        Args:
            value (str): 群益回傳的委託條件
        
        Returns:
            str: 格式化後的委託條件
        """
        if value == "00" or value == "20":
            # 00 現股, 20 零股
            return OrderCond.CASH.value
        elif value == "03":
            return OrderCond.MARGIN_T.value
        elif value == "04":
            return OrderCond.SHORT_S.value
        else:
            return value
    
    def normalize_price_type(self, value: str) -> str:
        """格式化群益回傳的價格類型

        Args:
            value (str): 群益回傳的價格類型
        
        Returns:
            str: 格式化後的價格類型
        """
        if value == "1":
            return PriceType.MKT.value
        elif value == "2":
            return PriceType.LMT.value
        elif value == "3":
            return PriceType.MKP.value
        else:
            return value

    def normalize_octype(self, value: str) -> str:
        """格式化群益回傳的期貨開倉或平倉類型

        Args:
            value (str): 群益回傳的期貨開倉或平倉類型
        
        Returns:
            str: 格式化後的期貨開倉或平倉類型
        """
        if value == "Y":
            return OCType.DAY_TRADE.value
        elif value == "N":
            return OCType.NEW.value
        elif value == "O":
            return OCType.COVER.value
        else:
            return value

    def normalize_stock_order_response(self, data_lst: list) -> Dict[str, Any]:
        """格式化群益回傳的委託回報格式

        Args:
            data (list): 群益回傳的委託回報資料
        
        Returns:
            Dict[str, Any]: 格式化後的委託回報格式
        """
        op_code = SuccessCode.CreateOrderSuccess.value if data_lst[3] == "N" else ErrorCode.ReceiveStockOrderError.value
        op_message = data_lst[44] if op_code == SuccessCode.CreateOrderSuccess.value else ""

        if data_lst[1] == "TL": # 盤後零股
            order_lot = OrderLot.ODD.value
        elif data_lst[1] == "TC": # 盤中零股
            order_lot = OrderLot.INTRADAY_ODD.value
        elif data_lst[1] == "TA": # 盤後
            order_lot = OrderLot.FIXING.value
        else: # 整股
            order_lot = OrderLot.COMMON.value
        
        exchange_ts = datetime.strptime(f"{data_lst[23]} {data_lst[24]}", "%Y%m%d %H:%M:%S").timestamp()

        return {
            "operation_type": self.normalize_operation_type(data_lst[2]),
            "operation_status_code": op_code,
            "operation_message": op_message,
            "order": {
                "id": data_lst[0],
                "seqno": data_lst[0],
                "ordno": data_lst[10],
                "account": data_lst[5],
                "code": data_lst[8],
                "action": self.normalize_action(data_lst[6][0]),
                "price": Decimal(data_lst[11]),
                "quantity": int(data_lst[20]),
                "order_type": self.normalize_order_type(data_lst[6][3]),
                "order_cond": self.normalize_order_cond(data_lst[6][1:3]),
                "order_lot": order_lot,
                "price_type": self.normalize_price_type(data_lst[6][4]),
            },
            "trade_status": {
                "id": data_lst[0],
                "exchange": data_lst[7],
                "exchange_ts": exchange_ts
            },
        }

    def normalize_future_order_response(self, data_lst: list) -> Dict[str, Any]:
        """格式化群益回傳的期貨委託回報格式

        Args:
            data (list): 群益回傳的委託回報資料
        
        Returns:
            Dict[str, Any]: 格式化後的委託回報格式
        """
        op_code = SuccessCode.CreateOrderSuccess.value if data_lst[3] == "N" else ErrorCode.ReceiveStockOrderError.value
        op_message = data_lst[44] if op_code == SuccessCode.CreateOrderSuccess.value else ""

        exchange_ts = datetime.strptime(f"{data_lst[23]} {data_lst[24]}", "%Y%m%d %H:%M:%S").timestamp()

        # @TODO combo 是否為組合單 等群益做好後再看怎麼加上
        return {
            "operation_type": self.normalize_operation_type(data_lst[2]),
            "operation_status_code": op_code,
            "operation_message": op_message,
            "order": {
                "id": data_lst[0],
                "seqno": data_lst[0],
                "ordno": data_lst[10],
                "account": data_lst[5],
                "code": data_lst[8],
                "action": self.normalize_action(data_lst[6][0]),
                "price": Decimal(data_lst[11]),
                "quantity": int(data_lst[20]),
                "order_type": self.normalize_order_type(data_lst[6][2]),
                "oc_type": self.normalize_octype(data_lst[6][1]),
                "price_type": self.normalize_price_type(data_lst[6][3]),
            },
            "trade_status": {
                "id": data_lst[0],
                "exchange": data_lst[7],
                "exchange_ts": exchange_ts
            },
        }

    def normalize_stock_deal_response(self, data_lst: list) -> Dict[str, Any]:
        """格式化群益回傳的證券成交回報格式
        
        Args:
            data (list): 群益回傳的成交回報資料
        
        Returns:
            Dict[str, Any]: 格式化後的成交回報格式
        """
        if data_lst[1] == "TL": # 盤後零股
            order_lot = OrderLot.ODD.value
        elif data_lst[1] == "TC": # 盤中零股
            order_lot = OrderLot.INTRADAY_ODD.value
        elif data_lst[1] == "TA": # 盤後
            order_lot = OrderLot.FIXING.value
        else: # 整股
            order_lot = OrderLot.COMMON.value
        
        exchange_ts = datetime.strptime(f"{data_lst[23]} {data_lst[24]}", "%Y%m%d %H:%M:%S").timestamp()

        return {
            "id": data_lst[0],
            "seqno": data_lst[0],
            "ordno": data_lst[0],
            "exchange_seqno": data_lst[38],
            "broker_id": data_lst[4],
            "account": data_lst[5],
            "action": self.normalize_action(data_lst[6][0]),
            "code": data_lst[8],
            "quantity": int(data_lst[20]),
            "price": Decimal(data_lst[11]),
            "order_cond": self.normalize_order_cond(data_lst[6][1:3]),
            "order_lot": order_lot,
            "exchange_ts": exchange_ts
        }

    def normalize_future_deal_response(self, data_lst: list) -> Dict[str, Any]:
        """格式化群益回傳的期貨成交回報格式

        Args:
            data (list): 群益回傳的成交回報資料
        
        Returns:
            Dict[str, Any]: 格式化後的成交回報格式
        """
        exchange_ts = datetime.strptime(f"{data_lst[23]} {data_lst[24]}", "%Y%m%d %H:%M:%S").timestamp()
        
        return {
            "id": data_lst[0],
            "seqno": data_lst[0],
            "ordno": data_lst[0],
            "exchange_seqno": data_lst[38],
            "broker_id": data_lst[4],
            "account": data_lst[5],
            "action": self.normalize_action(data_lst[6][0]),
            "code": data_lst[8],
            "quantity": int(data_lst[20]),
            "price": Decimal(data_lst[11]),
            "exchange_ts": exchange_ts
        }

class CapitalSystemMixin:
    """針對群益 API 的 Mixin
    """
    def OnTimer(self, nTime: int):
        """定時Timer通知。每分鐘會由該函式得到一個時間。

        Args:
            nTime (int): 群益的函式庫回傳的時間
        """
        msg = "【OnTimer】" + str(nTime)

        SYSTEM_EVENT.send(Event.ON_SYSTEM, response={"message": msg})

    def OnShowAgreement(self, bstrData: str):
        """群益同意書狀態通知。

        Args:
            bstrData (str): 群益的函式庫回傳的資料
        """
        msg = "【OnShowAgreement】" + bstrData
        
        SYSTEM_EVENT.send(Event.ON_SYSTEM, response={"message": msg})

    def OnConnection(self, nKind, nCode):
        msg = "【OnConnection】" + str(nKind) + " 代碼:" + str(nCode)
        
        SYSTEM_EVENT.send(Event.ON_SYSTEM, response={"message": msg})

    def OnNotifyServerTime(self, sHour, sMinute, sSecond, nTotal):
        msg = "【OnNotifyServerTime】" + str(sHour) + ":" + str(sMinute) + ":" + str(sSecond) + "總秒數:" + str(nTotal)
        
        SYSTEM_EVENT.send(Event.ON_SYSTEM, response={"message": msg})

class CapitalOrderMixin:
    """針對群益下單的 Mixin
    """
    def OnAccount(self, bstrLogInID: str, bstrAccountData: str):
        """帳號回報事件

        Args:
            bstrLogInID (str): 群益回傳的使用者 ID
            bstrAccountData (str): 群益函式庫回傳的帳號資料
        """
        SYSTEM_EVENT.send(Event.ON_RECEIVE_ACCOUNT, account=bstrAccountData, login_id=bstrLogInID)

class CapitalReplyMixin(CapitalOrderResponseNormalizerMixin):
    """針對群益回報的 Mixin
    """
    def OnReplyMessage(self, bstrUserID: str, bstrMessages: str):
        """群益訊息回覆事件

        Args:
            bstrUserID (str): 群益回傳的使用者 ID
            bstrMessages (str): 群益函式庫回傳的訊息
        """
        msg = "【註冊公告OnReplyMessage】" + bstrUserID + "_" + bstrMessages

        SYSTEM_EVENT.send(Event.ON_SYSTEM, response={"message": msg})

        # 群益要求回傳 -1
        return -1

    def OnNewData(self, bstrUserID, bstrData):
        """群益接收回報的事件，包含委託回報、成交回報、其他回報

        Args:
            bstrUserID (str): 群益回傳的使用者 ID
            bstrMessages (str): 群益函式庫回傳的訊息
        """
        values = bstrData.split(",")
        
        if values[1] == "TS":
            if values[2] == "D":
                normalize_data = CapitalOrderResponseNormalizerMixin.normalize_stock_order_response(self, values)
                normalize_data["product_type"] = "Stock"
                event = Event.ON_DEAL
            elif values[2] == "N":
                normalize_data = CapitalOrderResponseNormalizerMixin.normalize_stock_order_response(self, values)
                normalize_data["product_type"] = "Stock"
                event = Event.ON_ORDER
            else:
                normalize_data = {"data": bstrData}
                event = Event.ON_REPLY
        elif values[1] == "TF":
            if values[2] == "D":
                normalize_data = CapitalOrderResponseNormalizerMixin.normalize_future_deal_response(self, values)
                normalize_data["product_type"] = "Future"
                event = Event.ON_DEAL
            elif values[2] == "N":
                normalize_data = CapitalOrderResponseNormalizerMixin.normalize_future_order_response(self, values)
                normalize_data["product_type"] = "Future"
                event = Event.ON_ORDER
            else:
                normalize_data = {"data": bstrData}
                event = Event.ON_REPLY
        else:
            normalize_data = {"data": bstrData}
            event = Event.ON_REPLY

        TRADE_EVENT.send(event, response=normalize_data)
        
        return -1

class CapitalQuoteMixin:
    """針對群益報價的 Mixin
    """
    @property
    def quote_manager(self):
        """取得報價管理器
        """
        raise NotImplementedError("You must implement the quote_manager property.")

    @property
    def m_pSKQuote(self):
        """取得群益報價函式庫
        """
        raise NotImplementedError("You must implement the m_pSKQuote property.")

    def OnNotifyTicksLONG(self, sMarketNo, nStockidx, nPtr, lDate, lTimehms, lTimemillismicros, nBid, nAsk, nClose, nQty, nSimulate):
        """
            這是市場報價 SKQuoteLib_RequestTicks 的回傳事件
        """
        if sMarketNo == 0:
            event_name = Event.ON_STOCK_TICK
        elif sMarketNo == 2:
            event_name = Event.ON_FUTURE_TICK
        else:
            event_name = Event.ON_TICK

        # 透過市場與商品代號取得商品資訊
        product = self.m_pSKQuote.SKQuoteLib_GetStockByIndexLONG(sMarketNo, nStockidx)

        if (nClose / 100) > nBid:
            tick_type = 2 # 外盤
        elif (nClose / 100) < nBid:
            tick_type = 2 # 內盤
        else:
            tick_type = 0 # 無法判定

        if sMarketNo in (2, 3):
            market_type = "Future"
        else:
            market_type = "Stock"

        tick_data = format_tick_data(
            timestamp = get_timestamp(lDate, lTimehms, lTimemillismicros),
            market_type = market_type,
            code = product[0].bstrStockNo,
            close = nClose / 100,
            qty = nQty,
            tick_type = tick_type,
            is_simulate = nSimulate
        )

        self.quote_manager.add_tick(tick_data)
        QUOTE_EVENT.send(event_name, response=tick_data)

class CapitalEventHandler(BaseBroker, CapitalSystemMixin, CapitalOrderMixin, CapitalReplyMixin, CapitalQuoteMixin):
    """群益事件處理器。
    """
    def __init__(self):
        self.sk = sk

        self._quote_manager = QuoteManager()
        self.init_handler()

    def init_handler(self):
        """初始化群益事件處理器。
        """
        self._m_pSKCenter = comtypes.client.CreateObject(sk.SKCenterLib,interface=sk.ISKCenterLib)
        self.SKCenterEventHandler = comtypes.client.GetEvents(self.m_pSKCenter, self)

        self._m_pSKOrder = comtypes.client.CreateObject(sk.SKOrderLib,interface=sk.ISKOrderLib)
        self.SKOrderLibEventHandler = comtypes.client.GetEvents(self.m_pSKOrder, self)

        self._m_pSKReply = comtypes.client.CreateObject(sk.SKReplyLib,interface=sk.ISKReplyLib)
        self.SKReplyLibEventHandler = comtypes.client.GetEvents(self.m_pSKReply, self)
        
        self._m_pSKQuote = comtypes.client.CreateObject(sk.SKQuoteLib,interface=sk.ISKQuoteLib)
        self.SKQuoteLibEventHandler = comtypes.client.GetEvents(self.m_pSKQuote, self)
    
    @property
    def m_pSKCenter(self):
        """取得群益中心函式庫
        """
        return self._m_pSKCenter

    @property
    def m_pSKOrder(self):
        """取得群益委託函式庫
        """
        return self._m_pSKOrder
    
    @property
    def m_pSKReply(self):
        """取得群益回覆函式庫
        """
        return self._m_pSKReply
    
    @property
    def m_pSKQuote(self):
        """取得群益報價函式庫

        Returns:
            sk.SKQuoteLib: 群益報價函式庫
        """
        return self._m_pSKQuote

    @property
    def quote_manager(self):
        """取得報價管理器

        Returns:
            QuoteManager: 報價管理器
        """
        return self._quote_manager
    
    def get_kbar(self, code: str, unit: Literal["m", "h", "d", "w", "mo", "q", "y"], freq: int, exprs: List[pl.Expr] = [], to_pandas_df: bool = False) -> pl.DataFrame:
        """取得 K 線資料

        Args:
            code (str): 商品代號
            unit (Literal["m", "h", "d", "w", "mo", "q", "y"]): K 線頻率單位
            freq (int): 頻率
            exprs (List[pl.Expr], optional): 需要計算的指標. Defaults to [].
            to_pandas_df (bool, optional): 是否轉換成 pandas DataFrame. Defaults to False.
        
        Returns:
            pl.DataFrame: K 線資料
        """
        return self.quote_manager.get_kbar(code, unit, freq, exprs, to_pandas_df=to_pandas_df)
    
handler = CapitalEventHandler()
