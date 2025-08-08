from tsst.base import Base

class BaseQuote(Base):
    """
        報價元件的基底類別
    """
    def __init__(self, **kwargs):
        pass

    def subscribe(self, **kwargs):
        """訂閱報價
        """
        raise NotImplementedError("尚未實作訂閱報價的功能")

    def unsubscribe(self, **kwargs):
        """取消訂閱報價
        """
        raise NotImplementedError("尚未實作取消訂閱報價的功能")

    def backfilling(self, **kwargs):
        """回補即時行情報價
        """
        raise NotImplementedError("尚未實作即時行情報價的功能")

    def get_kbar(self, *args, **kwargs):
        """取得 K 線資料
        """
        raise NotImplementedError("尚未實作取得 K 線資料的功能")
    