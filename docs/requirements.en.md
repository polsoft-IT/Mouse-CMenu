# Application requirements

## System requirements

- Windows 10 or Windows 11
- Python 3.10 or newer
- `pip` included with Python or installed separately

## Python dependencies

Install the runtime dependencies from `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

Required packages:

- `PySide6-Essentials>=6.7,<7`
- `pynput>=1.7.7,<2`

## Optional build tools

- PyInstaller is required only when building `.dev\dist\MouseCMenu.exe` with `.dev\build.bat`.
- The build script installs PyInstaller automatically in a temporary environment.

## Notes

- Mouse CMenu is a Windows desktop application and uses the Windows system tray.
- Settings are stored in the user's application configuration directory as `settings.json`.

---

<div align="center">Mouse CMenu by Sebastian Janychowski ⌁ polsoft.ITS™</div>
