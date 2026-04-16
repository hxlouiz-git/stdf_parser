@echo off
setlocal

:: Strip quotes from PATH to fix Graphviz vcvarsall.bat incompatibility
set PATH=%PATH:"=%

:: Clean previous build artifacts
echo Cleaning previous build...
if exist dist\*.whl del /q dist\*.whl
if exist build rmdir /s /q build
if exist build_cython rmdir /s /q build_cython

:: Compile and package
echo Cythonizing and building wheel...
.venv\Scripts\python.exe setup.py bdist_wheel

if %ERRORLEVEL% neq 0 (
    echo.
    echo BUILD FAILED.
    exit /b 1
)

echo.
echo Wheel contents:
.venv\Scripts\python.exe -c "import zipfile, glob; whl=glob.glob('dist/*.whl')[0]; print(whl); [print(' ', n) for n in zipfile.ZipFile(whl).namelist()]"

:: Clean up intermediate Cython files
echo.
echo Cleaning intermediate files...
if exist build rmdir /s /q build
if exist build_cython rmdir /s /q build_cython
del /q stdf_parser\*.c 2>nul
del /q stdf_parser\*.pyd 2>nul

echo.
echo BUILD SUCCEEDED. Wheel is in dist\
endlocal
