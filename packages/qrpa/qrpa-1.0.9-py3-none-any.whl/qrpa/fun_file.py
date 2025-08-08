import os
import threading
import json

file_lock = threading.Lock()  # 线程锁

from datetime import date, datetime, timedelta, timezone

from .fun_base import log

def read_dict_from_file(file_path, cache_interval=3600 * 24 * 365 * 10):
    """
    从文件中读取字典。
    如果文件的修改时间未超过一个小时，则返回字典；否则返回 None。

    :param file_path: 文件路径
    :return: 字典或 None
    """
    with file_lock:  # 使用锁保护文件操作
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {}

        # 获取文件的最后修改时间
        modification_time = os.path.getmtime(file_path)
        modification_time = datetime.fromtimestamp(modification_time)

        # 获取当前时间
        current_time = datetime.now()

        interval = current_time - modification_time
        log(f'缓存文件 {file_path} 缓存时长 {timedelta(seconds=int(cache_interval))} 已过时长 {interval}')

        # 判断文件的修改时间是否超过一个小时
        if interval <= timedelta(seconds=int(cache_interval)):
            # 如果未超过一个小时，则读取文件内容
            with open(file_path, "r", encoding='utf-8') as file:
                return json.load(file)
        else:
            # 如果超过一个小时，则返回 None
            return {}

def write_dict_to_file(file_path, data):
    """
    将字典写入文件。

    :param file_path: 文件路径
    :param data: 要写入的字典
    """
    with file_lock:  # 使用锁保护文件操作
        # 确保目标文件夹存在
        dir_name = os.path.dirname(file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)  # 递归创建目录

        with open(file_path, 'w', encoding='utf-8') as f:
            # 使用 json.dump() 并设置 ensure_ascii=False
            json.dump(data, f, ensure_ascii=False, indent=4)

def read_dict_from_file_ex(file_path, key, cache_interval=3600 * 24 * 365 * 10, default='dict'):
    """
    从 JSON 文件中读取指定键的值。

    :param file_path: JSON 文件路径
    :param key: 要读取的键
    :param default: 如果文件不存在、解析失败或键不存在时返回的默认值
    :return: 对应键的值，或 default
    """
    with file_lock:  # 使用锁保护文件操作
        if not os.path.exists(file_path):
            return {} if default == 'dict' else []

        # 获取文件的最后修改时间
        modification_time = os.path.getmtime(file_path)
        modification_time = datetime.fromtimestamp(modification_time)

        # 获取当前时间
        current_time = datetime.now()

        interval = current_time - modification_time
        log(f'缓存文件 {file_path} 缓存时长 {timedelta(seconds=cache_interval)} 已过时长 {interval}')

        # 判断文件的修改时间是否超过一个小时
        if interval <= timedelta(seconds=cache_interval):
            # 如果未超过一个小时，则读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get(key, {})
        else:
            # 如果超过一个小时，则返回 None
            return {} if default == 'dict' else []

def write_dict_to_file_ex(file_path, data, update_keys=None):
    """
    将字典写入文件，可选择性地只更新指定键。

    :param file_path: 文件路径
    :param data: 要写入的字典数据
    :param update_keys: 可选，需要更新的键列表。如果为None，则替换整个文件内容
    """
    with file_lock:  # 使用锁保护文件操作
        # 确保目标文件夹存在
        dir_name = os.path.dirname(file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)  # 递归创建目录

        # 如果指定了update_keys，先读取现有数据然后合并
        if update_keys is not None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_data = {}

            # 只更新指定的键
            for key in update_keys:
                if key in data:
                    existing_data[key] = data[key]
            data = existing_data

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

######################################################################################################
def getTaskStoreKey(key_id, store_name):
    return f'{key_id}_{store_name}'

def generate_progress_file(config, key_id):
    return f'{config.auto_dir}/progress/progress_{key_id}.json'

def get_progress_index_ex(config, task_key, store_name):
    task_store_key = getTaskStoreKey(task_key, store_name)
    progress_file = generate_progress_file(config, task_key)
    dict = read_dict_from_file(progress_file)
    if len(dict) > 0:
        count = 0
        for key, value in dict.items():
            if key == task_store_key:
                return count
            count += 1
    return len(dict)

def get_progress_json_ex(config, task_key, store_name):
    task_store_key = getTaskStoreKey(task_key, store_name)
    progress_file = generate_progress_file(config, task_key)
    dict = read_dict_from_file_ex(progress_file, task_store_key)
    if len(dict) > 0:
        return dict[0] == 1
    else:
        length = get_progress_index_ex(config, task_key, store_name)
        write_dict_to_file_ex(progress_file, {task_store_key: [0, length + 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}, [task_store_key])
    return False

def done_progress_json_ex(config, task_key, store_name):
    task_store_key = getTaskStoreKey(task_key, store_name)
    progress_file = generate_progress_file(config, task_key)
    length = get_progress_index_ex(config, task_key, store_name)
    write_dict_to_file_ex(progress_file, {task_store_key: [1, length + 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}, [task_store_key])

def check_progress_json_ex(config, task_key, just_store_username=None):
    progress_file = generate_progress_file(config, task_key)
    dict = read_dict_from_file(progress_file)
    if len(dict) > 0:
        for task_store_key, data_list in dict.items():
            if just_store_username and len(just_store_username) > 0:
                if all([store_username not in task_store_key for store_username in just_store_username]):
                    continue
            if 'run_' not in task_store_key and int(data_list[0]) == 0:
                log(task_store_key, just_store_username)
                return False
    else:
        log(f"进度文件不存在或为空: {progress_file}")
    return True
