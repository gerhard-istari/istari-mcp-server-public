set HOME_DIR=%~dp0
set PYTHONHOME=
set PATH=%HOME_DIR%\venv\Scripts;%PATH%

cd %HOME_DIR%
python istari-server.py
