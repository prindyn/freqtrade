from pydantic import BaseModel
from typing import List, Optional


class FreqtradeConfigBase(BaseModel):
    exchange_name: str
    api_key: str
    api_secret: str
    dry_run: bool = True
    stake_currency: str
    stake_amount: float
    strategy: Optional[str] = "SampleStrategy"  # Defaulting to a common example

    # Optional pair whitelist, will default in helper if not provided
    pair_whitelist: Optional[List[str]] = None

    # Telegram - basic fields
    telegram_enabled: bool = False
    telegram_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    # Fields for Freqtrade's internal API server,
    # These are typically not set by the end-user directly for basic setup,
    # but are part of the config.json that freqtrade uses.
    # We will set defaults for these in the helper function.
    # api_server_enabled: bool = True # Defaulted in helper
    # api_server_listen_ip_address: str = "0.0.0.0" # Defaulted in helper
    # api_server_listen_port: int = 8080 # Defaulted in helper, internal to container
    # api_server_username: Optional[str] = "user" # Defaulted in helper
    # api_server_password: Optional[str] = "password" # Defaulted in helper

    # Other common Freqtrade settings that might be useful
    max_open_trades: Optional[int] = 3  # Default, can be overridden
    # timeframe: Optional[str] = "5m" # Users might want to set this

    class Config:
        orm_mode = True  # if you plan to use it with an ORM


# Example for creating/updating a config via API
class FreqtradeConfigCreate(FreqtradeConfigBase):
    pass


# Example for reading a config (e.g., from DB or API response)
class FreqtradeConfig(FreqtradeConfigBase):
    bot_id: Optional[str] = None  # Could be added when storing/retrieving

    class Config:
        orm_mode = True
