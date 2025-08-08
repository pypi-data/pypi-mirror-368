from typing import Any, Dict, List, Literal

import shioaji as sj

from tsst.account.base import BaseAccount
from tsst.constant import Action, OrderCond
from tsst.error import MarketCodeNotFound
from tsst.event import Event, get_event
from tsst.system_code import SuccessCode
from tsst.utils import console, get_response, log_message

ACCOUNT_EVENT = get_event("account")

class SinoAccount(BaseAccount):
    """永豐帳務模組
    """
    def __init__(self, obj, **kwargs):
        """初始化永豐帳務模組

        Args:
            obj (SinoLogin): TSST Login
        """
        super().__init__(**kwargs)
        self.api = obj.api
        self.login_module = obj

    def __format_portfolio(self, positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化永豐的持倉資訊
        @TODO 優化賦值方式, 改為用解構的方式處理

        Args:
            positions (List[Dict[str, Any]]): 永豐 list_positions 回傳的持倉資訊

        Returns:
            List[Dict[str, Any]]: 格式化後的持倉資訊
        """
        result = []

        for position in positions:
            if isinstance(position, sj.position.StockPosition):
                response_struct = self.get_stock_position_summary_struct()
                response_struct["code"] = position.code
                response_struct["quantity"] = position.quantity
                response_struct["avg_price"] = position.price
                response_struct["pnl"] = position.pnl
                response_struct["cond"] = OrderCond.from_value(position.cond)
                response_struct["margin_purchase_amount"] = position.margin_purchase_amount
                response_struct["collateral"] = position.collateral
                response_struct["short_sale_margin"] = position.short_sale_margin
                response_struct["interest"] = position.interest

                result.append(response_struct)
            elif isinstance(position, sj.position.FuturePosition):
                response_struct = self.get_future_position_summary_struct()
                response_struct["code"] = position.code
                response_struct["quantity"] = position.quantity
                response_struct["avg_price"] = position.price
                response_struct["pnl"] = position.pnl

                result.append(response_struct)
            elif isinstance(position, sj.position.StockProfitLoss):
                response = self.get_stock_profit_loss_summary_struct()
                response["date"] = position.date
                response["code"] = position.code
                response["quantity"] = position.quantity
                response["trade_id"] = position.dseq
                response["price"] = position.price
                response["pnl"] = position.pnl
                response["pr_rate"] = position.pr_ratio
                response["cond"] = OrderCond.from_value(position.cond)

                result.append(response)
            elif isinstance(position, sj.position.FutureProfitLoss):
                response = self.get_future_profit_loss_summary_struct()
                response["code"] = position.code
                response["quantity"] = position.quantity
                response["pnl"] = position.pnl
                response["date"] = position.date
                response["entry_price"] = position.entry_price
                response["cover_price"] = position.cover_price
                response["tax"] = position.tax
                response["fee"] = position.fee

                result.append(response)

        return result

    def __format_portfolio_detail(self, position: Dict[str, Any]) -> Dict[str, Any]:
        """格式化永豐的持倉明細資訊
        @TODO 優化賦值方式, 改為用解構的方式處理

        Args:
            position (Dict[str, Any]): 永豐 list_position_detail 回傳的持倉明細資訊

        Returns:
            Dict[str, Any]: 格式化後的持倉明細資訊
        """
        if isinstance(position, sj.position.StockPositionDetail):
            response_struct = self.get_stock_position_detail_struct()
            response_struct["date"] = position.date
            response_struct["code"] = position.code
            response_struct["quantity"] = position.quantity
            response_struct["cost"] = position.price
            response_struct["pnl"] = position.pnl
            response_struct["fee"] = position.fee
            response_struct["margin_purchase_amount"] = position.margintrading_amt
            response_struct["collateral"] = position.collateral
            response_struct["trade_id"] = position.dseq

            return response_struct
        elif isinstance(position, sj.position.FuturePositionDetail):
            response_struct = self.get_future_position_detail_struct()
            response_struct["date"] = position.date
            response_struct["code"] = position.code
            response_struct["quantity"] = position.quantity
            response_struct["cost"] = position.price
            response_struct["pnl"] = position.pnl
            response_struct["fee"] = position.fee
            response_struct["trade_id"] = position.dseq

            return response_struct
        elif isinstance(position, sj.position.StockProfitDetail):
            response = self.get_stock_profit_loss_detail_struct()
            response["date"] = position.date
            response["code"] = position.code
            response["quantity"] = position.quantity
            response["trade_id"] = position.dseq
            response["fee"] = position.fee
            response["tax"] = position.tax
            response["price"] = position.price
            response["cost"] = position.price
            response["pnl"] = 0 # 永豐沒有提供明細的損益資訊

            return response
        elif isinstance(position, sj.position.FutureProfitDetail):
            response = self.get_future_profit_loss_detail_struct()
            response["date"] = position.date
            response["code"] = position.code
            response["quantity"] = position.quantity
            response["trade_id"] = position.dseq
            response["fee"] = position.fee
            response["tax"] = position.tax
            response["direction"] = Action.from_value((position.direction).upper())
            response["entry_price"] = position.entry_price
            response["cover_price"] = position.cover_price
            response["pnl"] = position.pnl

            return response
        else:
            return {}

    def fetch_portfolio(self, account_type = Literal["Stock", "Future", "Option"], fetch_detail = False, **kwargs) -> Dict[str, Any]:
        """查詢未實現損益(=目前持倉)

        Args:
            account_type (Literal["Stock", "Future", "Option"], optional): 帳號類型. 預設為 "Stock"
            fetch_detail (bool, optional): 是否取得詳細資訊. 預設為 False

        Returns:
            Dict[str, any]: 回傳結果
        """
        if account_type not in ["Stock", "Future", "Option"]:
            raise MarketCodeNotFound(account_type)
        elif account_type == "Stock":
            search_account = self.login_module.main_stock_account.source
        else:
            # 永豐的期貨與選擇權是共用的
            search_account = self.login_module.main_future_account.source

        try:
            positions = self.api.list_positions(
                search_account,
                unit = sj.constant.Unit.Share # 以股數為單位
            )
        except Exception as e:
            log_message(f"永豐查詢未實現損益失敗 {str(e)}", "broker", "error")
            raise e

        if fetch_detail:
            format_result = []

            for position in positions:
                # 查詢明細並 Format
                try:
                    detail = self.api.list_position_detail(
                        search_account, position.id
                    )
                except Exception as e:
                    log_message(f"永豐查詢未實現損益明細失敗 {str(e)}", "broker", "error")
                    raise e

                for row in detail:
                    format_response = self.__format_portfolio_detail(row)

                    if format_response:
                        format_result.append(format_response)

            ACCOUNT_EVENT.send(Event.ON_POSITION_DETAIL, response = format_result)
        else:
            format_result = self.__format_portfolio(positions)
            ACCOUNT_EVENT.send(Event.ON_POSITION, response = format_result)

        return get_response(
            status_code=SuccessCode.Success.code,
            message="查詢成功",
        )

    def fetch_portfolio_loss(self, account_type = Literal["Stock", "Future", "Option"], start_from: str = "", end_to: str = "", fetch_detail = False, **kwargs) -> Dict[str, Any]:
        """查詢已實現損益

        Args:
            account_type (Literal["Stock", "Future", "Option"], optional): 帳號類型. 預設為 "Stock"
            start_from (str, optional): 開始日期. 預設為 ""
            end_to (str, optional): 結束日期. 預設為 ""
            fetch_detail (bool, optional): 是否取得詳細資訊. 預設為 False

        Returns:
            Dict[str, Any]: 回傳結果
        """
        if account_type not in ["Stock", "Future", "Option"]:
            raise MarketCodeNotFound(account_type)
        elif account_type == "Stock":
            search_account = self.login_module.main_stock_account.source
        else:
            # 永豐的期貨與選擇權是共用的
            search_account = self.login_module.main_future_account.source

        try:
            profit_loss = self.api.list_profit_loss(
                search_account,
                begin_date = start_from,
                end_date = end_to
            )
        except Exception as e:
            log_message(f"永豐查詢已實現損益失敗 {str(e)}", "broker", "error")
            raise e

        if fetch_detail:
            format_result = []

            for row in profit_loss:
                # 查詢明細並 Format
                try:
                    detail = self.api.list_profit_loss_detail(
                        search_account, row.id
                    )
                except Exception as e:
                    log_message(f"永豐查詢已實現損益明細失敗 {str(e)}", "broker", "error")
                    raise e

                for detail_row in detail:
                    format_response = self.__format_portfolio_detail(detail_row)

                    if format_response:
                        format_result.append(format_response)

            ACCOUNT_EVENT.send(Event.ON_PROFIT_DETAIL, response = format_result)
        else:
            format_result = self.__format_portfolio(profit_loss)
            ACCOUNT_EVENT.send(Event.ON_PROFIT, response = format_result)

    def fetch_account_balance(self):
        """取得股票交割帳戶餘額"""
        obj = self.api.account_balance()

        ACCOUNT_EVENT.send(Event.ON_ACCOUNT_BALANCE, response=obj.acc_balance)

    def fetch_margin(self, **kwargs):
        """取得股票保證金"""
        obj = self.api.margin()

        ACCOUNT_EVENT.send(Event.ON_MARGIN, response=obj.today_balance)
