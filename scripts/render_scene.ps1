param(
  [string]$SceneFile = "topics\smoke-test\scenes\demo_no_latex.py",
  [string]$SceneName = "NoLatexSmokeTest",
  [string]$Quality = "-ql"
)

$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv\Scripts\python.exe"
$localFfmpegBin = Join-Path $root "tools\ffmpeg\bin"
$miktexBin = Join-Path $env:LOCALAPPDATA "Programs\MiKTeX\miktex\bin\x64"

if (-not (Test-Path $python)) {
  throw "Missing .venv. Run scripts\setup_venv.ps1 first."
}

if (Test-Path (Join-Path $localFfmpegBin "ffmpeg.exe")) {
  $env:PATH = $localFfmpegBin + ";" + $env:PATH
}

if (Test-Path (Join-Path $miktexBin "xelatex.exe")) {
  $env:PATH = $miktexBin + ";" + $env:PATH
}

function Get-TopicMediaArgs {
  param([string]$SceneFilePath)

  $topicsRoot = (Join-Path $root "topics").TrimEnd("\", "/")
  if ([System.IO.Path]::IsPathRooted($SceneFilePath)) {
    $sceneFull = [System.IO.Path]::GetFullPath($SceneFilePath)
  } else {
    $sceneFull = [System.IO.Path]::GetFullPath((Join-Path $root $SceneFilePath))
  }

  $prefix = $topicsRoot + [System.IO.Path]::DirectorySeparatorChar
  if (-not $sceneFull.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    return @()
  }

  $relative = $sceneFull.Substring($prefix.Length)
  $topic = $relative.Split([char[]]@('\', '/'), [System.StringSplitOptions]::RemoveEmptyEntries)[0]
  if (-not $topic) {
    return @()
  }

  return @("--media_dir", "topics\$topic\exports\manim")
}

Push-Location $root
try {
  $mediaArgs = Get-TopicMediaArgs -SceneFilePath $SceneFile
  & $python -m manim $Quality @mediaArgs $SceneFile $SceneName
} finally {
  Pop-Location
}
