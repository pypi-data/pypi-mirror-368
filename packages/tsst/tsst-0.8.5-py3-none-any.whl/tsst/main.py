import queue
import requests as req
import signal
import traceback
from typing import Any, Callable, Dict, List, Literal, Optional

import polars as pl

from tsst.backtest.new_base import BacktestMixin
from tsst.error import BrokerNotSupport
from tsst.event import (
    AccountEventListener,
    Event,
    LoginEventListener,
    QuoteEventListener,
    SystemEventListener,
    TradeEventListener,
    get_event,
)
from tsst.system_code import SuccessCode, TsstErrorCode
from tsst.utils import console, get_response, log_message

SYSTEM_EVENT = get_event("system")
QUOTE_EVENT = get_event("quote")
TRADE_EVENT = get_event("trade")
ACCOUNT_EVENT = get_event("account")

class Tsst(BacktestMixin, LoginEventListener, SystemEventListener, QuoteEventListener, TradeEventListener, AccountEventListener):
    """TSST
    """
    def __init__(self, is_simulation: bool, use_broker: Literal["Sino", "Capital"], is_backtest: bool = False, **kwargs):
        """初始化 TSST

        Args:
            is_simulation (bool): 是否為模擬環境
            use_broker (str): 使用的券商, 目前可選擇永豐(Sino)或群益(Capital)
            is_backtest (bool): 是否為回測環境, 若為是, 則會初始化回測相關的套件
        """
        super().__init__(**kwargs)

        self.is_simulation = is_simulation
        self.broker = use_broker
        self.is_backtest = is_backtest
        self.TsstLogin = None
        self.TsstQuote = None
        self.TsstTrade = None
        self.TsstAccount = None

        self.login_obj = None
        self.quote_obj = None
        self.trade_obj = None
        self.account_obj = None

        self.main_queue = queue.Queue()

        self.__check_package_update()
        self.__load_package()
        self.__bind_signal()

    def __bind_signal(self):
        """綁定訊號
        """
        SYSTEM_EVENT.connect_via(Event.ON_SYSTEM)(self.on_system)

        QUOTE_EVENT.connect_via(Event.ON_FUTURE_TICK)(self.on_future_tick)
        QUOTE_EVENT.connect_via(Event.ON_STOCK_TICK)(self.on_stock_tick)

        TRADE_EVENT.connect_via(Event.ON_ORDER)(self.on_order)
        TRADE_EVENT.connect_via(Event.ON_DEAL)(self.on_deal)

        ACCOUNT_EVENT.connect_via(Event.ON_POSITION)(self.on_position)
        ACCOUNT_EVENT.connect_via(Event.ON_POSITION_DETAIL)(self.on_position_detail)
        ACCOUNT_EVENT.connect_via(Event.ON_PROFIT)(self.on_profit)
        ACCOUNT_EVENT.connect_via(Event.ON_PROFIT_DETAIL)(self.on_profit_detail)
        ACCOUNT_EVENT.connect_via(Event.ON_ACCOUNT_BALANCE)(self.on_account_balance)
        ACCOUNT_EVENT.connect_via(Event.ON_MARGIN)(self.on_margin)

    def __check_package_update(self):
        """檢查 tsst 是否需要更新"""
        import json
        from tsst import __version__

        verify_url = "https://tsst-package-verify.aiaristosit.workers.dev"

        try:
            console.print("正在檢查 TSST 套件更新...", style="bold blue")

            payload = {
                "current_version": __version__,
                "package_name": "tsst"
            }

            res = req.post(verify_url, data=json.dumps(payload))
            res_json = res.json()

            if res.status_code != 200:
                console.print("[red]無法取得 TSST 版本資訊[/red]")
                return
            
            versions = res_json.get("versions", [])

            if not versions:
                console.print("[green]TSST 已是最新版本[/green]")
            
            notify_message = ""

            for info in versions:
                version = info.get("version", "")
                change_type = info.get("change_type", "其他")
                description = info.get("description", "無")
                force_update = info.get("is_force_update", False)

                tmp = f"[yellow][{change_type}]版本: {version}[/yellow], 說明: {description}"

                if force_update:
                    tmp = "[red]建議儘速更新！[/red]" + tmp
                
                notify_message += tmp + "\n"
            
            console.print(notify_message)
        except Exception as e:
            console.print(f"[red]檢查套件更新失敗: {e}[/red]")
            log_message(traceback.format_exc(), level="error")
            return

    def __load_package(self):
        """載入套件
        """
        if self.broker == "Sino":
            self.__load_sino_package()
        elif self.broker == "Capital":
            self.__load_capital_package()
        else:
            raise BrokerNotSupport(self.broker)

    def __load_sino_package(self):
        """載入永豐相關的套件
        """
        console.print("載入永豐相關的套件...", style="bold blue")

        from tsst.account.sino.main import SinoAccount as TsstAccount
        from tsst.login.sino.main import SinoLogin as TsstLogin
        from tsst.trade.order.sino.main import SinoOrder as TsstTrade
        from tsst.trade.quote.sino.main import SinoQuote as TsstQuote

        self.TsstLogin = TsstLogin
        self.TsstQuote = TsstQuote
        self.TsstTrade = TsstTrade
        self.TsstAccount = TsstAccount

        console.print("套件載入完成", style="bold green")

    def __load_capital_package(self):
        """載入群益相關的套件
        """
        console.print("載入群益相關的套件...", style="bold blue")

        from tsst.login.capital.main import CaptialLogin as TsstLogin
        from tsst.trade.order.capital.main import CapitalOrder as TsstTrade
        from tsst.trade.quote.capital.main import CapitalQuote as TsstQuote

        self.TsstLogin = TsstLogin
        self.TsstQuote = TsstQuote
        self.TsstTrade = TsstTrade

        console.print("套件載入完成", style="bold green")

    def init_quote(self):
        """初始化報價
        """
        if not self.quote_obj:
            console.print("正在初始化報價物件...", style="bold blue")
            self.quote_obj = self.TsstQuote(obj = self.login_obj)

    def init_trade(self):
        """初始化交易
        """
        if not self.trade_obj:
            console.print("正在初始化交易物件...", style="bold blue")
            self.trade_obj = self.TsstTrade(obj = self.login_obj)

    def init_account(self):
        """初始化帳務模組
        """
        if not self.account_obj:
            console.print("正在初始化帳務物件...", style="bold blue")
            self.account_obj = self.TsstAccount(obj = self.login_obj)

        if not self.is_backtest:
            pass

    def login(self, params: Dict, **kwargs) -> Dict[str, str]:
        """登入

        Args:
            params (dict): 參數

        Returns:
            response (dict): 登入成功或失敗
        """
        self.login_obj = self.TsstLogin(is_simulation = self.is_simulation)

        if self.is_backtest:
            self.tsst_login(params)
            console.print("[yellow]已登入回測模組[/yellow]")

        response = self.login_obj.run(params)
        self.login_params = params

        return response

    def subscribe(self, params: Dict, backtest_params: Dict[str, Any] = None, **kwargs) -> Dict[str, str]:
        """訂閱

        Args:
            params (dict): 參數
            backtest_params (dict): 回測參數, 僅回測模式下的訂閱才會套用

        Returns:
            response (dict): 訂閱成功或失敗
        """
        # 初始化報價物件
        self.init_quote()

        if self.is_backtest:
            # 回測模式下，改成向回測模組做訂閱
            codes = params.get("codes", [])

            if not codes:
                console.print("[subscribe] 參數錯誤, 請檢查 codes", style="bold red")
                return get_response(TsstErrorCode.SubscribeFailed.code, "參數錯誤, 請檢查 codes")

            self.stream_ticks(
                codes = codes,
                **backtest_params
            )

            response = get_response(SuccessCode.FetchMarketLiveSuccess.code, {})
        else:
            try:
                response = self.quote_obj.subscribe(params)
            except Exception as e:
                console.print(f"[subscribe] 訂閱即時行情失敗: {e}", style="bold red")
                log_message(traceback.format_exc(), level="error")
                response = get_response(TsstErrorCode.SubscribeFailed.code, str(e))

        return response

    def unsubscribe(self, params: Dict, **kwargs) -> Dict[str, str]:
        """取消訂閱

        Args:
            params (dict): 參數

        Returns:
            response (dict): 取消訂閱成功或失敗
        """
        try:
            if self.is_backtest:
                self.bt.stop_send_ticks()
                response = get_response(SuccessCode.CancelMarketLiveSuccess.code, {})
            else:
                self.init_quote()
                response = self.quote_obj.unsubscribe(params)
        except Exception as e:
            console.print(f"[unsubscribe] 取消訂閱即時行情失敗: {e}", style="bold red")
            log_message(traceback.format_exc(), level="error")
            response = get_response(TsstErrorCode.UnsubscribeFailed.code, str(e))

        return response

    def backfilling(self, params: Dict, **kwargs) -> Dict[str, str]:
        """回補即時行情報價

        Args:
            params (Dict): 參數

        Returns:
            Dict[str, str]: 回補成功或失敗
        """
        if self.is_backtest:
            console.print("[backfilling] 回測模式下不支援回補即時行情", style="bold red")
            return get_response(TsstErrorCode.BackFillingNotSupport.code, "回測模式下不支援回補即時行情")

        try:
            self.init_quote()
            response = self.quote_obj.backfilling(params)
        except Exception as e:
            console.print(f"[backfilling] 回補即時行情報價失敗: {e}", style="bold red")
            log_message(traceback.format_exc(), level="error")
            response = get_response(TsstErrorCode.BackFillingFailed.code, str(e))

        return response

    def create_order(self, code: str, product_type: Literal["Stock", "Future"], params: Dict, **kwargs) -> Dict[str, str]:
        """下單

        Args:
            code (str): 商品代號
            product_type (Literal["Stock", "Future"]): 商品類型
            params (dict): 參數

        Returns:
            response (dict): 下單成功或失敗
        """
        try:
            self.init_trade()

            if not self.is_backtest:
                response = self.trade_obj.create_order(code, product_type, params)
            else:
                # 回測模式下, 改由送單給回測模組
                self.create_backtest_order(code, product_type, params)
                response = get_response(
                    status_code=SuccessCode.CreateOrderSuccess.code,
                    message="下單成功",
                )
        except Exception as e:
            console.print(f"[create_order] 下單失敗: {e}", style="bold red")
            log_message(traceback.format_exc(), level="error")
            response = get_response(TsstErrorCode.OrderFailed.code, str(e))

        return response

    def modify_order(self, id: str, product_type: Literal["Stock", "Future"], price: float = None, quantity: int = None, **kwargs) -> Dict[str, str]:
        """改單

        Args:
            id (str): 交易編號
            product_type (Literal["Stock", "Future"]): 商品類型
            price (float): 要修改的價格
            quantity (int): 要刪除的數量

        Returns:
            Dict[str, str]: 改單成功或失敗
        """
        try:
            if not self.is_backtest:
                response = self.trade_obj.modify_order(
                    id = id,
                    product_type = product_type,
                    price = price,
                    quantity = quantity
                )
            else:
                # 回測模式下, 改由送單給回測模組
                self.modify_backtest_order(
                    id = id,
                    price = price,
                    quantity = quantity
                )
                response = get_response(
                    status_code=SuccessCode.ModifyOrderSuccess.code,
                    message="改單成功",
                )
        except Exception as e:
            console.print(f"[modify_order] 改單失敗: {e}", style="bold red")
            log_message(traceback.format_exc(), level="error")
            response = get_response(TsstErrorCode.ModifyOrderFailed.code, str(e))

        return response

    def cancel_order(self, id: str, product_type: Literal["Stock", "Future"]) -> Dict[str, str]:
        """刪單

        Args:
            id (str): 交易編號
            product_type (Literal["Stock", "Future"]): 商品類型

        Returns:
            Dict[str, str]: 刪單成功或失敗
        """
        try:
            if not self.is_backtest:
                response = self.trade_obj.cancel_order(
                    id = id,
                    product_type = product_type
                )
            else:
                # 回測模式下, 改由送單給回測模組
                self.cancel_backtest_order(id)
                response = get_response(
                    status_code=SuccessCode.CancelOrderSuccess.code,
                    message="刪單成功",
                )
        except Exception as e:
            console.print(f"[cancel_order] 刪單失敗: {e}", style="bold red")
            log_message(traceback.format_exc(), level="error")
            response = get_response(TsstErrorCode.CancelOrderFailed.code, str(e))

        return response

    def fetch_positions(self, account_type: Literal["Stock", "Future", "Option"], fetch_detail = False, **kwargs) -> Dict[str, Any]:
        """取得未實現損益(庫存)

        Args:
            account_type (Literal["Stock", "Future", "Option"]): 帳號類型
            fetch_detail (bool): 是否取得詳細資訊

        Returns:
            Dict[str, Any]: 未實現損益(庫存)
        """
        try:
            if self.is_backtest:
                self.fetch_backtest_positions(account_type, fetch_detail)
                return get_response(
                    status_code=SuccessCode.Success.code,
                    message="查詢成功",
                )
            else:
                self.init_account()
                return self.account_obj.fetch_portfolio(account_type, fetch_detail)
        except Exception as e:
            console.print(f"[fetch_positions] 取得未實現損益(庫存)失敗: {e}", style="bold red")
            log_message(traceback.format_exc(), level="error")
            return {}

    def fetch_profit(self, account_type: Literal["Stock", "Future", "Option"], start_from: str = "", end_to: str = "", fetch_detail = False, **kwargs) -> Dict[str, Any]:
        """取得已實現損益
        @TODO 增加回測模式下的支援
        Args:
            account_type (Literal["Stock", "Future", "Option"]): 帳號類型
            start_from (str): 查詢開始日期
            end_to (str): 查詢結束日期
            fetch_detail (bool): 是否取得詳細資訊

        Returns:
            response (dict): 已實現損益
        """
        try:
            self.init_account()
            response = self.account_obj.fetch_portfolio_loss(account_type, start_from, end_to, fetch_detail)
            return response
        except Exception as e:
            console.print(f"[fetch_profit] 取得已實現損益失敗: {e}", style="bold red")
            log_message(traceback.format_exc(), level="error")
            return {}

    def get_kbar(self, code: str, unit: Literal["m", "h", "d", "w", "mo", "q", "y"], freq: int, exprs: List[pl.Expr] = [], to_pandas_df: bool = False) -> pl.DataFrame:
        """取得 K 線資料

        Args:
            code (str): 商品代號
            unit (Literal["m", "h", "d", "w", "mo", "q", "y"]): K 線頻率單位
            freq (int): 頻率
            exprs (List[pl.Expr]): polars 運算式
            to_pandas_df (bool): 是否轉換為 pandas DataFrame

        Returns:
            pl.DataFrame: K 線資料
        """
        if not self.quote_obj:
            console.print("[get_kbar] 尚未初始化報價物件", style="bold red")
            raise ValueError("Quote object not initialized")
        else:
            try:
                return self.quote_obj.get_kbar(code, unit, freq, exprs, to_pandas_df)
            except Exception as e:
                console.print(f"[get_kbar] 取得 K 線資料失敗: {e}", style="bold red")
                log_message(traceback.format_exc(), level="error")
                self.unsubscribe({"codes": [{"code": code, "market": "Stock"}]})
                return pl.DataFrame()

    def keep_running(self, stop_fn: Optional[Callable[[], bool]] = None):
        """保持程式持續運行

        Args:
            stop_fn (Optional[Callable[[], bool]]): 停止時的 callback
        """
        def handler(signum, frame):
            print("Ctrl + C pressed, exiting")

            self.main_queue.put("exit")

        signal.signal(signal.SIGINT, handler)

        try:
            while True:
                try:
                    command = self.main_queue.get(timeout=1)
                except queue.Empty:
                    continue

                if command == "exit":
                    console.print("[bold red]已停止[/bold red]")
                    break
        except KeyboardInterrupt:
            console.print("[bold red]Ctrl + C detected, exiting...[/bold red]")
            self.main_queue.put("exit")

    def fetch_account_balance(self) -> Dict[str, Any]:
        """取得股票交割戶餘額

        Returns:
            Dict[str, Any]: 成功與否
        """
        try:
            if not self.is_backtest:
                if not self.account_obj:
                    self.init_account()

                self.account_obj.fetch_account_balance()
            else:
                balance = self.bt.fetch_account_balance()
                ACCOUNT_EVENT.send(Event.ON_ACCOUNT_BALANCE, response=balance)

            return get_response(
                status_code=SuccessCode.FetchAccountBalanceSuccess.code,
                message=SuccessCode.FetchAccountBalanceSuccess.message
            )
        except Exception as e:
            console.print(f"[fetch_account_balance] 取得股票交割戶餘額失敗: {e}", style="bold red")
            log_message(traceback.format_exc(), level="error")
            return {}

    def fetch_margin(self) -> Dict[str, Any]:
        """取得期貨保證金餘額

        Returns:
            Dict[str, Any]: 成功與否
        """
        try:
            if not self.is_backtest:
                if not self.account_obj:
                    self.init_account()

                self.account_obj.fetch_margin()
            else:
                margin = self.bt.fetch_margin()
                ACCOUNT_EVENT.send(Event.ON_MARGIN, response=margin)

            return get_response(
                status_code=SuccessCode.FetchMarginSuccess.code,
                message=SuccessCode.FetchMarginSuccess.message
            )
        except Exception as e:
            console.print(f"[fetch_account_balance] 取得保證金餘額失敗: {e}", style="bold red")
            log_message(traceback.format_exc(), level="error")
            return {}

    def set_initial_capital(self, amount: float):
        """設定初始資金

        Args:
            amount (float): 初始資金
        """
        if not self.is_backtest:
            console.print("[set_initial_capital] 只有回測模式下才支援設定初始資金", style="bold red")
            return

        self.bt.set_initial_capital(amount)
        console.print(f"[set_initial_capital] 已設定初始資金: {amount}", style="bold green")
    
    def update_fee_settings(self, setting_type: Literal['stock', 'future'], action: Literal['buy', 'sell'] = None, fee: (float) = None, tax: float = None, per_trade_cost: int = None, tick_count: int = None, direction: Literal['up', 'down'] = None):
        """更新回測費用設定
        
        Args:
            setting_type (Literal['stock', 'future']): 費用設定類型
            action (Literal['buy', 'sell'], optional): 動作類型. Defaults to None.
            fee (float, optional): 手續費. Defaults to None.
            tax (float, optional): 稅金. Defaults to None.
            per_trade_cost (int, optional): 每筆交易成本. Defaults to None.
            tick_count (int, optional): Tick 數量. Defaults to None.
            direction (Literal['up', 'down'], optional): 方向. Defaults to None.
        """
        if not self.is_backtest:
            console.print("[update_fee_settings] 只有回測模式下才支援更新費用設定", style="bold red")
            return

        self.bt.update_fee_settings(
            setting_type = setting_type,
            action = action,
            fee = fee,
            tax = tax,
            per_trade_cost = per_trade_cost,
            tick_count = tick_count,
            direction = direction
        )
        console.print(f"[update_fee_settings] 已更新 {setting_type} 費用設定", style="bold green")

    def get_current_accounts(self):
        """取得目前可用的帳號資訊
        
        Returns:
            Dict[str, Any]: 目前可用的帳號資訊
        """
        if not self.login_obj:
            console.print("[get_current_accounts] 尚未登入", style="bold red")
            return {}
        
        if self.is_backtest:
            console.print("[get_current_accounts] 回測模式下不支援取得帳號資訊", style="bold red")
            return {}
        
        return self.login_obj.accounts

    def mock_tick_data(self, market_type: Literal["Stock", "Future"], mock_data: List[Dict[str, Any]]):
        """可使用測試用的 Tick, 用於快速測試策略
        給定模擬的 Tick 資料, 將會依照市場別把 Tick 透過 on_stock 或 on_future 回傳

        Args:
            market_type (Literal["Stock", "Future"]): 市場別
            mock_data (List[Dict[str, Any]]): 模擬的 Tick 資料
                - datetime (string|datetime): 時間, 將會自動轉為 Timestamp
                - code (str): 商品代號
                - close (float): 收盤價
                - qty (int): 成交量
                - tick_type (int): Tick 類型
                - is_simulate (int): 是否為試搓 Tick
                - is_backfilling (int, optional): 是否為回補 Tick. Defaults to 0.
        """
        from tsst.utils import format_tick_data, format_to_dt

        for data in mock_data:
            timestamp = format_to_dt(data["datetime"]).timestamp()
            tick_response = format_tick_data(
                timestamp = timestamp,
                market_type = market_type,
                code = data["code"],
                close = data["close"],
                qty = data["qty"],
                tick_type = data["tick_type"],
                is_simulate = data["is_simulate"],
                is_backfilling = data.get("is_backfilling", 0)
            )
            self.quote_obj.quote_manager.add_tick(tick_response)

            if market_type == "Stock":
                QUOTE_EVENT.send(Event.ON_STOCK_TICK, response=tick_response)
            elif market_type == "Future":
                QUOTE_EVENT.send(Event.ON_FUTURE_TICK, response=tick_response)
