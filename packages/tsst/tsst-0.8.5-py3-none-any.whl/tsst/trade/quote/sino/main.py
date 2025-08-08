import asyncio
import shioaji as sj
import polars as pl
import traceback

from datetime import timedelta
from typing import List, Dict, Literal
from tsst.broker import QuoteManager
from tsst.broker.sino import SinoMixin
from tsst.trade.quote.base import BaseQuote
from tsst.trade.quote.sino.validate import SinoQuoteValidate, SinoBackfilling
from tsst.system_code import SuccessCode
from tsst.event import get_event, Event, QuoteEventListener, SystemEventListener
from tsst.utils import format_tick_data, format_to_dt, format_sino_nano_ts_to_second_ts, get_response, log_message
from tsst.error import SubscribeFailed, BackFillingFailed

SYSTEM_EVENT = get_event("system")
QUOTE_EVENT = get_event("quote")

class SinoQuote(BaseQuote, SinoMixin, QuoteEventListener, SystemEventListener):
    """
    永豐報價模組的主要類別
    """
    def __init__(self, obj, **kwargs):
        """初始化永豐報價模組

        Args:
            obj (SinoLogin): TSST Login
        """
        super().__init__(**kwargs)
        self.api = obj.api
        self.quote_manager = QuoteManager()

        self.__bind_event()
    
    def __bind_event(self):
        """綁定事件
        """
        self.api.quote.set_on_tick_stk_v1_callback(self.__stock_quote_callback)
        self.api.quote.set_on_tick_fop_v1_callback(self.__future_quote_callback)

        QUOTE_EVENT.connect_via(Event.ON_STOCK_TICK)(self.on_stock_tick)
        QUOTE_EVENT.connect_via(Event.ON_FUTURE_TICK)(self.on_future_tick)

    def __stock_quote_callback(self, exchange: sj.Exchange, tick: sj.TickSTKv1):
        """接收永豐股票 Tick 資料

        Args:
            exchange (sj.Exchange): 交易所
            tick (sj.TickSTKv1): Tick 資料
        """
        tick_data = format_tick_data(
            timestamp = tick.datetime.timestamp(),
            market_type = "Stock",
            code = tick.code,
            close = tick.close,
            qty = tick.volume,
            tick_type = tick.tick_type,
            is_simulate = tick.simtrade
        )

        self.quote_manager.add_tick(tick_data)
        QUOTE_EVENT.send(Event.ON_STOCK_TICK, response=tick_data)
    
    def __future_quote_callback(self, exchange: sj.Exchange, tick: sj.TickFOPv1):
        """接收永豐期貨 Tick 資料

        Args:
            exchange (sj.Exchange): 交易所
            tick (sj.TickFOPv1): Tick 資料
        """
        tick_data = format_tick_data(
            timestamp = tick.datetime.timestamp(),
            market_type = "Future",
            code = tick.code,
            close = tick.close,
            qty = tick.volume,
            tick_type = tick.tick_type,
            is_simulate = tick.simtrade
        )

        self.quote_manager.add_tick(tick_data)
        QUOTE_EVENT.send(Event.ON_FUTURE_TICK, response=tick_data)

    def backfilling(self, params: Dict[str, str], **kwargs) -> Dict[str, str]:
        """
        ### 回補即時行情報價 (Tick)

        #### Args:
            params (Dict[str, str]): 參數
        
        #### Returns:
            Dict[str, str]: 回傳結果
        """
        try:
            model = SinoBackfilling(**params)
        except Exception as e:
            raise BackFillingFailed
        
        summary = {
            "success": 0,
            "failed": 0,
            "errors": []
        }

        for code in model.codes:
            try:
                contract = self.make_sino_contract_object(code["code"], code["market"])
                
                date = format_to_dt(model.backfill_start_from)
                end_date = format_to_dt(model.backfill_end_to)

                while date <= end_date:

                    try:
                        ticks = self.api.ticks(contract=contract, date=date.strftime("%Y-%m-%d"))
                        df = pl.DataFrame({**ticks})
                    except Exception as e:
                        log_message(f"永豐獲取歷史報價失敗 {str(e)}", "broker", "error")
                        raise e

                    for tick in df.iter_rows(named=True):
                        tick_data = format_tick_data(
                            timestamp = format_sino_nano_ts_to_second_ts(tick["ts"], 8),  # 永豐的 ts 是微秒
                            market_type = code["market"],
                            code = code["code"],
                            close = tick["close"],
                            qty = int(tick["volume"]),
                            tick_type = int(tick["tick_type"]),
                            is_simulate = 0,  # 永豐的回補資料沒有試搓資料
                            is_backfilling = True  # 標記為回補資料
                        )
                        self.quote_manager.add_tick(tick_data)

                    date += timedelta(days=1)

                summary["success"] += 1
            except Exception as e:
                summary["failed"] += 1
                summary["errors"].append(str(e))
        
        if summary["failed"] == 0 and summary["success"] > 0:
            system_message = "回補成功"
        elif summary["success"] == 0 and summary["failed"] > 0:
            system_message = "沒有商品被回補"
        else:
            system_message = "部分商品回補成功, 請查看回傳訊息"

        SYSTEM_EVENT.send(Event.ON_SYSTEM, response=get_response(SuccessCode.BackFillingSuccess.code, {"message": system_message, **summary}))

        return get_response(SuccessCode.BackFillingSuccess.code, summary)

    def subscribe(self, params: Dict[str, str], **kwargs) -> Dict[str, str]:
        """訂閱永豐報價

        Args:
            params (Dict[str, str]): 參數
        
        Returns:
            Dict[str, str]: 回傳結果
        """
        try:
            model = SinoQuoteValidate(**params)
        except Exception:
            raise SubscribeFailed

        summary = {
            "success": 0,
            "failed": 0,
            "errors": []
        }

        for code in model.codes:
            try:
                contract = self.make_sino_contract_object(code["code"], code["market"])

                try:
                    self.api.quote.subscribe(
                        contract = contract
                    )
                except Exception as e:
                    log_message(f"永豐訂閱報價失敗 {str(e)}", "broker", "error")
                    raise e

                summary["success"] += 1
            except Exception as e:
                summary["failed"] += 1
                summary["errors"].append(str(e))

        if summary["failed"] == 0 and summary["success"] > 0:
            system_message = "訂閱成功"
        elif summary["success"] == 0 and summary["failed"] > 0:
            system_message = "沒有商品被訂閱"
        else:
            system_message = "部分商品訂閱成功, 請查看回傳訊息"

        SYSTEM_EVENT.send(Event.ON_SYSTEM, response=get_response(SuccessCode.FetchMarketLiveSuccess.code, system_message))

        return get_response(SuccessCode.FetchMarketLiveSuccess.code, summary)

    def unsubscribe(self, params: Dict[str, str], **kwargs) -> Dict[str, str]:
        """取消訂閱永豐報價

        Args:
            params (Dict[str, str]): 參數
        
        Returns:
            Dict[str, str]: 回傳結果
        """
        try:
            model = SinoQuoteValidate(**params)
        except Exception as e:
            raise SubscribeFailed

        summary = {
            "success": 0,
            "failed": 0,
            "errors": []
        }

        for code in model.codes:
            try:
                contract = self.make_sino_contract_object(code["code"], code["market"])

                try:
                    self.api.quote.unsubscribe(
                        contract = contract
                    )
                except Exception as e:
                    log_message(f"永豐取消訂閱報價失敗 {str(e)}", "broker", "error")
                    raise e
                
                summary["success"] += 1
            except Exception as e:
                summary["failed"] += 1
                summary["errors"].append(str(e))
        
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
            exprs (List[pl.Expr]): polars 運算式
        to_pandas_df (bool): 是否轉換成 pandas DataFrame, 預設為 False
        
        Returns:
            pl.DataFrame: K 線資料
        """
        return self.quote_manager.get_kbar(code, unit, freq, exprs, to_pandas_df=to_pandas_df)
