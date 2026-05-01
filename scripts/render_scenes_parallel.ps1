param(
  [Parameter(Mandatory = $true)]
  [string]$SceneFile,

  [Parameter(Mandatory = $true)]
  [string[]]$SceneNames,

  [string]$Quality = "-ql",

  [int]$MaxParallel = 3
)

$ErrorActionPreference = "Stop"

if ($MaxParallel -lt 1) {
  throw "MaxParallel must be at least 1."
}

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv\Scripts\python.exe"
$localFfmpegBin = Join-Path $root "tools\ffmpeg\bin"
$miktexBin = Join-Path $env:LOCALAPPDATA "Programs\MiKTeX\miktex\bin\x64"

if (-not (Test-Path $python)) {
  throw "Missing .venv. Run scripts\setup_venv.ps1 first."
}

$pathPrefix = @()
if (Test-Path (Join-Path $localFfmpegBin "ffmpeg.exe")) {
  $pathPrefix += $localFfmpegBin
}
if (Test-Path (Join-Path $miktexBin "xelatex.exe")) {
  $pathPrefix += $miktexBin
}
$renderPath = (($pathPrefix + @($env:PATH)) -join ";")

function Get-TopicMediaArgText {
  param([string]$SceneFilePath)

  $topicsRoot = (Join-Path $root "topics").TrimEnd("\", "/")
  if ([System.IO.Path]::IsPathRooted($SceneFilePath)) {
    $sceneFull = [System.IO.Path]::GetFullPath($SceneFilePath)
  } else {
    $sceneFull = [System.IO.Path]::GetFullPath((Join-Path $root $SceneFilePath))
  }

  $prefix = $topicsRoot + [System.IO.Path]::DirectorySeparatorChar
  if (-not $sceneFull.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    return ""
  }

  $relative = $sceneFull.Substring($prefix.Length)
  $topic = $relative.Split([char[]]@('\', '/'), [System.StringSplitOptions]::RemoveEmptyEntries)[0]
  if (-not $topic) {
    return ""
  }

  $mediaDir = "topics\$topic\exports\manim"
  return "--media_dir `"$mediaDir`""
}

$mediaArgText = Get-TopicMediaArgText -SceneFilePath $SceneFile

$pending = [System.Collections.Generic.Queue[string]]::new()
foreach ($scene in $SceneNames) {
  if ($scene -and $scene.Trim()) {
    $pending.Enqueue($scene.Trim())
  }
}

$jobs = @()
$failures = @()

while ($pending.Count -gt 0 -or $jobs.Count -gt 0) {
  while ($pending.Count -gt 0 -and $jobs.Count -lt $MaxParallel) {
    $scene = $pending.Dequeue()
    Write-Host "Starting $scene"
    $jobs += Start-Job -Name $scene -ScriptBlock {
      param($Root, $Python, $Quality, $SceneFile, $SceneName, $RenderPath, $MediaArgText)
      $env:PATH = $RenderPath
      Set-Location $Root
      $log = [System.IO.Path]::GetTempFileName()
      $psi = [System.Diagnostics.ProcessStartInfo]::new()
      $psi.FileName = $env:ComSpec
      $command = "`"$Python`" -m manim $Quality $MediaArgText `"$SceneFile`" `"$SceneName`" > `"$log`" 2>&1"
      $psi.Arguments = "/d /s /c `"$command`""
      $psi.WorkingDirectory = $Root
      $psi.UseShellExecute = $false
      $psi.CreateNoWindow = $true
      $process = [System.Diagnostics.Process]::new()
      $process.StartInfo = $psi
      [void]$process.Start()
      $process.WaitForExit()
      $exitCode = $process.ExitCode
      $output = (Get-Content -LiteralPath $log -Raw -ErrorAction SilentlyContinue).Trim()
      Remove-Item -LiteralPath $log -ErrorAction SilentlyContinue
      [pscustomobject]@{
        Scene = $SceneName
        ExitCode = $exitCode
        Output = $output
      }
    } -ArgumentList $root, $python, $Quality, $SceneFile, $scene, $renderPath, $mediaArgText
  }

  $finished = Wait-Job -Job $jobs -Any
  $result = Receive-Job -Job $finished
  Remove-Job -Job $finished
  $jobs = @($jobs | Where-Object { $_.Id -ne $finished.Id })

  foreach ($item in $result) {
    if ($item.Output) {
      Write-Host $item.Output
    }
    if ($item.ExitCode -ne 0) {
      $failures += "$($item.Scene) exited with $($item.ExitCode)"
    } else {
      Write-Host "Completed $($item.Scene)"
    }
  }
}

if ($failures.Count -gt 0) {
  throw "Render failed: $($failures -join '; ')"
}
