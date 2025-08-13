import os
import yaml
from dotenv import load_dotenv

CONFIG_PATH = os.path.join(os.getcwd(), 'config.yaml')
ENV_PATH = os.path.join(os.getcwd(), '.env')

_config = None
_env_loaded = False

def load_env():
    global _env_loaded
    if not _env_loaded:
        if not os.path.exists(ENV_PATH):
            # raise FileNotFoundError(f"[function_logger] Missing .env file at: {ENV_PATH}")
            print(f"[function_logger] Missing .env file at: {ENV_PATH}")
        load_dotenv(dotenv_path=ENV_PATH)
        _env_loaded = True

def load_config():
    global _config
    if _config is None:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                _config = yaml.safe_load(f)
        else:
            _config = {}  # or None if you prefer
    return _config

def init_config():
    """
    初始化配置：
    - 如果没有 .env，抛出错误；
    - 如果没有 config.yaml，返回空 dict；
    - 返回 config（即 config.yaml 的内容）
    """
    load_env()
    return load_config()
