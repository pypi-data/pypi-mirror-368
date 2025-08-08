from typing import Dict, Any

class BaseAccount:
    """帳務模組的基底類別
    """
    def __init__(self):
        pass

    def fetch_account_balance(self, **kwargs):
        """取得帳務資訊
        """
        raise NotImplementedError("Please implement this method")

    def fetch_margin(self, **kwargs):
        """取得保證金資訊
        """
        raise NotImplementedError("Please implement this method")

    def fetch_portfolio(self, **kwargs):
        """取得未實現損益(=目前持倉)
        """
        raise NotImplementedError("Please implement this method")

    def fetch_portfolio_loss(self, **kwargs):
        """取得已實現損益
        """
        raise NotImplementedError("Please implement this method")

    def get_stock_profit_loss_summary_struct(self, **kwargs) -> Dict[str, Any]:
        """取得股票損益摘要的資料結構

        Returns:
            Dict[str, Any]: 股票損益摘要的資料結構
        """
        return {
            "trade_id": None, # 委託書號
            "code": None, # 股票代碼
            "quantity": 0, # 數量
            "price": None, # 價格
            "pnl": 0, # 損益
            "pr_rate": 0, # 損益率
            "cond": None, # 現股/融資/融券
            "date": None, # 交易日期
        }

    def get_future_profit_loss_summary_struct(self, **kwargs) -> Dict[str, Any]:
        """取得期貨損益摘要的資料結構

        Returns:
            Dict[str, Any]: 期貨損益摘要的資料結構
        """
        return {
            "code": None, # 期貨代碼
            "quantity": 0, # 數量
            "pnl": 0, # 損益
            "date": None, # 交易日期
            "entry_price": None, # 進場價格
            "cover_price": None, # 出場價格
            "tax": 0, # 稅金
            "fee": 0, # 手續費
        }

    def get_stock_profit_loss_detail_struct(self, **kwargs) -> Dict[str, Any]:
        """取得股票損益明細的資料結構

        Returns:
            Dict[str, Any]: 股票損益明細的資料結構
        """
        return {
            "date": None, # 交易日期
            "code": None, # 股票代碼
            "quantity": 0, # 數量
            "trade_id": None, # 委託書號
            "fee": 0, # 手續費
            "tax": 0, # 稅金
            "price": None, # 成交單價
            "cost": None, # 成本
            "pnl": 0, # 損益
        }
    
    def get_future_profit_loss_detail_struct(self, **kwargs) -> Dict[str, Any]:
        """取得期貨損益明細的資料結構
        
        Returns:
            Dict[str, Any]: 期貨損益明細的資料結構
        """
        return {
            "date": None, # 交易日期
            "code": None, # 期貨代碼
            "quantity": 0, # 數量
            "trade_id": None, # 委託書號
            "fee": 0, # 手續費
            "tax": 0, # 稅金
            "direction": None, # 買賣別
            "entry_price": None, # 進場價格
            "cover_price": None, # 出場價格
            "pnl": 0, # 損益
        }

    def get_stock_position_summary_struct(self, **kwargs) -> Dict[str, Any]:
        """取得股票持倉摘要的資料結構

        Returns:
            Dict[str, Any]: 股票持倉摘要的資料結構
        """
        # @TODO cond 永豐還有餘額交割與興櫃, 這邊到時候要看群益的怎麼處理
        return {
            "code": None, # 股票代碼
            "quantity": 0, # 數量
            "avg_price": None, # 均價
            "pnl": 0, # 損益
            "cond": None, # 現股/融資/融券
            "margin_purchase_amount": 0, # 融資金額
            "collateral": 0, # 擔保品
            "short_sale_margin": 0, # 保證金
            "interest": 0, # 利息
        }

    def get_future_position_summary_struct(self, **kwargs) -> Dict[str, Any]:
        """取得期貨持倉摘要的資料結構

        Returns:
            Dict[str, Any]: 期貨持倉摘要的資料結構
        """
        return {
            "code": None, # 期貨代碼
            "quantity": 0, # 數量
            "avg_price": None, # 均價
            "pnl": 0, # 損益
        }

    def get_stock_position_detail_struct(self, **kwargs) -> Dict[str, Any]:
        """取得股票持倉明細摘要的資料結構

        Returns:
            Dict[str, Any]: 股票持倉明細摘要的資料結構
        """
        return {
            "date": None, # 交易日期
            "code": None, # 股票代碼
            "quantity": 0, # 數量
            "cost": None, # 付出成本
            "pnl": 0, # 損益
            "fee": 0, # 手續費
            "margin_purchase_amount": 0, # 融資金額
            "collateral": 0, # 擔保品
            "trade_id": None, # 委託書號
        }
    
    def get_future_position_detail_struct(self, **kwargs) -> Dict[str, Any]:
        """取得期貨持倉明細摘要的資料結構

        Returns:
            Dict[str, Any]: 期貨持倉明細摘要的資料結構
        """
        return {
            "date": None, # 交易日期
            "code": None, # 期貨代碼
            "quantity": 0, # 數量
            "cost": None, # 付出成本
            "pnl": 0, # 損益
            "fee": 0, # 手續費
            "trade_id": None, # 委託書號
        }