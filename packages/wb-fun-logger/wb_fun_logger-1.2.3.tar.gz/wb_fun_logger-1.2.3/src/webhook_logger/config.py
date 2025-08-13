import os
from typing import Any
from webhook_logger.utils.config_loader import init_config

class Config:
    def __init__(self):
        self.config_dict = init_config()

    def get(self, key: str, env_var: str = None, default: Any = None) -> Any:
        if env_var:
            value = os.getenv(env_var)
            if value is not None:
                return value

        value = self.config_dict.get(key)
        if value is not None:
            return value
        
        return default

def get_config():
    return Config()

CONFIG = Config()