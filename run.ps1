# run.ps1 — запуск PlatCube DL
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv")) {
    Write-Host "Создаю venv..." -ForegroundColor Yellow
    python -m venv .venv
    & ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
}

& ".\.venv\Scripts\python.exe" main.py