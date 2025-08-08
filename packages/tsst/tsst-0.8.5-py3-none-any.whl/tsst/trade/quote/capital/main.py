import polars as pl

from typing import Dict, Literal, List
from tsst.broker.capital import handler
from tsst.trade.quote.base import BaseQuote
from tsst.trade.quote.capital.validate import CapitalQuoteValidate, CapitalBackfilling
from tsst.system_code import SuccessCode
from tsst.event import get_event, Event, QuoteEventListener, SystemEventListener
from tsst.error import SubscribeFailed
from tsst.utils import console, get_response, pump_event_loop, log_message

SYSTEM_EVENT = get_event("system")
QUOTE_EVENT = get_event("quote")

class CapitalQuote(BaseQuote, QuoteEventListener, SystemEventListener):
    """
    群益報價模組的主要類別
    """
    def __init__(self, obj, **kwargs):
        """初始化群益報價模組

        Args:
            obj (CapitalLogin): TSST Login
        """
        super().__init__(**kwargs)
        self.api = obj
        self.bsPageNo = 0

    def __bind_event(self):
        """綁定事件
        """
        QUOTE_EVENT.connect_via(Event.ON_STOCK_TICK)(self.on_stock_tick)
        QUOTE_EVENT.connect_via(Event.ON_FUTURE_TICK)(self.on_future_tick)

    def __connect_quote_server(self):
        """
        連線群益報價主機
        """
        status = handler.m_pSKQuote.SKQuoteLib_IsConnected()

        # 0 => 斷線
        # 1 => 連線中
        # 2 => 下載中
        if status == 1:
            return

        nCode = handler.m_pSKQuote.SKQuoteLib_EnterMonitorLONG()
        while (status := handler.m_pSKQuote.SKQuoteLib_IsConnected()) != 1:
            print(f"群益API連線狀態: {status} 尚未連線成功...", flush=True, end="\r")

            # 群益 API 是基於 window event loop 執行的
            # 當使用 while 迴圈時必須要使用 pythoncom 的 pythoncom.PumpWaitingMessages() 來推動
            # 否則將不會取得任何更新
            pump_event_loop()

        if nCode != 0:
            log_message("【SKQuoteLib_EnterMonitorLONG】" + handler.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode), "ERROR")
        else:
            log_message("【SKQuoteLib_EnterMonitorLONG】" + handler.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode))

    def __get_ps_page_no(self, code: str) -> int:
        """
            群益的每一個訂閱都必須要指定一個獨一的編號用以區分不同的訂閱

            Args:
                code (str): 商品代號
            
            Returns:
                int: 編號
        """
        self.bsPageNo += 1

        return self.bsPageNo

    def backfilling(self, params: Dict[str, str], **kwargs):
        """群益當日報價回補

        Args:
            params (Dict[str, str]): 參數
        """
        console.print("TSST 尚未提供群益 API 當日報價回補功能", style="bold red")

    def subscribe(self, params: Dict[str, str], **kwargs) -> Dict[str, str]:
        """訂閱群益報價

        Args:
            params (Dict[str, str]): 參數
        
        Returns:
            Dict[str, str]: 回傳結果
        """
        try:
            model = CapitalQuoteValidate(**params)
        except Exception as e:
            raise SubscribeFailed
        
        # 連線至群益報價主機
        self.__connect_quote_server()

        summary = {
            "success": 0,
            "failed": 0,
            "errors": []
        }

        for code in model.codes:
            psPageNo, nCode= handler.m_pSKQuote.SKQuoteLib_RequestTicks(self.__get_ps_page_no(code["code"]), code["code"])
            msg = f"【SKQuoteLib_RequestStocks】【psPageNo {psPageNo}】" + handler.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)

            if nCode == 0:
                summary["success"] += 1
            else:
                summary["failed"] += 1
                summary["errors"].append(msg)

            log_message(msg)
            log_message(f"訂閱即時資料 產品類型:{code['market']} 產品代號:{code['code']}")

        if summary["failed"] == 0 and summary["success"] > 0:
            system_message = "訂閱成功"
        elif summary["success"] == 0 and summary["failed"] > 0:
            system_message = "沒有商品被訂閱"
        else:
            system_message = "部分商品訂閱成功, 請查看回傳訊息"

        SYSTEM_EVENT.send(Event.ON_SYSTEM, response=get_response(SuccessCode.FetchMarketLiveSuccess.code, system_message))

        return get_response(SuccessCode.FetchMarketLiveSuccess.code, summary)

    def unsubscribe(self, params: Dict[str, str], **kwargs) -> Dict[str, str]:
        """取消訂閱群益報價

        Args:
            params (Dict[str, str]): 參數
        
        Returns:
            Dict[str, str]: 回傳結果
        """
        try:
            model = CapitalQuoteValidate(**params)
        except Exception as e:
            raise SubscribeFailed
        
        # 連線至群益報價主機
        self.__connect_quote_server()

        summary = {
            "success": 0,
            "failed": 0,
            "errors": []
        }

        for code in model.codes:
            nCode= handler.m_pSKQuote.SKQuoteLib_CancelRequestTicks(code["code"])
            msg = f"【SKQuoteLib_CancelRequestTicks】" + handler.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)

            if nCode == 0:
                summary["success"] += 1
            else:
                summary["failed"] += 1
                summary["errors"].append(msg)

            log_message(msg)
            log_message(f"取消訂閱即時資料 產品類型:{code['market']} 產品代號:{code['code']}")

        if summary["failed"] == 0 and summary["success"] > 0:
            system_message = "取消訂閱成功"
        elif summary["success"] == 0 and summary["failed"] > 0:
            system_message = "沒有商品被取消訂閱"
        else:
            system_message = "部分商品取消訂閱成功, 請查看回傳訊息"

        SYSTEM_EVENT.send(Event.ON_SYSTEM, response=get_response(SuccessCode.CancelMarketLiveSuccess.code, system_message))

        return get_response(SuccessCode.CancelMarketLiveSuccess.code, summary)

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
        return handler.get_kbar(code, unit, freq, exprs, to_pandas_df)
