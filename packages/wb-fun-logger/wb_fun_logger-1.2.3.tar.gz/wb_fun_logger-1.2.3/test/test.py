import os
import sys

# 添加src目录到Python路径
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

from webhook_logger import function_logger
from webhook_logger.utils.create_webhook_data import WebhookMessager

@function_logger(sid="test", user_name="xingjian", error_level=3)
def test_function():
    print("test")
    webhook_messager = WebhookMessager(message_target="feishu", machine_name="test")
    webhook_messager.post_data(msg="test", at_user="xingjian", error_type=None, is_success=True, log_mode=False)
    raise Exception("test error")

if __name__ == "__main__":
    test_function()