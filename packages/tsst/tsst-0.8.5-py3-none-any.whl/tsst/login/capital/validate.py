from pydantic import Field
from tsst.login.base_validate import BaseLogin

class CapitalLoginValidate(BaseLogin):
    """
        群益登入模組的驗證類別
    """
    account: str = Field(..., description="帳號")
    password: str = Field(..., description="密碼")