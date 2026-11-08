# Uruchamianie Mouse CMenu z kodu źródłowego

Ten przewodnik uruchamia aplikację Python bezpośrednio z katalogu projektu.

## Wymagania

- Windows 10 lub Windows 11
- Python 3.10 lub nowszy
- Zainstalowane zależności projektu

Szczegóły znajdziesz w pliku [Wymagania aplikacji](requirements.pl.md).

## Instalacja i uruchomienie

Otwórz PowerShell w katalogu głównym projektu i uruchom:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Jeśli PowerShell zablokuje skrypt aktywacji środowiska wirtualnego, użyj interpretera bezpośrednio:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Mouse CMenu uruchamia się w zasobniku systemowym Windows. Domyślnym skrótem myszy jest środkowy przycisk myszy; zmień go w **Ustawieniach**.

---

<div align="center">Mouse CMenu by Sebastian Janychowski ⌁ polsoft.ITS™</div>
