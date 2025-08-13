# Webhook Function Logger

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/wb-fun-logger.svg)](https://badge.fury.io/py/wb-fun-logger)

一个Python函数日志记录和Webhook通知工具，支持自动记录函数执行情况并通过webhook机器人发送错误通知。

## ✨ 功能特性

- 🔍 **自动函数监控**: 自动记录函数执行时间、参数和结果
- 📝 **详细日志记录**: 使用loguru提供结构化日志输出
- 🚨 **智能错误通知**: 支持飞书机器人自动发送错误通知
- ⚡ **异步支持**: 完美支持同步和异步函数
- 🎯 **灵活配置**: 支持环境变量和配置文件双重配置
- 🔧 **错误分级**: 支持不同级别的错误处理（致命、严重、普通、警告）
- 👥 **用户通知**: 支持@特定用户或@所有人
- 🎨 **美观卡片**: 使用飞书卡片消息格式，支持颜色区分

## 📦 安装

### 从PyPI安装

```bash
pip install wb-fun-logger
```

## 🚀 快速开始

### 基本使用

```python
from webhook_logger import function_logger

@function_logger(sid="user_123", user_name="张三")
def my_function(x, y):
    return x + y

# 调用函数
result = my_function(10, 20)
```

### 异步函数支持

```python
import asyncio
from webhook_logger import function_logger

@function_logger(sid="async_task", user_name="李四")
async def async_function(data):
    await asyncio.sleep(1)
    return data.upper()

# 调用异步函数
result = await async_function("hello world")
```

### 错误处理和通知

```python
@function_logger(sid="error_test", user_name="王五", error_level=1)
def risky_function():
    # 这个函数可能会出错
    raise ValueError("这是一个测试错误")

# 当函数出错时，会自动发送飞书通知
try:
    risky_function()
except ValueError:
    print("错误已被捕获并通知")
```

## ⚙️ 配置

### 环境变量配置

创建 `.env` 文件：

```env
# 日志文件路径
LOG_FILE_PATH=/path/to/your/logs/app.log

# 飞书机器人Webhook URL
WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-url

# 机器标识
MACHINE_ID=production-server-01
```

### 配置文件

创建 `config.yaml` 文件：

```yaml
# 日志配置
log_file_path: /path/to/your/logs/app.log

# Webhook配置
webhook_url: https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-url

# 机器标识
machine_id: production-server-01

feishu:
  张三_user_id: "oc_1234567890abcdef"
  李四_user_id: "oc_0987654321fedcba"
```

## 📚 API 文档

### function_logger 装饰器

```python
@function_logger(sid, user_name=None, error_level=3)
```

**参数说明：**

- `sid` (str): 会话ID，用于标识不同的执行上下文
- `user_name` (str, optional): 用户名，用于错误通知时@用户（需要在配置中设置对应的user_id）
- `error_level` (int, optional): 错误级别
  - `0`: 致命错误 - 会@所有人
  - `1`: 严重错误
  - `2`: 普通错误
  - `3`: 普通警告

### WebhookMessager 类

```python
from webhook_logger import WebhookMessager

messager = WebhookMessager(message_target="feishu", machine_name="server-01")
```

**post_data 方法：**

```python
messager.post_data(
    msg="消息内容",
    at_user="用户名",           # 可选，对应配置文件中的用户名
    error_type=3,              # 可选，错误类型：0=致命，1=严重，2=错误，3=警告，None=普通消息
    is_success=False,          # 可选，是否为成功消息
    log_mode=False             # 可选，是否以代码块方式显示消息（适用于日志）
)
```

## 🔧 高级用法

### 自定义错误处理

```python
@function_logger(sid="critical", user_name="admin", error_level=0)
def critical_function():
    # 这个函数的错误会被标记为致命错误，会@所有人
    if some_critical_condition:
        raise SystemError("系统严重错误")
```

### 批量函数监控

```python
from webhook_logger import function_logger

class DataProcessor:
    @function_logger(sid="processing", user_name="data_team")
    def process_data(self, data):
        # 数据处理逻辑
        return processed_data
    
    @function_logger(sid="validation", user_name="data_team")
    def validate_data(self, data):
        # 数据验证逻辑
        return validation_result
```

### 手动发送通知

```python
from webhook_logger import WebhookMessager

# 创建消息发送器
messager = WebhookMessager(message_target="feishu", machine_name="server-01")

# 发送普通消息
messager.post_data(msg="任务完成", at_user="张三")

# 发送成功消息
messager.post_data(msg="数据处理完成", is_success=True)

# 发送错误消息
messager.post_data(
    msg="数据库连接失败", 
    at_user="admin", 
    error_type=1,
    log_mode=True
)

# 发送日志消息（以代码块形式显示）
messager.post_data(
    msg="详细的错误日志信息...", 
    error_type=2,
    log_mode=True
)
```

## 📋 日志格式

日志输出格式示例：

```
2024-01-15 10:30:45 - INFO - [sid=user_123] - 函数 my_function 执行成功 | 参数: (10, 20), {} | 耗时: 0.001s
2024-01-15 10:30:46 - ERROR - [sid=error_test] - 函数 risky_function 执行失败 | 参数: (), {} | 耗时: 0.002s | 错误: 这是一个测试错误
```

## 🐛 故障排除

### 常见问题

1. **Webhook URL未配置**
   ```
   错误: webhook_url is not set
   解决: 设置环境变量 WEBHOOK_URL 或在 config.yaml 中配置
   ```

2. **用户ID未配置**
   ```
   错误: 无法@用户
   解决: 在 config.yaml 中配置 feishu.用户名_user_id
   ```

3. **日志文件权限问题**
   ```
   错误: Permission denied
   解决: 确保日志目录存在且有写入权限
   ```

4. **网络连接问题**
   ```
   错误: Failed to send message
   解决: 检查网络连接和Webhook URL是否正确
   ```

### 调试模式

启用详细日志输出：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👨‍💻 作者

**Guan Xingjian** - [guanxj99@outlook.com](mailto:guanxj99@outlook.com)

