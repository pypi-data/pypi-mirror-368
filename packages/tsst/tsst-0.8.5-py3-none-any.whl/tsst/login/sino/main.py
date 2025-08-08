import shioaji as sj

from typing import Dict, Any, Literal

import tsst
import tsst.error
from tsst.event import get_event, Event, LoginEventListener, SystemEventListener
from tsst.login.base import BaseLogin
from tsst.login.sino.validate import SinoLoginValidate
from tsst.system_code import SuccessCode
from tsst.utils import get_response, log_message

SYSTEM_EVENT = get_event("system")
LOGIN_EVENT = get_event("login")

class SinoLogin(BaseLogin, LoginEventListener, SystemEventListener):
    """
        永豐登入模組的類別
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.__bind_event()
        self.__init_sino_api()

    @property
    def api(self):
        """取得永豐 API
        """
        return self._api

    def __bind_event(self):
        """綁定事件
        """
        SYSTEM_EVENT.connect_via(Event.ON_SYSTEM)(self.on_system)
        LOGIN_EVENT.connect_via(Event.ON_LOGIN)(self.on_login)

    def __init_sino_api(self):
        """初始化永豐 API
        """
        self._api = sj.Shioaji(
            simulation=self.is_simulation
        )
    
    def run(self, params: dict) -> Dict[str, str]:
        """登入 API

        Args:
            params (dict): 參數

        Returns:
            Dict[str, str]: 登入成功或失敗
        """
        try:
            model = SinoLoginValidate(**params)
        except Exception as e:
            raise tsst.error.LoginFailed

        try:
            accounts = self.api.login(
                api_key=model.api_key,
                secret_key=model.secret_key
            )

            self.api.activate_ca(
                ca_path=model.ca_path,
                ca_passwd=model.ca_password
            )
        except Exception as e:
            log_message(f"永豐登入失敗 {str(e)}", "broker", "error")
            raise tsst.error.LoginFailed

        # 儲存交易帳號
        for account in accounts:
            account_type = "Stock" if isinstance(account, sj.account.StockAccount) else "Future"
            self.set_account(
                key=account.account_id,
                account=account.account_id,
                type=account_type,
                source=account
            )

        log_message("永豐登入成功")

        LOGIN_EVENT.send(Event.ON_LOGIN, response=get_response(SuccessCode.LoginSuccess.code))

        return get_response(SuccessCode.LoginSuccess.code)

