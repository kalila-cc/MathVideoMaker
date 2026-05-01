$ErrorActionPreference = "Continue"

$tools = @(
  @{ Name = "python"; Hint = "Required. Python 3.11 is recommended." },
  @{ Name = "node"; Hint = "Optional. Needed for Motion Canvas or Remotion." },
  @{ Name = "npm"; Hint = "Optional. Needed for Motion Canvas or Remotion." },
  @{ Name = "git"; Hint = "Recommended for versioning scenes and scripts." },
  @{ Name = "ffmpeg"; Hint = "Required for rendering/transcoding video." },
  @{ Name = "manim"; Hint = "Installed after pip install -r requirements.txt." },
  @{ Name = "latex"; Hint = "Installed with MiKTeX or TeX Live." },
  @{ Name = "xelatex"; Hint = "Recommended for CJK/Chinese LaTeX workflows." },
  @{ Name = "typst"; Hint = "Optional fast math/typesetting renderer." },
  @{ Name = "blender"; Hint = "Optional for 3D scenes." }
)

$miktexBin = Join-Path $env:LOCALAPPDATA "Programs\MiKTeX\miktex\bin\x64"
if (Test-Path (Join-Path $miktexBin "xelatex.exe")) {
  $env:PATH = $miktexBin + ";" + $env:PATH
}

Write-Host "VideoMaker tool check" -ForegroundColor Cyan
Write-Host "Workspace: $PWD"
Write-Host ""

if (Test-Path (Join-Path $miktexBin "xelatex.exe")) {
  Write-Host ("[OK]      MiKTeX bin => {0}" -f $miktexBin) -ForegroundColor Green
  Write-Host ""
}

$localFfmpeg = ".\tools\ffmpeg\bin\ffmpeg.exe"
if (Test-Path $localFfmpeg) {
  Write-Host ("[OK]      local ffmpeg => {0}" -f $localFfmpeg) -ForegroundColor Green
  try {
    $localFfmpegVersion = & $localFfmpeg -version 2>$null | Select-Object -First 1
    if ($localFfmpegVersion) {
      Write-Host ("          {0}" -f $localFfmpegVersion)
    }
  } catch {
    Write-Host "          version check skipped"
  }
  Write-Host ""
}

foreach ($tool in $tools) {
  if (($tool.Name -eq "ffmpeg") -and (Test-Path $localFfmpeg)) {
    Write-Host ("[OK]      ffmpeg => {0}" -f $localFfmpeg) -ForegroundColor Green
    continue
  }

  if (($tool.Name -eq "manim") -and (Test-Path ".\.venv\Scripts\python.exe")) {
    try {
      $venvManimVersion = .\.venv\Scripts\python -m manim --version 2>$null | Select-Object -First 1
      if ($venvManimVersion) {
        Write-Host ("[OK]      manim => project .venv ({0})" -f $venvManimVersion) -ForegroundColor Green
        continue
      }
    } catch {
      # Fall through to the normal command lookup.
    }
  }

  $cmd = Get-Command $tool.Name -ErrorAction SilentlyContinue
  if ($cmd) {
    Write-Host ("[OK]      {0} => {1}" -f $tool.Name, $cmd.Source) -ForegroundColor Green
    try {
      $version = & $tool.Name --version 2>$null | Select-Object -First 1
      if ($version) {
        Write-Host ("          {0}" -f $version)
      }
    } catch {
      Write-Host "          version check skipped"
    }
  } else {
    Write-Host ("[MISSING] {0}" -f $tool.Name) -ForegroundColor Yellow
    Write-Host ("          {0}" -f $tool.Hint)
  }
}

Write-Host ""
Write-Host "Project Python environment" -ForegroundColor Cyan

if (Test-Path ".\.venv\Scripts\python.exe") {
  Write-Host "[OK]      .venv python => .\.venv\Scripts\python.exe" -ForegroundColor Green
  try {
    $manimVersion = .\.venv\Scripts\python -m manim --version 2>$null | Select-Object -First 1
    if ($manimVersion) {
      Write-Host ("[OK]      .venv manim  => {0}" -f $manimVersion) -ForegroundColor Green
    }
  } catch {
    Write-Host "[MISSING] .venv manim" -ForegroundColor Yellow
  }

  try {
    $edgeVersion = .\.venv\Scripts\python -m edge_tts --version 2>$null | Select-Object -First 1
    if ($edgeVersion) {
      Write-Host ("[OK]      .venv edge-tts => {0}" -f $edgeVersion) -ForegroundColor Green
    }
  } catch {
    Write-Host "[MISSING] .venv edge-tts" -ForegroundColor Yellow
  }
} else {
  Write-Host "[MISSING] .venv python" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "If manim is missing inside .venv, run:" -ForegroundColor Cyan
Write-Host "  python -m venv .venv"
Write-Host "  .\.venv\Scripts\python -m pip install --upgrade pip"
Write-Host "  .\.venv\Scripts\pip install -r requirements.txt"
