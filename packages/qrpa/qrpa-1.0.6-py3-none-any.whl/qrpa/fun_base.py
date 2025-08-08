import inspect
import os
import traceback
import socket

from datetime import datetime

from .wxwork import WxWorkBot

from typing import TypedDict

# 定义一个 TypedDict 来提供配置结构的类型提示

class ZiNiao(TypedDict):
    company: str
    username: str
    password: str

class Config(TypedDict):
    wxwork_bot_exception: str
    ziniao: ZiNiao
    auto_dir: str
    shein_store_alias: str

def log(*args, **kwargs):
    """封装 print 函数，使其行为与原 print 一致，并写入日志文件"""
    stack = inspect.stack()
    fi = stack[1] if len(stack) > 1 else None
    log_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][{os.path.basename(fi.filename) if fi else 'unknown'}:{fi.lineno if fi else 0}:{fi.function if fi else 'unknown'}] " + " ".join(map(str, args))

    print(log_message, **kwargs)

def hostname():
    return socket.gethostname()

def send_exception(config: Config, msg=None):
    error_msg = f'【{hostname()}】{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n{msg}\n'
    error_msg += f'{traceback.format_exc()}'
    WxWorkBot(config['wxwork_bot_exception']).send_text(error_msg)
    print(error_msg)
    return error_msg
