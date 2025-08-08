import logging
import os
import sys
import importlib.util
import importlib.resources

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date
from rich.console import Console
from pathlib import Path
from typing import Dict, Any

from tsst.system_code import BaseCode, SuccessCode, ErrorCode


# 初始化 log 檔案路徑
ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
tsst_log_file_path = os.path.join(ROOT_DIR_PATH, 'tsst.log')
broker_log_file_path = os.path.join(ROOT_DIR_PATH, 'broker.log')

class TsstConsole(Console):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def print(self, *args, **kwargs):
        if kwargs.get("disable_print"):
            return
        else:
            kwargs.pop("disable_print", None)
        
        super().print(*args, **kwargs)

# 初始化 Console
console = TsstConsole()

# 初始化 Loggers
def setup_loggers():
    """
    ## 初始化 Loggers
    
    確保 log 檔案存在, 並設定 log 檔案路徑
    """
    # 設定 root logger
    logging.basicConfig(
        filename=tsst_log_file_path,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )

    # 建立 broker logger
    broker_logger = logging.getLogger("broker")

    # 設置 broker logger
    broker_handler = logging.FileHandler(broker_log_file_path, mode='a', encoding='utf-8')
    broker_handler.setLevel(logging.INFO)
    broker_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    broker_logger.addHandler(broker_handler)

    # 關閉 root logger 傳播
    broker_logger.propagate = False
setup_loggers()

def format_tick_data(timestamp: int, market_type: str, code: str, close: float, qty: int, tick_type: int, is_simulate: int, is_backfilling: int = 0) -> Dict[str, str]:
    """格式化報價資料

    Args:
        timestamp (int): 時間戳
        market_type (str): 市場類型
        code (str): 商品代號
        close (float): 收盤價
        qty (int): 成交量
        tick_type (int): Tick 類型
        is_simulate (int): 是否為試搓 Tick
        is_backfilling (int, optional): 是否為回補 Tick. Defaults to 0.

    Returns:
        Dict[str, Any]: 格式化後的報價資料
    """
    rounded_close = Decimal(close).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP) if close else Decimal('0.0000', rounding=ROUND_HALF_UP)
    
    return {
        "timestamp": timestamp,
        "market_type": market_type,
        "code": code,
        "close": rounded_close,
        "qty": qty,
        "tick_type": tick_type,
        "is_simulate": bool(is_simulate),
        "is_backfilling": bool(is_backfilling)
    }

def format_to_dt(value: Any) -> datetime:
    """格式化時間資料

    Args:
        value (Any): 時間資料, 字串或者日期物件

    Returns:
        datetime: 格式化後的時間物件
    """
    if isinstance(value, str):
        if '.' in value:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        elif ':' in value:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.strptime(value, '%Y-%m-%d')
    
    if type(value) == date:
        return datetime.combine(value, datetime.min.time())

    return value

def format_sino_nano_ts_to_second_ts(value: int, truncate_gmt_sec: int = 0) -> float:
    """將永豐的奈秒時間戳轉換為秒時間戳
    
    Args:
        value (int): 奈秒時間戳
        truncate_gmt_sec (int): 減去 GMT + n 的秒數
    
    Returns:
        float: 秒時間戳
    """
    # @TODO 看有沒有更好的做法
    # 永豐歷史 Tick 的時區是 GMT + 0, 為了讓本地電腦也可以正常顯示, 所以減掉 8 小時的秒數
    return value / 1e9 - (truncate_gmt_sec * 3600) # 歷史 Tick 的時間戳記單位是 ns, 而即時的 tick 是 ms, 而客戶端目前是使用 fromtimestamp 轉換, 

def generate_file_path(filename, *subfolder):
    """產生檔案路徑

    Args:
        filename (str): 檔案名稱
        subfolder (Tuple[str]): 子資料夾

    Returns:
        str: 檔案路徑
    """
    dir_path = os.path.join(ROOT_DIR_PATH, *subfolder)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    return os.path.join(dir_path, filename)

def get_response(status_code=None ,message=None):
    """
    取得標準的回應格式

    Args:
        message (str): 訊息, 如果是系統預設的狀態碼物件, 則使用該狀態碼物件的 Code 與訊息
        status_code: 狀態碼, 預設為 Success
    """
    if isinstance(status_code, (BaseCode, SuccessCode, ErrorCode)):
        status_code = status_code.code
        
        if not message:
            message = "Success" if status_code == "0000" else "Failed"
    else:
        if not status_code:
            status = SuccessCode.Success
            status_code = status.code
            
            if not message:
                message = status.message

    # 定義回傳資訊
    return_info = {"code": status_code, "message": message}

    # 回傳訊息
    return return_info

def log_message(message: str, logger_name: str = None, level: str = 'info'):
    """
    ## 紀錄訊息
    
    紀錄訊息到 log 檔案中

    ### Args:
        message (str): 訊息
        logger_name (str): Logger 名稱
        level (str): 等級
    """
    # 檢查 logger_name 是否在 logger_name_list 中
    logger_name_list = ["tsst", "broker"]
    if logger_name is not None:
        if logger_name not in logger_name_list:
            raise ValueError(f"logger_name is not found in {logger_name_list}")

    # 依照是否指定 logger_name 決定要使用哪一個 Logger
    if logger_name is None or logger_name == "tsst":
        logger_obj = logging.getLogger()
    else:
        logger_obj = logging.getLogger(logger_name)

    if level == 'info':
        logger_obj.info(message)
    elif level == 'error':
        logger_obj.error(message)
    elif level == 'warning':
        logger_obj.warning(message)
    elif level == 'debug':
        logger_obj.debug(message)
    else:
        logger_obj.info(message)

def get_static_file_path(filename: str) -> str:
    """取得靜態檔案路徑（開發與安裝均可）"""
    # 檢查是否為開發環境：檢查專案目錄中是否存在 src/tsst/static
    dev_static_dir = Path(__file__).resolve().parent.parent / 'static'
    dev_file = dev_static_dir / filename

    if dev_file.exists():
        return str(dev_file)

    # 安裝後環境：使用 importlib.resources
    try:
        with importlib.resources.path('tsst.static', filename) as static_file:
            return str(static_file)
    except (FileNotFoundError, ModuleNotFoundError):
        raise FileNotFoundError(f"找不到靜態檔案: {filename}")

def pump_event_loop():
    pythoncom.PumpWaitingMessages()