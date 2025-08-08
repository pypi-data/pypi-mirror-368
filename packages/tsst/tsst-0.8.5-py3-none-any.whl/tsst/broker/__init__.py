import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal

import polars as pl

from tsst.utils import get_static_file_path
from tsst.validate import KbarParams, TickParams


class BaseBroker:
    """券商 Mixin 的基底類別
    """
    def normalize_stock_order_response(self, data: Any):
        """規範化下單回應
        """
        raise NotImplementedError("Please implement this method")

    def normalize_future_order_response(self, data: Any):
        """規範化下單回應
        """
        raise NotImplementedError("Please implement this method")

    def normalize_stock_deal_response(self, data: Any):
        """規範化成交回應
        """
        raise NotImplementedError("Please implement this method")

    def normalize_future_deal_response(self, data: Any):
        """規範化成交回應
        """
        raise NotImplementedError("Please implement this method")

    def to_standard_stock_order_response(self, data: Any) -> Dict[str, Any]:
        """轉換為標準的證券委託回報格式

        Args:
            data (Any): 原始委託回報資料

        Returns:
            Dict[str, Any]: 標準的委託回報格式
        """
        normalized_response = self.normalize_stock_order_response(data)

        return {
            "product_type": "Stock",
            **normalized_response
        }

    def to_standard_future_order_response(self, data: Any) -> Dict[str, Any]:
        """轉換為標準的期貨委託回報格式

        Args:
            data (Any): 原始委託回報資料

        Returns:
            Dict[str, Any]: 標準的委託回報格式
        """
        normalized_response = self.normalize_future_order_response(data)

        return {
            "product_type": "Future",
            **normalized_response
        }

    def to_standard_stock_deal_response(self, data: Any) -> Dict[str, Any]:
        """轉換為標準的證券成交回報格式

        Args:
            data (Any): 原始成交回報資料

        Returns:
            Dict[str, Any]: 標準的成交回報格式
        """
        normalized_response = self.normalize_stock_deal_response(data)

        return normalized_response

    def to_standard_future_deal_response(self, data: Any) -> Dict[str, Any]:
        """轉換為標準的期貨成交回報格式

        Args:
            data (Any): 原始成交回報資料

        Returns:
            Dict[str, Any]: 標準的成交回報格式
        """
        normalized_response = self.normalize_future_deal_response(data)

        return normalized_response

