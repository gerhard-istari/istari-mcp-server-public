set HOME_DIR="%~dp0"
set PYTHONHOME=
set PATH="%HOME_DIR%\venv\Scripts";%PATH%

C:
cd "%HOME_DIR%"
python.exe %1
