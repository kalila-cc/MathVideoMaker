param(
  [string]$Quality = "-qh",
  [int]$MaxParallel = 2
)

$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $root

$sceneNames = @(
  "CoverFrame",
  "StoryHook",
  "VariablesMatter",
  "LineEquationNatural",
  "EnvelopeIdea",
  "DerivativeStep",
  "SolveParameter",
  "FourQuadrantAstroid",
  "RealityExamples"
)

& (Join-Path $PSScriptRoot "render_scenes_parallel.ps1") `
  -SceneFile "topics\astroid-envelope\scenes\astroid_envelope_v6.py" `
  -SceneNames $sceneNames `
  -Quality $Quality `
  -MaxParallel $MaxParallel

& (Join-Path $PSScriptRoot "render_scene.ps1") `
  -SceneFile "topics\astroid-envelope\scenes\chatgpt_outro.py" `
  -SceneName "ChatGPTOutro" `
  -Quality $Quality
