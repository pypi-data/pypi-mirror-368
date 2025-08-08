from pydantic import Field
from typing import Literal, Any, Dict
from tsst.trade.order.base_validate import BaseCreateOrder

# 群益下單模組參數的映射表
MAPPER_TABLE = {
    "action": {
        "Buy": 0,
        "Sell": 1
    },
    "order_lot": {
        "Common": 0,
        "Fixing": 1,
        "Odd": 2,
        "IntradayOdd": 2
    },
    "order_cond": {
        "Cash": 0,
        "MarginTrading": 1,
        "ShortSelling": 2
    },
    "order_type": {
        "ROD": 0,
        "IOC": 1,
        "FOK": 2
    },
    "price_type": {
        "LMT": 2,
        "MKT": 1,
        "MKP": 1
    },
    "octype": {
        "Auto": 2,
        "New": 0,
        "Cover": 1,
        "DayTrade": 2
    }
}

class CapitalCreateStockOrder(BaseCreateOrder):
    """群益股票下單模組的股票訂單參數
    """
    # 群益文件中所寫的 struct STOCKORDER 的參數
    # {
    # 	BSTR	bstrFullAccount;	//證券帳號，分公司代碼＋帳號7碼
    # 	BSTR	bstrStockNo;		//委託股票代號
    # 	SHORT	sPrime;			//0:上市上櫃1:興櫃
    # 	SHORT	sPeriod;			//0:盤中 1:盤後 2:零股
    # 	SHORT	sFlag;			//0:現股 1:融資 2:融券 3:無券 
    # 	SHORT	sBuySell;			//0:買進 1:賣出
    # 	BSTR	bstrPrice;			//委託價格，「M」表示參考價（昨收價）
    # 	LONG	nQty;			//整股交易為張數，如果是零股則為股數
    #   LONG	nTradeType;			//[證券逐筆交易]0:ROD ; 1:IOC ; 2:FOK
    # 	LONG	nSpecialTradeType;	//[證券逐筆交易]1:市價; 2:限價 
    # (市價單之委託價格Price請給0; 限價單之委託價格Price 不可為0)
    # };
    prime: Literal[0, 1] = Field(0, description="0:上市上櫃1:興櫃")

    # 對應 sPeriod
    order_lot: Literal["Common", "Fixing", "Odd", "IntradayOdd"] = Field("Common", description="Common:一般; Fixing:定盤; Odd:零股; IntradayOdd:盤後零股")

    # 對應 sFlag
    order_cond: Literal["Cash", "MarginTrading", "ShortSelling"] = Field("Cash", description="Cash:現股; MarginTrading:融資; ShortSelling:融券")
    
    def to_capital_dict(self) -> Dict[str, Any]:
        """將參數轉換成 for 群益下單的 dict

        Returns:
            Dict[str, Any]: 群益下單的 dict
        """
        return {
            "sPrime": self.prime,
            "sPeriod": MAPPER_TABLE["order_lot"][self.order_lot],
            "sFlag": MAPPER_TABLE["order_cond"][self.order_cond],
            "sBuySell": MAPPER_TABLE["action"][self.action],
            "bstrPrice": str(self.price),
            "nQty": int(self.quantity),
            "nTradeType": MAPPER_TABLE["order_type"][self.order_type],
            "nSpecialTradeType": MAPPER_TABLE["price_type"][self.price_type]
        }

class CapitalCreateFutureOrder(BaseCreateOrder):
    """群益股票下單模組的期貨訂單參數
    """
    # 群益文件中所寫的 struct FUTUREORDER
    # {
    # 	BSTR	bstrFullAccount;	//期貨帳號，分公司代碼＋帳號7碼
    # 	BSTR	bstrStockNo;		//委託期權代號
    # 	SHORT	sTradeType;		//0:ROD  1:IOC  2:FOK
    # 	SHORT	sBuySell;			//0:買進 1:賣出
    # 	SHORT	sDayTrade;		//當沖0:否 1:是，可當沖商品請參考交易所規定。
    # 	SHORT	sNewClose;		//新平倉，0:新倉 1:平倉 2:自動{新期貨、選擇權使用}
    # 	BSTR	bstrPrice;			//委託價格(IOC and FOK，可用「M」表示市價，「P」表示範圍市價)　　　　　　　　　　　　
    # 	LONG	nQty;			//交易口數	
    # 	SHORT	sReserved;		//{期貨委託SendFutureOrderCLR適用}盤別，0:盤中(T盤及T+1盤)；1:T盤預約
    # };
    # 對應 sNewClose
    octype: Literal["Auto", "New", "Cover", "DayTrade"] = Field("Auto", description="Auto:自動; New:新倉; Cover:平倉; DayTrade:當沖")

    reserved: Literal[0, 1] = Field(0, description="盤別 0:盤中(T盤及T+1盤)；1:T盤預約")

    def to_capital_dict(self) -> Dict[str, Any]:
        """將參數轉換成 for 群益下單的 dict

        Returns:
            Dict[str, Any]: 群益下單的 dict
        """
        if self.price_type == "MKT":
            # 市價
            self.price = "M"
        elif self.price_type == "MKP":
            # 範圍市價
            self.price = "P"
        else:
            self.price = str(self.price)

        return {
            "sTradeType": MAPPER_TABLE["order_type"][self.order_type],
            "sBuySell": MAPPER_TABLE["action"][self.action],
            "sDayTrade": 1 if self.order_type == "DayTrade" else 0,
            "sNewClose": MAPPER_TABLE["octype"][self.octype],
            "bstrPrice": self.price,
            "nQty": int(self.quantity),
            "sReserved": self.reserved
        }

