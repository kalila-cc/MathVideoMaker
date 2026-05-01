$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv\Scripts\python.exe"
$pip = Join-Path $root ".venv\Scripts\pip.exe"
$installBin = Join-Path $root "tools\ffmpeg\bin"
$target = Join-Path $installBin "ffmpeg.exe"

if (-not (Test-Path $python)) {
  throw "Missing .venv. Run scripts\setup_venv.ps1 first."
}

& $pip install imageio-ffmpeg==0.6.0

$source = & $python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
if (-not (Test-Path $source)) {
  throw "imageio-ffmpeg did not provide an ffmpeg executable: $source"
}

New-Item -ItemType Directory -Force -Path $installBin | Out-Null
Copy-Item -LiteralPath $source -Destination $target -Force

& $target -version | Select-Object -First 1
Write-Host ""
Write-Host "FFmpeg is ready at tools\ffmpeg\bin\ffmpeg.exe" -ForegroundColor Green
