# Wymagania aplikacji

## Wymagania systemowe

- Windows 10 lub Windows 11
- Python 3.10 lub nowszy
- `pip` dołączony do Pythona lub zainstalowany osobno

## Zależności Python

Zainstaluj zależności środowiska uruchomieniowego z pliku `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

Wymagane pakiety:

- `PySide6-Essentials>=6.7,<7`
- `pynput>=1.7.7,<2`

## Opcjonalne narzędzia budowania

- PyInstaller jest wymagany tylko podczas budowania `.dev\dist\MouseCMenu.exe` za pomocą `.dev\build.bat`.
- Skrypt budowania instaluje PyInstaller automatycznie w tymczasowym środowisku.

## Uwagi

- Mouse CMenu jest aplikacją pulpitu Windows i używa zasobnika systemowego Windows.
- Ustawienia są zapisywane w katalogu konfiguracji użytkownika jako `settings.json`.

---

<div align="center">Mouse CMenu by Sebastian Janychowski ⌁ polsoft.ITS™</div>
