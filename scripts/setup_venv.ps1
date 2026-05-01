$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
  python -m venv .venv
}

.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt

Write-Host ""
Write-Host "Python environment is ready." -ForegroundColor Green
Write-Host "Next: install FFmpeg and MiKTeX, then run .\scripts\check_tools.ps1"
