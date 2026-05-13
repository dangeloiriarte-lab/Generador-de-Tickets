@echo off
for /f "usebackq tokens=*" %%i in (`powershell -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike '*Loopback*' -and $_.IPAddress -notlike '169.254.*' }).IPAddress"`) do set LOCAL_IP=%%i
echo Iniciando Generador de Tickets...
echo Servidor local: http://127.0.0.1:8035
echo Red local:     http://%LOCAL_IP%:8035
echo Presiona Ctrl+C para detener.
echo.
python manage.py runserver 0.0.0.0:8035
