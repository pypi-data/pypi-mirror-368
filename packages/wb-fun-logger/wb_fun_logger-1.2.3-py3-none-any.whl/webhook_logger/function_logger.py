import time
import asyncio
import functools
import traceback
import json
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

from webhook_logger.config import CONFIG
from webhook_logger.utils.create_webhook_data import WebhookMessager

load_dotenv()

log_path = CONFIG.get("log_file_path", env_var="LOG_FILE_PATH")

logger.configure(
    handlers=[
        {
            "sink": log_path,
            "rotation": "1 day",
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> - <level>{level}</level> - [{extra}] - <level>{message}</level>",
            "enqueue": True,
            "backtrace": True,
        }
    ]
)


def _safe_str(obj, max_len=2000, sid=None, func_name=None, when="runtime", save_full_params=True):
    """
    用于生成安全的字符串用于飞书的提示以及log的保存，同时会全量记录。
    Args:
        obj: 需要转换的字典或者字符串
        max_len: 最大长度
        sid: 会话id
        func_name: 函数名
        when: 时间
    Returns:
        s: 转换后的字符串
    """
    try:
        s = json.dumps(obj, ensure_ascii=False) if not isinstance(obj, str) else obj
    except Exception:
        s = str(obj)

    if len(s) > max_len:
        full_dir = Path("logs/full_params")
        full_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"{sid or 'unknown'}_{func_name or 'func'}_{when}.txt"
        full_path = full_dir / file_name
        if save_full_params:
            full_path.write_text(s, encoding="utf-8")
        return f"{s[:max_len]}... [TRUNCATED, saved full content to {full_path}]"
    return s


def function_logger(sid, user_name=None, error_level=3, save_full_params=True):
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            logger_context = logger.bind(sid=sid)
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger_context.info(
                    f"函数 {func.__qualname__} 执行成功 | 参数: {_safe_str(args, sid=sid, func_name=func.__qualname__, when='runtime', save_full_params=save_full_params)}, {_safe_str(kwargs, sid=sid, func_name=func.__qualname__, when='runtime', save_full_params=save_full_params)} | 耗时: {duration:.3f}s"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                error_msg = f"函数 {func.__qualname__} 执行失败 | 参数: {_safe_str(args, sid=sid, func_name=func.__qualname__, when='error', save_full_params=save_full_params)}, {_safe_str(kwargs, sid=sid, func_name=func.__qualname__, when='error', save_full_params=save_full_params)} | 耗时: {duration:.3f}s | 错误: {str(e)}"
                logger_context.exception(error_msg)
                logger_context.error(f"错误 traceback: {traceback.format_exc()}")

                try:
                    webhook_messager = WebhookMessager(
                        message_target="feishu",
                        machine_name=CONFIG.get("machine_id", env_var="MACHINE_ID")
                    )
                    webhook_messager.post_data(
                        msg=error_msg,
                        at_user=user_name,
                        error_type=error_level,
                        is_success=False,
                        log_mode=True
                    )
                except Exception as feishu_error:
                    logger_context.error(f"发送飞书通知失败: {str(feishu_error)}")
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            logger_context = logger.bind(sid=sid)
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger_context.info(
                    f"函数 {func.__qualname__} 执行成功 | 参数: {_safe_str(args, sid=sid, func_name=func.__qualname__, when='runtime', save_full_params=save_full_params)}, {_safe_str(kwargs, sid=sid, func_name=func.__qualname__, when='runtime', save_full_params=save_full_params)} | 耗时: {duration:.3f}s"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                error_msg = f"函数 {func.__qualname__} 执行失败 | 参数: {_safe_str(args, sid=sid, func_name=func.__qualname__, when='error', save_full_params=save_full_params)}, {_safe_str(kwargs, sid=sid, func_name=func.__qualname__, when='error', save_full_params=save_full_params)} | 耗时: {duration:.3f}s | 错误: {str(e)}"
                logger_context.exception(error_msg)
                logger_context.error(f"错误 traceback: {traceback.format_exc()}")

                try:
                    webhook_messager = WebhookMessager(
                        message_target="feishu",
                        machine_name=CONFIG.get("machine_id", env_var="MACHINE_ID")
                    )
                    webhook_messager.post_data(
                        msg=error_msg,
                        at_user=user_name,
                        error_type=error_level,
                        is_success=False,
                        log_mode=True
                    )
                except Exception as feishu_error:
                    logger_context.error(f"发送飞书通知失败: {str(feishu_error)}")
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
