from typing import Tuple
import os
import logging

# 将项目根目录添加到sys.path
_RUNTIME_ROOT_DIR = None

# 日志存储路径
_DEFAULT_LOG_PATH = None

# 临时文件目录，主要用于文件对话
_BASE_TEMP_DIR = None

# 是否显示详细日志
_LOG_VERBOSE = False

# 日志格式
LOG_FORMAT = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"

# 通常情况下不需要更改以下内容
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format=LOG_FORMAT)


def get_runtime_root_dir():
    global _RUNTIME_ROOT_DIR
    if _RUNTIME_ROOT_DIR is None:
        # 获取当前脚本的绝对路径
        __current_script_path = os.path.abspath(__file__)
        # 将项目根目录添加到sys.path
        _RUNTIME_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__current_script_path)))
    return _RUNTIME_ROOT_DIR


def set_runtime_root_dir(runtime_root_dir):
    global _RUNTIME_ROOT_DIR
    _RUNTIME_ROOT_DIR = runtime_root_dir


def get_default_log_path():
    global _DEFAULT_LOG_PATH
    if _DEFAULT_LOG_PATH is None:
        # 日志存储路径
        _DEFAULT_LOG_PATH = os.path.join(get_runtime_root_dir(), "logs")
    return _DEFAULT_LOG_PATH


def set_default_log_path(default_log_path):
    global _DEFAULT_LOG_PATH
    _DEFAULT_LOG_PATH = default_log_path
    if not os.path.exists(_DEFAULT_LOG_PATH):
        os.mkdir(_DEFAULT_LOG_PATH)


def get_base_temp_dir():
    global _BASE_TEMP_DIR
    if _BASE_TEMP_DIR is None:
        import tempfile
        import shutil
        # 临时文件目录，主要用于文件对话
        _BASE_TEMP_DIR = os.path.join(tempfile.gettempdir(), "fuxi_ai")
        try:
            shutil.rmtree(_BASE_TEMP_DIR)
        except Exception:
            pass
        os.makedirs(_BASE_TEMP_DIR, exist_ok=True)
    return _BASE_TEMP_DIR


def set_base_temp_dir(base_temp_dir):
    global _BASE_TEMP_DIR
    _BASE_TEMP_DIR = base_temp_dir
    if not os.path.exists(_BASE_TEMP_DIR):
        os.mkdir(_BASE_TEMP_DIR)


def get_temp_dir(name: str = None) -> Tuple[str, str]:
    """
    创建一个临时目录，返回（路径，文件夹名称）
    """
    import tempfile

    if name is not None:  # 如果指定的临时目录已存在，直接返回
        path = os.path.join(get_base_temp_dir(), name)
        if os.path.isdir(path):
            return path, name

    path = tempfile.mkdtemp(dir=get_base_temp_dir())
    return path, os.path.basename(path)


def init_default_logger_config(level: int = logging.INFO, log_format: str = LOG_FORMAT):
    global logger
    logger.setLevel(level)
    logging.basicConfig(format=log_format)


def get_log_verbose():
    return _LOG_VERBOSE


def set_log_verbose(value):
    global _LOG_VERBOSE
    _LOG_VERBOSE = value


def init_nltk():
    try:
        # 配置nltk 模型存储路径
        import nltk
        nltk.data.path = [os.path.join(get_runtime_root_dir(), "nltk_data")] + nltk.data.path
    except ImportError:
        pass