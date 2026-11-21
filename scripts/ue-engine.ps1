# ue-engine.ps1 - finds the project file and the Unreal Engine install it names. Dot-source it, then:
#   $Project   = Get-UeProjectFile                # the one .uproject beside scripts/
#   $EngineDir = Get-UeEngineDir                  # the engine that project names
#   $EngineDir = Get-UeEngineDir -Project <path>  # the engine another .uproject names
# Returns the install's Engine folder; stops, naming the version, when that version is not installed.
# The launcher's own manifest is read, not the registry: the registry lacks some launcher installs.

function Get-UeProjectFile {
  $Root = Split-Path -Parent $PSScriptRoot
  $Found = @(Get-ChildItem -Path $Root -Filter '*.uproject' -File)
  if ($Found.Count -ne 1) { throw "expected one .uproject in $Root, found $($Found.Count)" }
  return $Found[0].FullName
}

function Get-UeEngineDir {
  param([string]$Project = (Get-UeProjectFile))
  $Manifest = 'C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat'
  $Version = (Get-Content -Raw $Project | ConvertFrom-Json).EngineAssociation
  $Installs = @()
  if (Test-Path $Manifest) { $Installs = (Get-Content -Raw $Manifest | ConvertFrom-Json).InstallationList }
  $Install = $Installs | Where-Object { $_.AppName -eq "UE_$Version" } | Select-Object -First 1
  $Dir = $null
  if ($Install) { $Dir = Join-Path $Install.InstallLocation 'Engine' }
  if (-not $Dir -or -not (Test-Path $Dir)) {
    throw "Unreal Engine $Version is not installed ($(Split-Path -Leaf $Project) names it). Install it from the Epic Games Launcher."
  }
  return $Dir
}
