$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$services = @(
    @{ Name = "customer-service"; Port = 8001 },
    @{ Name = "book-service"; Port = 8002 },
    @{ Name = "cart-service"; Port = 8003 },
    @{ Name = "order-service"; Port = 8004 },
    @{ Name = "pay-service"; Port = 8005 },
    @{ Name = "ship-service"; Port = 8006 },
    @{ Name = "comment-rate-service"; Port = 8007 },
    @{ Name = "api-gateway"; Port = 8000 }
)

foreach ($service in $services) {
    $servicePath = Join-Path $root $service.Name
    $activatePath = Join-Path $servicePath "venv\Scripts\Activate.ps1"

    $runCommand = if (Test-Path $activatePath) {
        ". `"$activatePath`"; python manage.py runserver $($service.Port) --noreload"
    }
    else {
        "python manage.py runserver $($service.Port) --noreload"
    }

    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command", "Set-Location `"$servicePath`"; $runCommand"
    ) | Out-Null
}

Write-Host "All services are starting in separate PowerShell windows..."
Write-Host "API Gateway: http://localhost:8000/"
