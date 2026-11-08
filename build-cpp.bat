cpp nie powinna uzywac @echo off
setlocal EnableExtensions EnableDelayedExpansion
rem ===========================================================================
rem  Builds the C++ version of Context Menu (.cpp) into a standalone .exe.
rem  Just double-click this file.
rem
rem  Optional overrides (set before running, or edit the defaults below):
rem    MSYS2_ROOT   root of the MSYS2 installation
rem    BUILD_DIR    build folder
rem    JOBS         parallel compiler jobs (1 is safest for memory, see note)
rem ===========================================================================

rem --- Paths -----------------------------------------------------------------
rem %~dp0 is the folder this .bat file lives in.
set "SCRIPT_DIR=%~dp0"
if "%MSYS2_ROOT%"=="" set "MSYS2_ROOT=D:\_instaled\msys64"
set "SRC_DIR=%SCRIPT_DIR%.cpp"
if "%BUILD_DIR%"=="" set "BUILD_DIR=%SRC_DIR%\build\mingw"
set "TOOLCHAIN=%MSYS2_ROOT%\ucrt64"
if "%JOBS%"=="" set "JOBS=1"

title Context Menu - C++ build
echo ===========================================================================
echo  Context Menu - C++ build
echo ===========================================================================
echo  Source   : %SRC_DIR%
echo  Build    : %BUILD_DIR%
echo  MSYS2    : %MSYS2_ROOT%
echo  Jobs     : %JOBS%
echo.

rem --- Toolchain sanity checks ----------------------------------------------
if not exist "%TOOLCHAIN%\bin\g++.exe" (
    echo [ERROR] g++ not found: "%TOOLCHAIN%\bin\g++.exe"
    echo         Set MSYS2_ROOT to your MSYS2 folder, e.g.
    echo             set MSYS2_ROOT=C:\msys64
    goto :fail
)
if not exist "%TOOLCHAIN%\lib\cmake\Qt6\Qt6Config.cmake" (
    echo [ERROR] Qt6 for MinGW not found in "%TOOLCHAIN%".
    echo         Install it in the MSYS2 UCRT64 shell with:
    echo             pacman -S mingw-w64-ucrt-x86_64-qt6-base mingw-w64-ucrt-x86_64-gcc
    goto :fail
)

rem Qt's tools (moc, windeployqt) need the UCRT64 DLLs on PATH, otherwise
rem CMake reports "Test run of moc failed" with exit code 0xc0000135.
set "PATH=%TOOLCHAIN%\bin;%PATH%"

where cmake >nul 2>&1
if errorlevel 1 (
    echo [ERROR] cmake is not on PATH. Install CMake or add "C:\Program Files\CMake\bin" to PATH.
    goto :fail
)
rem Ninja often lives in the MSYS2 folder without being on the Windows PATH.
set "NINJA="
for /f "delims=" %%N in ('where ninja 2^>nul') do if not defined NINJA set "NINJA=%%N"
if not defined NINJA if exist "%TOOLCHAIN%\bin\ninja.exe" set "NINJA=%TOOLCHAIN%\bin\ninja.exe"
if not defined NINJA (
    echo [ERROR] ninja was not found. Install it with "pacman -S mingw-w64-ucrt-x86_64-ninja"
    echo         or in Windows with "winget install Ninja-build.Ninja".
    goto :fail
)

rem --- Configure -------------------------------------------------------------
echo [1/3] Configuring...
cmake -S "%SRC_DIR%" -B "%BUILD_DIR%" -G Ninja ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DCMAKE_CXX_COMPILER="%TOOLCHAIN%\bin\g++.exe" ^
    -DCMAKE_MAKE_PROGRAM="%NINJA%" ^
    -DCMAKE_PREFIX_PATH="%TOOLCHAIN%"
if errorlevel 1 (
    echo.
    echo [ERROR] CMake configuration failed.
    goto :fail
)

rem --- Build -----------------------------------------------------------------
rem NOTE: parallel compiles of Qt headers can exhaust memory with
rem "cc1plus: out of memory allocating". Lower JOBS if that happens.
echo.
echo [2/3] Building with %JOBS% job^(s^)...
cmake --build "%BUILD_DIR%" --config Release --parallel %JOBS%
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed.
    goto :fail
)

rem --- Report ----------------------------------------------------------------
echo.
echo [3/3] Done.
set "EXE=%BUILD_DIR%\context-menu.exe"
if not exist "%EXE%" (
    echo [ERROR] Expected output not found: "%EXE%"
    goto :fail
)
for %%F in ("%EXE%") do echo  Executable: %%~fF  ^(%%~zF bytes^)

if exist "%BUILD_DIR%\tst_core.exe" (
    echo  Tests     : %BUILD_DIR%\tst_core.exe
    echo.
    echo  Run the tests with:
    echo      cd /d "%BUILD_DIR%" ^&^& ctest --output-on-failure
)

echo.
echo  Qt runtime DLLs are deployed next to the exe by windeployqt.
echo  Starting the app ...
start "" "%EXE%"
echo.
echo  Build finished successfully.
pause
exit /b 0

:fail
echo.
echo  Build NOT completed. See the messages above.
pause
exit /b 1
