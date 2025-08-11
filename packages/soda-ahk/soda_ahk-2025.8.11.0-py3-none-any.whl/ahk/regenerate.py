from pathlib import Path
import sys
import winreg
import logging

# 从新的 paths 模块导入路径和辅助函数
from ahk.paths import (
    get_resource_path,
    PERMANENT_SCRIPTS_DIR,
    PERMANENT_RESOURCES_DIR,
)
import shutil


home_folder = Path.home()
python_path = Path(sys.executable).resolve().parent
start_folder = home_folder.joinpath(
    r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
)


CURRENT = Path(__file__).resolve().parent

# 模板文件仍然从打包的资源中读取
templates_dir = get_resource_path("ahk_script_templates")


def resolve_ahk_chm():
    script_type = ""
    script_exec = ""
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ".ahk") as key:
            script_type = winreg.QueryValue(key, "")
    except OSError:
        logging.error(".ahk ext not found in registry")
    try:
        # \AutoHotkeyScript\Shell\Open\Command
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, script_type) as key:
            script_exec = winreg.QueryValue(key, r"Shell\Open\Command")
    except OSError:
        logging.error("query exec failed")
    logging.info("current exec: %s", script_exec)

    if script_exec != "":
        ahk_exe = script_exec.split(" ")[0]
        # need to remove start " and end "
        ahk_exe = ahk_exe[1:-1]
        chm = (
            Path(ahk_exe)
            .resolve()
            .parent.parent.joinpath("v2")
            .joinpath("AutoHotkey.chm")
        )
        if chm.exists():
            return chm

    logging.error("无法通过注册表找到帮助文件，将使用默认路径。")
    return home_folder.joinpath(r"scoop\apps\autohotkey\current\v2\AutoHotkey.chm")


def regenerate(output_dir: Path, resources_dir: Path):
    """
    从模板生成 .ahk 脚本并将其写入指定的输出目录。
    现在使用传入的 resources_dir 来构建模板变量。
    """
    # 将模板变量的定义移到函数内部，以便使用传入的 resources_dir
    vars = {
        "resources": resources_dir,
        "cursor": resources_dir / "ahk.cur",
        "AutoHotkey_chm": resolve_ahk_chm(),
        "desktop": home_folder.joinpath("Desktop"),
    }

    logging.info(f"开始生成脚本到: {output_dir}")
    if not templates_dir.exists():
        logging.error(f"模板目录不存在: {templates_dir}")
        return

    for t in templates_dir.glob("*.ahk"):
        try:
            template_content = t.read_text(encoding="utf-8")
            for k, v in vars.items():
                v = str(v).replace('\\', '/')
                template_content = template_content.replace('{' + k + '}', v)
            # 将生成的文件写入永久目录
            output_file = output_dir.joinpath(t.name)
            output_file.write_text(template_content, encoding="utf-8")
            logging.info(f"已生成: {output_file}")
        except Exception as e:
            logging.error(f"处理 {t.name} 时出错: {e}")


if __name__ == "__main__":
    # 当此脚本直接运行时，使用永久目录进行测试
    # 这确保了测试行为与实际运行行为一致
    PERMANENT_SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    PERMANENT_RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

    # 注意：为了让这个测试正常工作，ahk_resources 必须存在于项目根目录
    # 我们可以手动同步一下用于测试
    test_source_resources = Path(__file__).parent.parent / "ahk_resources"
    if test_source_resources.exists():
        shutil.copytree(
            test_source_resources, PERMANENT_RESOURCES_DIR, dirs_exist_ok=True
        )

    regenerate(PERMANENT_SCRIPTS_DIR, PERMANENT_RESOURCES_DIR)
    print(f"测试脚本已生成到: {PERMANENT_SCRIPTS_DIR}")
