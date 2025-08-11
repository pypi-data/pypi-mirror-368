from ahk.autostart import create
import subprocess
import argparse
import os
import shutil
from ahk.regenerate import regenerate as init
# 从新的 paths 模块导入路径和辅助函数
from ahk.paths import (
    PERMANENT_SCRIPTS_DIR,
    PERMANENT_RESOURCES_DIR,
    get_resource_path,
)

def sync_resources():
    """将资源文件同步到永久存储位置。"""
    source_resources = get_resource_path('ahk_resources')
    PERMANENT_RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

    # 使用 shutil.copytree 来递归复制，dirs_exist_ok=True 确保目录已存在时不会报错
    shutil.copytree(source_resources, PERMANENT_RESOURCES_DIR, dirs_exist_ok=True)
    print(f"资源已同步到: {PERMANENT_RESOURCES_DIR}")

def clean():
    """清理永久目录中所有旧的 .ahk 脚本。"""
    if PERMANENT_SCRIPTS_DIR.exists():
        # 遍历并删除所有 .ahk 文件
        for file in PERMANENT_SCRIPTS_DIR.glob("*.ahk"):
            file.unlink()

def create_autoruns():
    """为永久目录中的所有 .ahk 脚本创建开机自启动项。"""
    files = list(PERMANENT_SCRIPTS_DIR.glob("*.ahk"))
    for f in files:
        create(f) # 调用 autostart 模块中的函数创建启动项

def exec1():
    """执行永久目录中的所有 .ahk 脚本。"""
    files = list(PERMANENT_SCRIPTS_DIR.glob("*.ahk"))
    for f in files:
        os.startfile(f) # 使用系统关联的程序打开 .ahk 文件

def open_reg():
    """使用 regjump.exe 打开注册表中程序的开机启动项位置。"""
    # 注意：这里我们使用永久路径中的 regjump.exe
    regjump = PERMANENT_RESOURCES_DIR / "regjump.exe"
    if not regjump.exists():
        print(f"错误: {regjump} 未找到。请先运行一次程序以同步资源。")
        return
    # 启动子进程打开注册表编辑器，并自动接受 EULA
    subprocess.Popen(
        rf'"{regjump}" HKCU:\Software\Microsoft\Windows\CurrentVersion\Run /accepteula'
    )

def main():
    from ahk.logs import setup_logging
    setup_logging()
    """程序主入口点。"""
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="管理和运行 AutoHotkey 脚本。")
    parser.add_argument(
        "-o", "--open", action="store_true", help="打开注册表中的开机启动项位置"
    )

    args = parser.parse_args()

    # 如果用户使用了 --open 参数，则只执行打开注册表的操作
    if args.open:
        open_reg()
        return # 执行后直接退出

    # --- 主要执行流程 ---
    # 1. 同步资源文件到永久目录
    sync_resources()

    # 2. 确保用于存放脚本的永久目录存在
    PERMANENT_SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    # 3. 清理旧的脚本文件
    clean()
    # 4. 从模板重新生成新的脚本文件，并传入永久资源目录的路径
    init(output_dir=PERMANENT_SCRIPTS_DIR, resources_dir=PERMANENT_RESOURCES_DIR)
    # 5. 为新生成的脚本创建开机自启动项
    create_autoruns()
    # 6. 立即执行新生成的脚本
    exec1()

if __name__ == '__main__':
    main()
