# Reports where the Unreal Engine the project file names is installed, or that it is not.
param([string]$Project)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'ue-engine.ps1')
if ($Project) { $EngineDir = Get-UeEngineDir -Project $Project } else { $EngineDir = Get-UeEngineDir }
Write-Host "FOUND: $EngineDir"
