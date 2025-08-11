from pathlib import Path
import winreg


def create(path: Path):
    with winreg.OpenKey(
        key=winreg.HKEY_CURRENT_USER,
        sub_key=r"Software\Microsoft\Windows\CurrentVersion\Run",
        access=winreg.KEY_WRITE,
    ) as key:
        winreg.SetValueEx(key, path.name, "reserved", winreg.REG_SZ, str(path))
