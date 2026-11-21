# run-ue-python.ps1 — canonical runner for UE editor-Python scripts (the MCP
# fallback path). Runs as a separate commandlet process; verified safe to run
# concurrently with a live editor session.
#
#   scripts\run-ue-python.ps1 -Project <abs .uproject> -Script <abs .py>
#       [-ScriptArgs "<args>"] [-SuccessPattern "<regex>"] [-AllowCommandletRendering]
#
# Gotchas this script exists to encode (do not "simplify"):
#   * UE escape-processes backslashes in the -script value (\u, \n in paths get
#     eaten) — paths are converted to forward slashes here.
#   * UnrealEditor-Cmd's exit code is UNRELIABLE for pythonscript: unrelated
#     subsystem log errors (VC++ redist notice, asset-manager warnings) make it
#     non-zero even when the script succeeded. Pass -SuccessPattern (a regex
#     matched against the run's log output) to get a trustworthy 0/1 exit code;
#     without it, the raw (unreliable) exit code is passed through.
param(
  [Parameter(Mandatory = $true)][string]$Project,
  [Parameter(Mandatory = $true)][string]$Script,
  [string]$ScriptArgs = "",
  [string]$SuccessPattern = "",
  [switch]$AllowCommandletRendering
)
$ErrorActionPreference = "Stop"
if (-not (Test-Path $Project)) { throw "project not found: $Project" }
. (Join-Path $PSScriptRoot 'ue-engine.ps1')
$editor = Join-Path (Get-UeEngineDir -Project $Project) "Binaries\Win64\UnrealEditor-Cmd.exe"
if (-not (Test-Path $Script)) { throw "script not found: $Script" }

$scriptFwd = $Script -replace "\\", "/"
$scriptSpec = if ($ScriptArgs) { "$scriptFwd $ScriptArgs" } else { $scriptFwd }

$logFile = Join-Path $env:TEMP ("run-ue-python-{0}.log" -f (Get-Date -Format "yyyyMMdd-HHmmss"))
$extra = @()
if ($AllowCommandletRendering) { $extra += "-AllowCommandletRendering" }  # scripts that draw (render targets); off by default
& $editor $Project -run=pythonscript -script="$scriptSpec" -unattended -nosplash -stdout -FullStdOutLogOutput @extra *> $logFile
$rawExit = $LASTEXITCODE

# Always surface the Python-relevant lines; full log stays on disk.
Select-String -Path $logFile -Pattern "LogPython" | ForEach-Object { $_.Line }
Write-Host "(full log: $logFile)"

if ($SuccessPattern) {
  if (Select-String -Path $logFile -Pattern $SuccessPattern -Quiet) {
    Write-Host "SUCCESS: matched '$SuccessPattern'"
    exit 0
  }
  Write-Host "FAILURE: pattern '$SuccessPattern' not found in log"
  exit 1
}
exit $rawExit
