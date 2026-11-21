# ue-editor.ps1 — canonical editor lifecycle for agents. Uses the launch recipe that avoids the
# hung-launch failure mode; readiness is probed on the MCP port, not by grepping logs.
#
#   scripts\ue-editor.ps1 start  [-Project <abs .uproject>] [-TimeoutSec 300]
#   scripts\ue-editor.ps1 status
#   scripts\ue-editor.ps1 stop
# -Project defaults to the one .uproject beside scripts/. State (pid, log) lives in
# %LOCALAPPDATA%\<that project's name>.
param(
  [Parameter(Mandatory = $true, Position = 0)][ValidateSet("start", "status", "stop")]
  [string]$Command,
  [string]$Project,
  [int]$TimeoutSec = 300,
  [string]$McpUrl = "http://127.0.0.1:8000/mcp"
)
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot 'ue-engine.ps1')
$stateDir = Join-Path $env:LOCALAPPDATA ([IO.Path]::GetFileNameWithoutExtension((Get-UeProjectFile)))
$pidFile = Join-Path $stateDir "ue-editor.pid"
$logFile = Join-Path $stateDir "ue-editor.log"

function Test-Mcp {
  try { Invoke-WebRequest -Uri $McpUrl -Method Head -TimeoutSec 2 -UseBasicParsing | Out-Null; return $true }
  catch {
    # Any HTTP response (incl. 4xx/405) means the server is listening; connection errors mean it is not.
    if ($_.Exception.Response) { return $true }
    return $false
  }
}

switch ($Command) {
  "status" {
    if (Test-Mcp) { Write-Host "MCP server RESPONDING at $McpUrl"; exit 0 }
    Write-Host "MCP server NOT reachable at $McpUrl"; exit 1
  }
  "stop" {
    if (-not (Test-Path $pidFile)) { Write-Host "no pid file ($pidFile); nothing to stop"; exit 0 }
    $procId = Get-Content $pidFile
    try { Stop-Process -Id $procId -Force -Confirm:$false; Write-Host "stopped editor (pid $procId)" }
    catch { Write-Host "pid $procId not running" }
    Remove-Item $pidFile -Force
    exit 0
  }
  "start" {
    if (Test-Mcp) { Write-Host "editor already up (MCP responding at $McpUrl)"; exit 0 }
    if (-not $Project) { $Project = Get-UeProjectFile }
    if (-not (Test-Path $Project)) { throw "project not found: $Project" }
    $editor = Join-Path (Get-UeEngineDir -Project $Project) "Binaries\Win64\UnrealEditor-Cmd.exe"
    New-Item -ItemType Directory -Force $stateDir | Out-Null
    # Verified-safe launch: -stdout -FullStdOutLogOutput -unattended with real
    # output redirection. (-log=<path> alone hung indefinitely.)
    $proc = Start-Process -FilePath $editor `
      -ArgumentList "`"$Project`"", "-stdout", "-FullStdOutLogOutput", "-unattended" `
      -RedirectStandardOutput $logFile -RedirectStandardError "$logFile.err" `
      -PassThru -WindowStyle Hidden
    Set-Content $pidFile $proc.Id
    Write-Host "launched editor pid $($proc.Id); waiting for MCP on $McpUrl (timeout ${TimeoutSec}s)"
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
      if ($proc.HasExited) { Write-Host "editor exited early (code $($proc.ExitCode)); see $logFile"; exit 1 }
      if (Test-Mcp) { Write-Host "MCP server up. Log: $logFile"; exit 0 }
      Start-Sleep -Seconds 3
    }
    Write-Host "timed out after ${TimeoutSec}s; editor still starting or MCP auto-start not configured. Log: $logFile"
    exit 1
  }
}
