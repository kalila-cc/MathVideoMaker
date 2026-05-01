$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$downloadDir = Join-Path $root "tools\_downloads"
$extractDir = Join-Path $downloadDir "ffmpeg_extract"
$installDir = Join-Path $root "tools\ffmpeg"
$zipPath = Join-Path $downloadDir "ffmpeg-release-essentials.zip"
$url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

$rootFull = [System.IO.Path]::GetFullPath($root)
$installFull = [System.IO.Path]::GetFullPath($installDir)
$extractFull = [System.IO.Path]::GetFullPath($extractDir)

Add-Type -AssemblyName System.IO.Compression.FileSystem

function Test-ZipArchive {
  param([string]$Path)

  try {
    $zip = [System.IO.Compression.ZipFile]::OpenRead($Path)
    $zip.Dispose()
    return $true
  } catch {
    return $false
  }
}

if (-not $installFull.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
  throw "Refusing to install outside workspace: $installFull"
}

if (-not $extractFull.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
  throw "Refusing to extract outside workspace: $extractFull"
}

New-Item -ItemType Directory -Force -Path $downloadDir | Out-Null

if ((Test-Path $zipPath) -and ((Get-Item $zipPath).Length -gt 50000000) -and (Test-ZipArchive $zipPath)) {
  Write-Host "Using existing FFmpeg archive:"
  Write-Host $zipPath
} else {
  if (Test-Path $zipPath) {
    Write-Host "Existing FFmpeg archive is missing or invalid; downloading again."
  }
  Write-Host "Downloading FFmpeg essentials build..."
  Write-Host $url
  Invoke-WebRequest -Uri $url -OutFile $zipPath
}

if (Test-Path $extractDir) {
  Remove-Item -LiteralPath $extractDir -Recurse -Force
}

Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force

$binDir = Get-ChildItem -Path $extractDir -Recurse -Directory |
  Where-Object { $_.Name -eq "bin" -and (Test-Path (Join-Path $_.FullName "ffmpeg.exe")) } |
  Select-Object -First 1

if (-not $binDir) {
  throw "Could not find ffmpeg.exe in downloaded archive."
}

if (Test-Path $installDir) {
  Remove-Item -LiteralPath $installDir -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $installDir | Out-Null
Copy-Item -LiteralPath $binDir.FullName -Destination $installDir -Recurse -Force

$env:PATH = (Join-Path $installDir "bin") + ";" + $env:PATH
& (Join-Path $installDir "bin\ffmpeg.exe") -version | Select-Object -First 1

Write-Host ""
Write-Host "FFmpeg is ready at tools\ffmpeg\bin\ffmpeg.exe" -ForegroundColor Green
Write-Host "Use scripts\render_scene.ps1 so the local FFmpeg path is added automatically."
