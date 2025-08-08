import copy
import inspect
import json
import os
import queue
import threading
import time
from typing import Any, Dict, List, Literal

import polars as pl
import polars_talib as plta
from tsst_sino_backtest.main import BacktestModule

import tsst
import tsst.error
from tsst.event import Event, get_event
from tsst.login.sino.validate import SinoLoginValidate
from tsst.system_code import SuccessCode
from tsst.utils import console


class BacktestMixin:
    def __init__(self, **kwargs):
        self.quote_event = get_event("quote")
        self.trade_event = get_event("trade")
        self.account_event = get_event("account")

        self.bt = BacktestModule()

    def __receive_response_thread(self):
        """接收回報"""
        while True:
            try:
                response = self.bt.receive_response()
            except queue.Empty:
                console.print("[bold red]接收回報失敗: queue.Empty[/bold red]")
                break

            if response is None:
                continue

            if response.get('tsst_status') == 'exit_receive_response':
                console.print("[bold red]已停止接收回報[/bold red]")
                break

            console.print(f"[bold green]接收到回報: {response}[/bold green]")
            if "order" in response:
                self.trade_event.send(Event.ON_ORDER, response=response)
            else:
                self.trade_event.send(Event.ON_DEAL, response=response)

    def __receive_tick_thread(self):
        """接收報價"""
        while True:
            response = self.bt.receive_tick()

            if response is None:
                continue

            if response.get('tsst_status') == 'exit_send_tick':
                # 通知下單模組回測已結束
                # @TODO 可能可以再調整 FLAG 的設定
                # 通知回測模組產生交易紀錄
                self.bt.export_trade_records()
                self.bt.generate_profit_report()

                self.main_queue.put("exit")
                console.print("[bold red]已停止報價[/bold red]")
                break
            elif response.get('tsst_status') == 'finish_backfilling':
                console.print("[bold red]回補完成[/bold red]")
                continue

            if hasattr(self, "quote_obj") and self.quote_obj:
                self.quote_obj.quote_manager.add_tick(response)

            # 由於 signal 是非同步的, 可能會導致 on_tick 事件還沒處理完就進入下一個 Tick, 所以這邊改成使用直接呼叫來進行 callback
            # 回補 Tick 不會觸發 on_tick 事件
            if not response["is_backfilling"]:
                if response['market_type'] == "Stock":
                    self.on_stock_tick('on_tick', response=response)
                elif response['market_type'] == "Future":
                    self.on_future_tick('on_tick', response=response)
                else:
                    console.print(f"[bold red]不支援的商品類型: {response['market_type']}[/bold red]")

                self.bt.allow_next_tick()

    def __receive_fetch_positions_thread(self):
        """接收持有部位"""
        while True:
            position = self.bt.receive_positions()

            if position is None:
                continue

            if isinstance(position, dict):
                if position.get('tsst_status') == 'exit_receive_positions':
                    console.print("[bold red]已停止接收持有部位[/bold red]")
                    break

            # 處理庫存明細
            self.on_position('position', response=position)
            self.bt.notify_fetch_positions_finish()

    def tsst_login(self, params: Dict[str, Any]):
        """登入 TSST

        Args:
            params (Dict[str, Any]): 登入參數
        """
        console.print("[yellow]回測模組初始化中...[/yellow]")

        try:
            model = SinoLoginValidate(**params)
        except Exception as e:
            console.print(f"登入回測模組失敗: {e}", style="bold red")
            raise tsst.error.BacktestLoginFailed

        self.bt.login(
            api_key=model.api_key,
            secret_key=model.secret_key,
            ca_path=model.ca_path,
            ca_password=model.ca_password,
            tsst_token=model.tsst_token,
            email=model.email
        )

        # 建立接收回報的執行緒
        response_thread = threading.Thread(target=self.__receive_response_thread, daemon=True)
        response_thread.start()
        console.print("[bold orange1]已建立回應接收 Thread[/bold orange1]")

        # 建立接收報價的執行緒
        tick_thread = threading.Thread(target=self.__receive_tick_thread, daemon=True)
        tick_thread.start()
        console.print("[bold orange1]已建立報價接收 Thread[/bold orange1]")

        # 建立接收持有部位的執行緒
        position_thread = threading.Thread(target=self.__receive_fetch_positions_thread, daemon=True)
        position_thread.start()
        console.print("[bold orange1]已建立持有部位接收 Thread[/bold orange1]")

    def stream_ticks(self, codes: List[Dict[str, str]], start_from: str, end_to: str, backfilling_start_from: str = None, backfilling_end_to: str = None, clear_quote_manager: bool = False):
        """接收歷史 ticks 資料

        Args:
            codes (List[Dict[str, str]]): 商品代號
            start_from (str): 開始時間
            end_to (str): 結束時間
            backfilling_start_from (str, optional): 回補開始日期. Defaults to None., 若回補結束日期沒有填寫, 回測模組會將回補結束日會預設為該值
            backfilling_end_to (str, optional): 回補結束日期. Defaults to None., 若回補開始日期沒有填寫, 回測模組會將回補開始日會預設為該值
            clear_quote_manager (bool): 是否清空報價管理器中已經儲存的 Tick
            aggregate_to_kbar (bool): 是否將 Tick 資料聚合成 K 棒後做回測. Defaults to False.
            callback (callable, optional): 接收歷史 ticks 資料完成的 callback. Defaults to None.
        """
        self.bt.send_ticks(
            codes=codes,
            start_from=start_from,
            end_to=end_to,
            backfilling_start_from=backfilling_start_from, #  @
            backfilling_end_to=backfilling_end_to,
        )

    def create_backtest_order(self, code: str, product_type: Literal["Stock", "Future"], params: Dict, **kwargs):
        """建立回測訂單

        Args:
            code (str): 商品代號
            product_type (Literal["Stock", "Future"]): 商品類型
            params (Dict): 訂單參數
        """
        console.print(f"[bold green]建立回測訂單: {code}, {product_type}, {params}[/bold green]")
        self.bt.add_order(
            code=code,
            product_type=product_type,
            **params
        )

    def modify_backtest_order(self, id: str, price: float = None, quantity: int = None, **kwargs):
        """修改回測訂單

        Args:
            id (str): 訂單編號
            price (float): 修改價格, default=None
            quantity (int): 修改數量, default=None
        """
        self.bt.modify_order(
            id,
            qty=quantity,
            price=price
        )

    def cancel_backtest_order(self, id: str, **kwargs):
        """取消回測訂單

        Args:
            id (str): 訂單編號
        """
        self.bt.cancel_order(id)

    def fetch_backtest_positions(self, product_type: Literal["Stock", "Future"], fetch_detail: bool = False):
        """取得持倉資訊

        Args:
            product_type (Literal["Stock", "Future"]): 商品類型
            fetch_detail (bool): 是否取得詳細資訊, default=False
        """
        self.bt.fetch_positions(product_type, fetch_detail)
