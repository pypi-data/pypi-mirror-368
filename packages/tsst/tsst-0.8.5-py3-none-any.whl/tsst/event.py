from blinker import signal
from functools import wraps
from enum import Enum
from typing import Dict

SIGNAL_DICT = {}

class Event(Enum):
    """事件列舉
    """
    ON_LOGIN = "on_login"
    ON_SYSTEM = "on_system"
    ON_RECEIVE_ACCOUNT = "on_receive_account"

    ON_STOCK_TICK = "on_stock_tick"
    ON_FUTURE_TICK = "on_future_tick"
    ON_TICK = "on_tick" # 未定義的 Tick 事件, 群益有分的比較細

    ON_ORDER = "on_order" # 委託回報事件
    ON_DEAL = "on_deal" # 成交回報事件
    ON_REPLY = "on_reply" # 回報事件

    ON_POSITION = "on_position" # 持倉回報事件
    ON_POSITION_DETAIL = "on_position_detail" # 持倉明細回報事件
    ON_PROFIT = "on_profit" # 損益回報事件
    ON_PROFIT_DETAIL = "on_profit_detail" # 損益明細回報事件
    ON_ACCOUNT_BALANCE = "on_account_balance" # 帳戶餘額回報事件
    ON_MARGIN = "on_margin" # 保證金回報事件

def get_event(name: str):
    """取得事件

    Args:
        name (str): 事件名稱

    Returns:
        signal: 事件
    """
    if name not in SIGNAL_DICT:
        SIGNAL_DICT[name] = signal(name)

    return SIGNAL_DICT[name]

class SystemEventListener:
    """系統事件監聽, 定義 Tsst 需監聽的系統事件
    """
    def on_system(self, sender: str, response: Dict, **kwargs):
        """接收系統事件

        Args:
            sender (str): 發送者
            response (Dict): 回應訊息
        """
        print("OnSystem", sender, response)

class LoginEventListener:
    """事件監聽, 定義 Tsst 需監聽的事件
    """
    def on_login(self, sender: str, response: Dict, **kwargs):
        """接收登入事件

        Args:
            sender (str): 發送者
            response (Dict): 回應訊息
        """
        print("OnLogin", sender, response)
    
    def on_receive_account(self, sender: str, account, **kwargs):
        """接收帳號事件

        Args:
            sender (str): 發送者
            account (Any): 回應訊息
        """
        print("Default OnReceiveAccount", sender, account)

class QuoteEventListener:
    """報價事件監聽, 定義 Tsst 需監聽的報價事件
    """
    def on_stock_tick(self, sender: str, response: Dict, **kwargs):
        """接收股票報價事件

        Args:
            sender (str): 發送者
            response (Dict): 回應訊息
        """
        # print("Default OnStockTick", sender, response)
    
    def on_future_tick(self, sender: str, response: Dict, **kwargs):
        """接收期貨報價事件

        Args:
            sender (str): 發送者
            response (Dict): 回應訊息
        """
        # print("Default OnFutureTick", sender, response)

class TradeEventListener:
    """交易事件監聽, 定義 Tsst 需監聽的交易事件
    """
    def on_order(self, sender: str, response: Dict, **kwargs):
        """接收 委託回報事件

        Args:
            sender (str): 發送者
            response (Dict): 回應訊息
        """
        print("Default OnOrder", sender, response)
    
    def on_deal(self, sender: str, response: Dict, **kwargs):
        """接收 成交回報事件

        Args:
            sender (str): 發送者
            response (Dict): 回應訊息
        """
        print("Default OnDeal", sender, response)

class AccountEventListener:
    """帳務事件監聽, 定義 Tsst 需監聽的帳務事件
    """
    def on_position(self, sender: str, response: Dict, **kwargs):
        """接收持倉回報事件

        Args:
            sender (str): 發送者
            response (Dict): 回應訊息
        """
        print("Default OnPosition", sender, response)
    
    def on_position_detail(self, sender: str, response: Dict, **kwargs):
        """接收持倉明細回報事件

        Args:
            sender (str): 發送者
            response (Dict): 回應訊息
        """
        print("Default OnPositionDetail", sender, response)
    
    def on_profit(self, sender: str, response: Dict, **kwargs):
        """接收損益回報事件

        Args:
            sender (str): 發送者
            response (Dict): 回應訊息
        """
        print("Default OnProfit", sender, response)
    
    def on_profit_detail(self, sender: str, response: Dict, **kwargs):
        """接收損益明細回報事件

        Args:
            sender (str): 發送者
            response (Dict): 回應訊息
        """
        print("Default OnProfitDetail", sender, response)
    
    def on_account_balance(self, sender: str, response: Dict, **kwargs):
        """接收帳戶餘額回報事件

        Args:
            sender (str): 發送者
            response (Dict): 回應訊息
        """
        print("Default OnAccountBalance", sender, response)

    def on_margin(self, sender: str, response: Dict, **kwargs):
        """接收保證金回報事件

        Args:
            sender (str): 發送者
            response (Dict): 回應訊息
        """
        print("Default OnMargin", sender, response)
