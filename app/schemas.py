from pydantic import BaseModel
from typing import Optional

class CurrencyRateBase(BaseModel):
    base_currency: str
    target_currency: str
    buy_rate: float
    sell_rate: float
    timestamp: str

    class Config:
        orm_mode = True

class CurrencyRateInDB(CurrencyRateBase):
    id: str
    created_at: str
