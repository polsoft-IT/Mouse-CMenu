@echo off
setlocal EnableExtensions

set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "DEV=%~dp0"
set "ENV_DIR=%DEV%.build-venv"
set "WORK_DIR=%DEV%build"
set "DIST_DIR=%DEV%dist"
set "ICON=%ROOT%\docs\ico.ico"
set "SPEC=%DEV%ContextMenu.spec"
set "VERSION_INFO=%DEV%version_info.txt"
set "BUILD_RESULT=1"

if not exist "%ICON%" (
    echo [ERROR] Icon file not found: "%ICON%"
    goto cleanup
)
if not exist "%SPEC%" (
    echo [ERROR] PyInstaller spec not found: "%SPEC%"
    goto cleanup
)
if not exist "%VERSION_INFO%" (
    echo [ERROR] Version information not found: "%VERSION_INFO%"
    goto cleanup
)

if exist "%WORK_DIR%" rmdir /s /q "%WORK_DIR%"
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

if not exist "%ENV_DIR%\Scripts\python.exe" (
    if defined PYTHON_EXE (
        "%PYTHON_EXE%" -m venv "%ENV_DIR%"
    ) else (
        py -3 -m venv "%ENV_DIR%"
    )
    if errorlevel 1 (
        echo [ERROR] Python is required. Set PYTHON_EXE to its interpreter path.
        goto cleanup
    )
)

set "PYTHON=%ENV_DIR%\Scripts\python.exe"
"%PYTHON%" -m pip install --disable-pip-version-check -r "%ROOT%\requirements.txt" pyinstaller
if errorlevel 1 (
    echo [ERROR] Could not install build dependencies.
    goto cleanup
)

pushd "%ROOT%"
if errorlevel 1 goto cleanup
"%PYTHON%" -m PyInstaller --noconfirm --clean --distpath "%DIST_DIR%" --workpath "%WORK_DIR%" "%SPEC%"
set "BUILD_RESULT=%ERRORLEVEL%"
popd
if not "%BUILD_RESULT%"=="0" (
    echo [ERROR] PyInstaller build failed.
    goto cleanup
)
if not exist "%DIST_DIR%\MouseCMenu.exe" (
    set "BUILD_RESULT=1"
    echo [ERROR] Expected executable was not produced.
    goto cleanup
)

echo Build complete: "%DIST_DIR%\MouseCMenu.exe"

:cleanup
if exist "%WORK_DIR%" rmdir /s /q "%WORK_DIR%"
if exist "%ENV_DIR%" rmdir /s /q "%ENV_DIR%"
if not "%BUILD_RESULT%"=="0" echo Build failed. Temporary builder files were removed.
exit /b %BUILD_RESULT%
