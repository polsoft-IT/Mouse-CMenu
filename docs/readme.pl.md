<div align="center">
  <img src="ico.ico" alt="Ikona Mouse CMenu" width="96" height="96" />
  <h1>Mouse CMenu</h1>
  <p><strong>Lekka aplikacja systemowa Windows do uruchamiania własnego menu aplikacji za pomocą myszy.</strong></p>
  <p>
    <img alt="Wersja 1.2.0" src="https://img.shields.io/badge/version-1.2.0-0078D4?style=flat-square" />
    <img alt="Platforma Windows" src="https://img.shields.io/badge/platform-Windows-0078D4?style=flat-square&logo=windows&logoColor=white" />
    <img alt="Python 3.10 lub nowszy" src="https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" />
    <img alt="PySide6 6.7 lub nowszy" src="https://img.shields.io/badge/PySide6-6.7%2B-41CD52?style=flat-square" />
    <img alt="Interfejs English i Polski" src="https://img.shields.io/badge/i18n-English%20%7C%20Polski-5865F2?style=flat-square" />
  </p>
</div>

Mouse CMenu utrzymuje ulubione aplikacje Windows o jedno działanie myszy. Przypisz globalny skrót przycisku myszy lub przewijania, zbuduj kompaktowe menu uruchamiające z zagnieżdżonymi podmenu i zarządzaj wszystkim z poziomu zasobnika systemowego Windows.

## Funkcje

- Globalny skrót myszy dla lewego, środkowego lub prawego przycisku myszy, przewijania w górę albo w dół.
- Nienachalny nasłuch myszy: skrót otwiera menu bez blokowania normalnego działania myszy.
- Własne menu uruchamiające z aplikacjami, skrótami, zagnieżdżonymi podmenu, etykietami i opcjonalnymi ikonami.
- Obsługa elementów `.exe`, `.com` i `.lnk`.
- Opcjonalny wpis w autostarcie Windows.
- Interfejs w języku angielskim i polskim.
- Lekka aplikacja systemowa z zabezpieczeniem przed wielokrotnym uruchomieniem.

## Wymagania

- Windows 10 lub Windows 11
- Python 3.10 lub nowszy
- Zależności z pliku `requirements.txt`:
  - `PySide6-Essentials>=6.7,<7`
  - `pynput>=1.7.7,<2`

## Szybki start

Uruchom poniższe polecenia z katalogu głównego projektu:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Aplikacja uruchamia się w zasobniku systemowym Windows. Domyślnym skrótem jest środkowy przycisk myszy. Użyj menu kontekstowego ikony w zasobniku lub pozycji **Ustawienia** w menu, aby skonfigurować aplikację.

## Konfiguracja skrótu

Otwórz **Ustawienia** i wybierz skrót z listy albo wybierz **Nagraj myszą...**, a następnie naciśnij przycisk myszy lub przewiń kółkiem. Podczas nagrywania naciśnij `Esc`, aby anulować.

Mysz pozostaje aktywna, gdy Mouse CMenu nasłuchuje skonfigurowanego skrótu.

## Budowanie menu

W **Ustawieniach** użyj opcji:

- **Dodaj aplikację**, aby wybrać plik `.exe`, `.com` lub `.lnk`, ustawić etykietę menu i opcjonalną ikonę.
- **Dodaj podmenu**, aby utworzyć zagnieżdżoną grupę.
- Wybierz podmenu przed dodaniem elementów, aby umieścić je wewnątrz tej grupy.
- Wybierz dowolny element i kliknij **Usuń**, aby go usunąć.

Zmiany są zapisywane automatycznie w katalogu konfiguracji użytkownika jako `settings.json`.

## Budowanie pliku wykonywalnego Windows

Uruchom skrypt budowania PyInstaller:

```powershell
.dev\build.bat
```

Plik wykonywalny zostanie zapisany w:

```text
.dev\dist\MouseCMenu.exe
```

## Tworzenie skrótu na pulpicie

Dla wersji źródłowej Python uruchom poniższy skrypt w PowerShell po zainstalowaniu zależności:

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

Dla wersji pakietowej ustaw skrót na `.dev\dist\MouseCMenu.exe` i użyj pliku wykonywalnego jako źródła ikony.

## Testy

```powershell
python -m unittest discover -s tests -v
```

## Dokumentacja

- [README po angielsku](../README.md)
- [Uruchamianie z kodu - English](run.en.md) / [Polski](run.pl.md)
- [Wymagania - English](requirements.en.md) / [Polski](requirements.pl.md)
- [Opis aplikacji](description.txt)

---

<div align="center">Mouse CMenu by Sebastian Janychowski ⌁ polsoft.ITS™</div>
