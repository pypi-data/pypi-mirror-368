import sys
from pathlib import Path
import os

# --- 永久存储路径 ---
# 主应用程序数据目录，例如 C:\Users\YourUser\AppData\Local\soda-ahk
APP_DATA_DIR = Path(os.getenv("LOCALAPPDATA")) / "soda-ahk"
# 用于存放生成的 .ahk 脚本的永久目录
PERMANENT_SCRIPTS_DIR = APP_DATA_DIR / "scripts"
# 用于存放同步的 .exe 等资源的永久目录
PERMANENT_RESOURCES_DIR = APP_DATA_DIR / "resources"
# 日志文件路径
LOG_FILE_PATH = APP_DATA_DIR / "soda-ahk.log"


def get_resource_path(relative_path: str) -> Path:
    """
    获取捆绑资源的绝对路径。
    适用于开发环境和 PyInstaller 打包后的环境。
    """
    base_path = Path(__file__).resolve().parent.parent
    if getattr(sys, "frozen", False):
        # PyInstaller 创建一个临时文件夹，并将其路径存储在 _MEIPASS 中
        base_path = Path(sys._MEIPASS)

    return base_path / relative_path
