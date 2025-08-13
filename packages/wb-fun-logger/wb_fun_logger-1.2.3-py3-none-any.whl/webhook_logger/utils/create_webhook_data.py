import re
import requests

from typing import Any, Dict

class WebhookMessager:
    def __init__(self, message_target: str, machine_name: str):
        """
        message_target: 消息发送目标, 例如: feishu
        """
        from webhook_logger.config import get_config
        self.message_target = message_target
        self.machine_name = machine_name
        self.config = get_config()
          
    def __create_data(self, 
                    msg: Any, 
                    at_user_id: str = None, 
                    error_type: int | None = None,
                    is_success: bool = False,
                    machine_name: str = None,
                    log_mode: bool = False,
                    ):
        """
        data: 消息数据
        user_id: 用户ID
        is_error: 是否是错误消息
        """
        target_choice = {
            "feishu": self.__create_feishu_data,
        }

        return target_choice[self.message_target](msg=msg, machine_name=machine_name, error_type=error_type, at_user_id=at_user_id, is_success=is_success, log_mode=log_mode)

    def __strip_ansi_codes(self,text: str) -> str:
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def __build_feishu_card_content(
        self,
        machine_name: str,
        msg: str,
        title: str,
        at_user_id: str = None,
        log_mode: bool = False
    ):
        msg = self.__strip_ansi_codes(str(msg))  # 清理颜色控制符

        if log_mode:
            content = f"""**Machine**: {machine_name}
**Title**: {title}

```text
{msg}
```"""
        else:
            content = f"""**Machine**: {machine_name}
**Message**: {msg}"""

        elements = [{"tag": "markdown", "content": content}]

        if at_user_id:
            if at_user_id == "all":
                elements.append({"tag": "markdown", "content": "<at id=all></at>"})
            else:
                elements.append({"tag": "markdown", "content": f"<at id={at_user_id}></at>"})

        # 根据 title 设置颜色模板
        color_map = {
            "致命错误": "red",
            "严重错误": "orange",
            "错误": "orange",
            "警告": "yellow",
            "Success!": "green",
            "Info": "blue"
        }
        template_color = color_map.get(title, "blue")

        return {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "template": template_color,
                    "title": {"tag": "plain_text", "content": title}
                },
                "elements": elements
            }
        }
    
    def __create_feishu_data(
        self,        
        msg: Any,
        machine_name: str,
        error_type: int = None,
        at_user_id: str = None,
        is_success: bool = False,
        log_mode: bool = False
        ):
        """
        向飞书发送通知消息

        Args:
            url: 飞书 webhook url
            machine_name: 机器名称  
            msg: 日志或文本内容
            error_type: 0=致命，1=严重，2=错误，3=警告，None=普通消息
            at_user: 配置中的用户名 key
            log_mode: 是否以代码块方式显示消息（适用于日志）
        """

        # 致命错误默认 @所有人
        if error_type == 0:
            at_user_id = "all"

        # 构建标题
        error_map = {0: "致命错误", 1: "严重错误", 2: "错误", 3: "警告"}
        title = "Success!" if is_success else error_map.get(error_type, "Info")

        # 构建消息体
        data = self.__build_feishu_card_content(
            machine_name=machine_name,
            msg=msg,
            title=title,
            at_user_id=at_user_id,
            log_mode=log_mode
        )

        return data

    def post_data(self, 
                  msg:Any,
                  at_user:str = None,
                  error_type:int | None = None,
                  is_success: bool = False,
                  log_mode: bool = False,
                  ):
        """
        发送消息
        """
        url = self.config.get("webhook_url", env_var="WEBHOOK_URL")
        machine_name = self.config.get("machine_id", env_var="MACHINE_ID")
        at_user_id = self.config.get("feishu", "").get(f"{at_user}_user_id", "") if at_user else ""
        data = self.__create_data(msg=msg, machine_name=machine_name, error_type=error_type, at_user_id=at_user_id, is_success=is_success, log_mode=log_mode)
        if not url:
            raise ValueError("webhook_url is not set")
        
        response = requests.post(url, json=data)
        if response.status_code != 200:
            raise ValueError("Failed to send message")