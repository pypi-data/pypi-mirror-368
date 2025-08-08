from typing import Dict, Any
from tsst.base import Base

class BaseOrder(Base):
    """
        下單元件的基底類別
    """
    def __init__(self, **kwargs):
        pass
    
    def create_order(self, **kwargs):
        """下單
        """
        raise NotImplementedError("Please implement this method")
    
    def modify_order(self, **kwargs):
        """改單
        """
        raise NotImplementedError("Please implement this method")
    
    def cancel_order(self, **kwargs):
        """刪單
        """
        raise NotImplementedError("Please implement this method")