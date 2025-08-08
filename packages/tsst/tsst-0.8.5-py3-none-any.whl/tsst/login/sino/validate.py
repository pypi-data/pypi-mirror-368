from pydantic import Field
from tsst.login.base_validate import BaseLogin

class SinoLoginValidate(BaseLogin):
    """
        永豐登入模組的驗證類別
    """
    api_key: str = Field(..., description="API Key")
    secret_key: str = Field(..., description="Secret Key")
    ca_path: str = Field(..., description="CA Path")
    ca_password: str = Field(..., description="CA Password")