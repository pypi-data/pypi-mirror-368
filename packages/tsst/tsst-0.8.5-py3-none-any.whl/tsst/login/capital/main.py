from typing import Dict

from tsst.event import get_event, Event, LoginEventListener, SystemEventListener
from tsst.login.base import BaseLogin
from tsst.login.capital.validate import CapitalLoginValidate
from tsst.system_code import SuccessCode
from tsst.broker.capital import handler
from tsst.error import LoginFailed
from tsst.utils import get_response, log_message

SYSTEM_EVENT = get_event("system")
LOGIN_EVENT = get_event("login")
TRADE_EVENT = get_event("trade")

class CaptialLogin(BaseLogin, LoginEventListener, SystemEventListener):
    """群益登入模組的類別
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.__bind_events()
        
        # 0 => 正式環境
        # 1 => 正式環境 SGX
        # 2 => 模擬環境
        # 3 => 模擬環境 SGX
        # 目前先只處理正式環境與模擬環境
        if self.is_simulation == 0:
            handler.m_pSKCenter.SKCenterLib_SetAuthority(0)
        else:
            handler.m_pSKCenter.SKCenterLib_SetAuthority(2)

    def __bind_events(self):
        """綁定事件
        """
        SYSTEM_EVENT.connect_via(Event.ON_SYSTEM)(self.on_system)
        LOGIN_EVENT.connect_via(Event.ON_LOGIN)(self.on_login)
        SYSTEM_EVENT.connect_via(Event.ON_RECEIVE_ACCOUNT)(self.on_receive_account)

    def run(self, params: dict) -> Dict[str, str]:
        """登入 API

        Args:
            params (dict): 參數

        Returns:
            Dict[str, str]: 回傳結果
        """
        try:
            model = CapitalLoginValidate(**params)
        except Exception as e:
            log_message(str(e), "error")
            raise LoginFailed

        nCode = handler.m_pSKCenter.SKCenterLib_Login(model.account, model.password)
        msg = "【SKCenterLib_Login】" + handler.m_pSKCenter.SKCenterLib_GetReturnCodeMessage(nCode)
        
        if nCode != 0:
            log_message(msg, "error")
            raise LoginFailed

        LOGIN_EVENT.send(Event.ON_LOGIN, response=get_response(SuccessCode.LoginSuccess.code, msg))

        # 必須要先執行 SKOrderLib_Initialize 才能執行 Order 相關功能
        handler.m_pSKOrder.SKOrderLib_Initialize()
        handler.m_pSKOrder.GetUserAccount()

        return get_response(SuccessCode.LoginSuccess.code, msg)

    def on_receive_account(self, sender: str, account: str, login_id: str, **kwargs):
        """接收帳號事件

        Args:
            sender (str): 發送者
            account: 群益回傳的帳號資料
            login_id: 群益回傳的使用者 ID
        """
        account_data = account.split(",")
        source = {
            "market": account_data[0],
            "company": account_data[1],
            "company_code": account_data[2],
            # 群益交易帳號等於分公司(4碼) + 證券帳號(7碼)
            "account": account_data[1] + account_data[3],
            "country_id": account_data[4],
            "name": account_data[5],
            "login_id": login_id
        }

        if source["market"] == "TS":
            self.set_account(
                key=source["login_id"],
                account=source["account"],
                type="Stock",
                source=source
            )
        elif source["market"] == "TF":
            self.set_account(
                key=source["login_id"],
                account=source["account"],
                type="Future",
                source=source
            )
        elif source["market"] == "OF":
            self.set_account(
                key=source["login_id"],
                account=source["account"],
                type="Option",
                source=source
            )
        else:
            pass
