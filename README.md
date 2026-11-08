<div align="center">
  <img src="docs/ico.ico" alt="Mouse CMenu icon" width="96" height="96" />
  <h1>Mouse CMenu</h1>
  <p><strong>A lightweight Windows system-tray launcher for a custom mouse-driven application menu.</strong></p>
  <p>
    <img alt="Version 1.2.0" src="https://img.shields.io/badge/version-1.2.0-0078D4?style=flat-square" />
    <img alt="Platform Windows" src="https://img.shields.io/badge/platform-Windows-0078D4?style=flat-square&logo=windows&logoColor=white" />
    <img alt="Python 3.10 or newer" src="https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" />
    <img alt="PySide6 6.7 or newer" src="https://img.shields.io/badge/PySide6-6.7%2B-41CD52?style=flat-square" />
    <img alt="English and Polish UI" src="https://img.shields.io/badge/i18n-English%20%7C%20Polski-5865F2?style=flat-square" />
  </p>
</div>

Mouse CMenu keeps your favorite Windows applications one mouse action away. Assign a global mouse-button or scroll shortcut, build a compact launcher menu with nested submenus, and manage everything from the Windows system tray.

## Features

- Global mouse shortcut for the left, middle, or right mouse button, scroll up, or scroll down.
- Non-intrusive mouse listener: the shortcut opens the menu without suppressing normal mouse input.
- Custom launcher menu with applications, shortcuts, nested submenus, labels, and optional icons.
- Supports `.exe`, `.com`, and `.lnk` targets.
- Optional Windows startup entry.
- English and Polish interface.
- Lightweight system-tray application with a single-instance guard.

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or newer
- Dependencies from `requirements.txt`:
  - `PySide6-Essentials>=6.7,<7`
  - `pynput>=1.7.7,<2`

## Quick start

Run these commands from the project root:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

The app starts in the Windows system tray. The default shortcut is the middle mouse button. Use the tray icon's context menu or the menu's **Settings** entry to configure the application.

## Configure the shortcut

Open **Settings** and choose a shortcut from the list, or select **Record with mouse...** and press a mouse button or scroll direction. Press `Esc` while recording to cancel.

Mouse input remains active while Mouse CMenu listens for the configured shortcut.

## Build the menu

In **Settings**, use:

- **Add application** to choose an `.exe`, `.com`, or `.lnk` file and set its menu label and optional icon.
- **Add submenu** to create a nested group.
- Select a submenu before adding items to place them inside that group.
- Select any entry and choose **Remove** to delete it.

Changes are saved automatically to the user's application configuration directory as `settings.json`.

## Build a Windows executable

Run the PyInstaller build script:

```powershell
.dev\build.bat
```

The executable is written to:

```text
.dev\dist\MouseCMenu.exe
```

## Create a desktop shortcut

For the Python source version, run this from PowerShell after installing the dependencies:

```powershell
$exe = (Get-Command pythonw).Source
$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut("$env:USERPROFILE\Desktop\Mouse CMenu.lnk")
$lnk.TargetPath = $exe
$lnk.Arguments = '"' + (Resolve-Path .\main.py).Path + '"'
$lnk.WorkingDirectory = (Get-Location).Path
$lnk.IconLocation = (Resolve-Path .\docs\ico.ico).Path
$lnk.Save()
```

For the packaged build, point the shortcut to `.dev\dist\MouseCMenu.exe` instead and use the executable as its icon source.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Documentation

- [Polish README](docs/readme.pl.md)
- [Run from source - English](docs/run.en.md) / [Polski](docs/run.pl.md)
- [Requirements - English](docs/requirements.en.md) / [Polski](docs/requirements.pl.md)
- [Application description](docs/description.txt)

---

<div align="center">Mouse CMenu by Sebastian Janychowski ⌁ polsoft.ITS™</div>
