@echo off
setlocal

set "ROOT=%~dp0"

call :run "customer-service" 8001
call :run "book-service" 8002
call :run "cart-service" 8003
call :run "order-service" 8004
call :run "pay-service" 8005
call :run "ship-service" 8006
call :run "comment-rate-service" 8007
call :run "api-gateway" 8000

echo.
echo All services are starting in separate windows...
echo API Gateway: http://localhost:8000/
echo.
exit /b 0

:run
set "SVC=%~1"
set "PORT=%~2"
start "%SVC%:%PORT%" cmd /k "cd /d "%ROOT%%SVC%" && if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) && python manage.py runserver %PORT% --noreload"
exit /b 0
