from __future__ import annotations

import subprocess
import sys
import winreg
from pathlib import Path


RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_VALUE_NAME = "Mouse CMenu"


def build_startup_command(
    executable: str | None = None,
    script_path: str | Path | None = None,
    frozen: bool | None = None,
) -> str:
    executable = executable or sys.executable
    if frozen is None:
        frozen = bool(getattr(sys, "frozen", False))

    command = [executable]
    if not frozen:
        if Path(executable).name.lower() == "python.exe":
            windowless_executable = Path(executable).with_name("pythonw.exe")
            if windowless_executable.is_file():
                command[0] = str(windowless_executable)
        command.append(str(Path(script_path or sys.argv[0]).resolve()))
    return subprocess.list2cmdline(command)


def set_run_at_startup(enabled: bool, command: str | None = None) -> None:
    if enabled:
        key = winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY,
            0,
            winreg.KEY_SET_VALUE,
        )
        try:
            winreg.SetValueEx(
                key,
                RUN_VALUE_NAME,
                0,
                winreg.REG_SZ,
                command or build_startup_command(),
            )
        finally:
            winreg.CloseKey(key)
        return

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY,
            0,
            winreg.KEY_SET_VALUE,
        )
    except FileNotFoundError:
        return
    try:
        try:
            winreg.DeleteValue(key, RUN_VALUE_NAME)
        except FileNotFoundError:
            pass
    finally:
        winreg.CloseKey(key)