import inspect
import os
import traceback
import socket
import hashlib
import shutil

from datetime import datetime

from .wxwork import WxWorkBot

from .RateLimitedSender import RateLimitedSender

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

def log(*args, **kwargs):
    """封装 print 函数，使其行为与原 print 一致，并写入日志文件"""
    stack = inspect.stack()
    fi = stack[1] if len(stack) > 1 else None
    log_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][{os.path.basename(fi.filename) if fi else 'unknown'}:{fi.lineno if fi else 0}:{fi.function if fi else 'unknown'}] " + " ".join(map(str, args))

    print(log_message, **kwargs)

def hostname():
    return socket.gethostname()

# ================= WxWorkBot 限频异常发送 =================
def send_exception(msg=None):
    """
    发送异常到 WxWorkBot，限制发送频率，支持异步批量
    """
    # 首次调用时初始化限频发送器
    if not hasattr(send_exception, "_wx_sender"):
        def wxwork_bot_send(message):
            bot_id = os.getenv('wxwork_bot_exception', 'ee5a048a-1b9e-41e4-9382-aa0ee447898e')
            WxWorkBot(bot_id).send_text(message)

        send_exception._wx_sender = RateLimitedSender(
            sender_func=wxwork_bot_send,
            interval=30,  # 60 秒发一次
            max_batch_size=5  # 累积 5 条立即发
        )

    # 构造异常消息
    error_msg = f'【{hostname()}】{datetime.now():%Y-%m-%d %H:%M:%S}\n{msg}\n'
    error_msg += f'{traceback.format_exc()}'
    print(error_msg)

    # 异步发送
    send_exception._wx_sender.send(error_msg)
    return error_msg

def get_safe_value(data, key, default=0):
    value = data.get(key)
    return default if value is None else value

def md5_string(s):
    # 需要先将字符串编码为 bytes
    return hashlib.md5(s.encode('utf-8')).hexdigest()

# 将windows文件名不支持的字符替换成下划线
def sanitize_filename(filename):
    # Windows 文件名非法字符
    illegal_chars = r'\/:*?"<>|'
    for char in illegal_chars:
        filename = filename.replace(char, '_')

    # 去除首尾空格和点
    filename = filename.strip(' .')

    # 替换连续多个下划线为单个
    filename = '_'.join(filter(None, filename.split('_')))

    return filename

def add_https(url):
    if url and url.startswith('//'):
        return 'https:' + url
    return url

def create_file_path(file_path):
    dir_name = os.path.dirname(file_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)  # 递归创建目录
    return file_path

def copy_file(source, destination):
    try:
        shutil.copy2(source, destination)
        print(f"文件已复制到 {destination}")
    except FileNotFoundError:
        print(f"错误：源文件 '{source}' 不存在")
    except PermissionError:
        print(f"错误：没有权限复制到 '{destination}'")
    except Exception as e:
        print(f"错误：发生未知错误 - {e}")
