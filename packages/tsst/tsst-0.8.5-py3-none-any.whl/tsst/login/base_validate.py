from pydantic import BaseModel, Field

class BaseLogin(BaseModel):
    """
        登入模組的基底類別
    """
    email: str = Field(..., description="Email")
    tsst_token: str = Field(..., description="TSST Token")
