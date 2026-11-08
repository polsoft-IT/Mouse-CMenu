# Run Mouse CMenu from source

This guide runs the Python application directly from the project folder.

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or newer
- Project dependencies installed

See [Application requirements](requirements.en.md) for details.

## Setup and run

Open PowerShell in the project root and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

If PowerShell blocks the virtual-environment activation script, use the interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Mouse CMenu starts in the Windows system tray. The default mouse shortcut is the middle mouse button; change it in **Settings**.

---

<div align="center">Mouse CMenu by Sebastian Janychowski ⌁ polsoft.ITS™</div>