class QuoteManager:
    """
        報價管理
    """
    def __init__(self):
        # 讀取假日資料
        file_path = get_static_file_path("holidays_search_from_2017.csv")
        holiday_search_df = pl.read_csv(file_path, has_header=True)
        self.holiday_search_set = set(holiday_search_df["Date"])

        # 紀錄接收進來的 Ticks, 後續用於行情管理
        self.ticks: List[Dict[str, Any]] = []

        # 用於紀錄訂閱的商品, 其最近一接收到的 Tick 資料
        self.subscribe_code_last_tick: Dict[str, Dict] = {}

        self.tick_df: pl.DataFrame = pl.DataFrame(
            [],
            schema=[
                ("dt", pl.Datetime),
                ("market_type", pl.Utf8),
                ("code", pl.Utf8),
                ("close", pl.Float64),
                ("qty", pl.Int64),
                ("tick_type", pl.Int8),
                ("is_simulate", pl.Boolean),
                ("is_virtual", pl.Boolean), # 是否為虛擬 Tick (用於補足連續 K 棒時間段缺失的 Tick)
            ],
        )

        self.not_trade_times = {
            "Stock": [
                [datetime.strptime("13:30:00", "%H:%M:%S").time(), datetime.strptime("23:59:59", "%H:%M:%S").time()],
                [datetime.strptime("00:00:00", "%H:%M:%S").time(), datetime.strptime("08:59:59", "%H:%M:%S").time()],
            ],
            "Future": [
                [datetime.strptime("13:45:00", "%H:%M:%S").time(), datetime.strptime("14:59:59", "%H:%M:%S").time()],
                [datetime.strptime("05:00:00", "%H:%M:%S").time(), datetime.strptime("08:44:59", "%H:%M:%S").time()],
            ]
        }

        self.cached_kbars = {} # 快取已經做好的 K 棒, 避免每次都要全部重新聚合一次

    def clear_ticks(self):
        """清空 ticks
        """
        self.subscribe_code_last_tick = {}
        self.ticks = []
        self.tick_df: pl.DataFrame = pl.DataFrame(
            [],
            schema=[
                ("dt", pl.Datetime),
                ("market_type", pl.Utf8),
                ("code", pl.Utf8),
                ("close", pl.Float64),
                ("qty", pl.Int64),
                ("tick_type", pl.Int8),
                ("is_simulate", pl.Boolean),
                ("is_virtual", pl.Boolean),
            ],
        )

    def add_tick(self, tick: Dict[str, Any]):
        """將 Tick 資料加入到 ticks 中

        Args:
            tick (Dict[str, Any]): Tick 資料
        """
        # 1. 型態檢查: tick 必須為 dict
        if not isinstance(tick, dict):
            raise TypeError("Tick must be a dictionary")

        # 2. 欄位型態驗證
        tick_params = TickParams(**tick)

        # 3. 轉成 datetime
        ts = datetime.fromtimestamp(tick_params.timestamp)
        ticks = []

        # 4. 若此 code 之前已有 Tick，檢查是否需要補齊虛擬 Tick
        if tick_params.code in self.subscribe_code_last_tick:
            last_tick = self.subscribe_code_last_tick[tick_params.code]
            diff_seconds = (ts - last_tick["dt"]).total_seconds()
            diff_minute = int(diff_seconds // 60)

            # 若秒數餘數>0，且跨分鐘超過 1 分鐘，則多算一分鐘
            rest_second = 1 if (diff_seconds % 60 > 0 and ts.minute - last_tick["dt"].minute > 1) else 0
            missing_kbar_count = diff_minute + rest_second

            if missing_kbar_count > 1:
                # 逐分鐘補齊
                for i in range(missing_kbar_count):
                    new_dt = last_tick["dt"].replace(second=0, microsecond=0) + timedelta(minutes=i + 1)

                    # 排除週末非交易（期貨週六00:00-05:00例外）
                    if new_dt.weekday() >= 5 and \
                        not (tick_params.market_type == "Future" and  datetime.strptime("00:00:00", "%H:%M:%S").time() <= new_dt.time() <= datetime.strptime("05:00:00", "%H:%M:%S").time()):
                        continue

                    # 日內非交易時段過濾
                    ignore_flag = False
                    for not_trade_time in self.not_trade_times.get(tick_params.market_type, []):
                        if not_trade_time[0] <= new_dt.time() <= not_trade_time[1]:
                            ignore_flag = True
                            break
                    if ignore_flag:
                        continue

                    # 國定假日／颱風假過濾 (若在凌晨5點前，視為前一日)
                    if new_dt.time() <= datetime.strptime("05:00:00", "%H:%M:%S").time():
                        new_dt_str = (new_dt - timedelta(days=1)).strftime("%Y-%m-%d")
                    else:
                        new_dt_str = new_dt.strftime("%Y-%m-%d")
                    if new_dt_str in self.holiday_search_set:
                        continue

                    # 新增虛擬 Tick
                    ticks.append({
                        "dt": new_dt,
                        "market_type": last_tick["market_type"],
                        "code": last_tick["code"],
                        "close": last_tick["close"],
                        "qty": 0,
                        "tick_type": 0,
                        "is_simulate": False,
                        "is_virtual": True,
                    })

        # 5. 加入真實 Tick
        ticks.append({
            "dt": ts,
            "market_type": tick["market_type"],
            "code": tick["code"],
            "close": tick["close"],
            "qty": tick["qty"],
            "tick_type": tick["tick_type"],
            "is_simulate": tick["is_simulate"],
            "is_virtual": False,
        })

        # 6. 若真實 Tick 時間落在當日非交易時段，將時間往前移一秒
        for not_trade_time in self.not_trade_times.get(tick["market_type"], []):
            if not_trade_time[0] <= ts.time() <= not_trade_time[1]:
                ticks[-1]["dt"] = ts.replace(hour=not_trade_time[0].hour, minute=not_trade_time[0].minute, second=not_trade_time[0].second) - timedelta(seconds=1)
                break

        # 7. 更新最後一筆 Tick，並將所有新 Tick 加入 self.ticks
        self.subscribe_code_last_tick[tick["code"]] = ticks[-1]
        self.ticks.extend(ticks)

    def combine_df(self, df: pl.DataFrame):
        """合併 DataFrame

        Args:
            df (pl.DataFrame): 要合併的 DataFrame
        """
        self.tick_df = self.tick_df.vstack(df)

    def poped_tick_to_df(self) -> pl.DataFrame:
        """將 ticks 中的資料轉換為 DataFrame 並清空 ticks

        Returns:
            pl.DataFrame: 轉換後的 DataFrame
        """
        poped_ticks, self.ticks = self.ticks, []
        if poped_ticks:
            df = pl.DataFrame(poped_ticks).select(
                pl.col("dt").cast(pl.Datetime),
                pl.col("market_type").cast(pl.Utf8),
                pl.col("code").cast(pl.Utf8),
                pl.col("close").cast(pl.Float64),
                pl.col("qty").cast(pl.Int64),
                pl.col("tick_type").cast(pl.Int8),
                pl.col("is_simulate").cast(pl.Boolean),
                pl.col("is_virtual").cast(pl.Boolean),
            )
            df = df.sort("dt", maintain_order=True)
            # self.tick_df = self.tick_df.vstack(df).sort("dt", maintain_order=True)
            return df
        else:
            return pl.DataFrame(
                [],
                schema=[
                    ("dt", pl.Datetime),
                    ("market_type", pl.Utf8),
                    ("code", pl.Utf8),
                    ("close", pl.Float64),
                    ("qty", pl.Int64),
                    ("tick_type", pl.Int8),
                    ("is_simulate", pl.Boolean),
                    ("is_virtual", pl.Boolean),
                ],
            )

    def aggregate_kbar(self, tick_df: pl.DataFrame) -> pl.DataFrame:
        """將 Tick 資料聚合成 K 棒資料 (tick_df 已包含 kbar_time 欄位)

        Args:
            tick_df (pl.DataFrame): Tick 資料，必須包含 kbar_time 欄

        Returns:
            pl.DataFrame: 聚合後的 K 棒資料
        """
        kbar_df = tick_df.group_by(
            ["kbar_time", "code", "is_virtual"]
        ).agg([
            pl.col("close").first().alias("Open"),
            pl.col("close").max().alias("High"),
            pl.col("close").min().alias("Low"),
            pl.col("close").last().alias("Close"),
            pl.col("qty").sum().alias("Volume"),
        ]).rename({"kbar_time": "dt"})

        return kbar_df

    def get_kbar(self, code: str, unit: Literal["m", "h", "d", "w", "mo", "q", "y"], freq: int, exprs: List[pl.Expr] = [], to_pandas_df: bool = False) -> pl.DataFrame:
        """取得 K 線資料

        Args:
            code (str): 商品代號
            unit (Literal["m", "h", "d", "w", "mo", "q", "y"]): K 線頻率單位
            freq (int): K 線頻率
            exprs (List[pl.Expr]): 給予使用者自定義的運算式
            to_pandas_df (bool): 是否轉換為 pandas DataFrame

        Returns:
            pl.DataFrame: K 線資料
        """
        # input parameters validate
        params = {"code": code, "freq": freq, "unit": unit, "exprs": exprs, "to_pandas_df": to_pandas_df}
        model = KbarParams(**params)

        def return_fn(df: pl.DataFrame):
            """轉換為 pandas DataFrame"""
            if to_pandas_df:
                return df.to_pandas()
            else:
                return df

        tick_df = self.poped_tick_to_df()

        tick_df = tick_df.filter(pl.col("code") == model.code).with_columns(
            pl.col("dt").cast(pl.Datetime).alias("dt"),
            pl.col("dt").dt.truncate(f"{model.freq}{model.unit}").alias("kbar_time")
        )

        cache_key = (model.code, model.unit, model.freq)

        if cache_key in self.cached_kbars:
            if tick_df.is_empty():
                return return_fn(self.cached_kbars[cache_key])

            kbar_df = self.cached_kbars[cache_key]
            last_kbar_dt = kbar_df["dt"].max()

            # 只保留重算最後一根未完成的 tick 資料
            tick_df = tick_df.filter(
                (pl.col("kbar_time") >= last_kbar_dt) &
                (pl.col("is_simulate") != True)
            )

            # 聚合新的 K 棒
            newest_kbar_df = self.aggregate_kbar(tick_df)

            combined_df = kbar_df.vstack(newest_kbar_df)

            kbar_df = combined_df.group_by(["dt", "code", "is_virtual"]).agg([
                pl.col("Open").first(),
                pl.col("High").max(),
                pl.col("Low").min(),
                pl.col("Close").last(),
                pl.col("Volume").sum(),
            ])
        else:
            tick_df = tick_df.filter(pl.col("is_simulate") != True)
            kbar_df = self.aggregate_kbar(tick_df)

        if kbar_df.is_empty():
            return return_fn(kbar_df)

        # 同一時間的 K 棒若有虛擬與實際，只保留實際
        kbar_df = kbar_df.sort(["dt", pl.col("is_virtual")])
        kbar_df = kbar_df.group_by("dt", maintain_order=True).agg(pl.all().first())

        # 更新快取
        self.cached_kbars[cache_key] = kbar_df

        # 套用額外運算式
        if exprs:
            kbar_df = kbar_df.with_columns(exprs)

        return return_fn(kbar_df)


