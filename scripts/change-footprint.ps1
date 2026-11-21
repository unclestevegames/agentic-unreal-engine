<#
.SYNOPSIS
  Reports how far a change spread: one greppable line giving the added and
  deleted lines, and the file count, in each layer of the repo.

.DESCRIPTION
  What a change COSTS to build is not its line count, it is how many layers it
  had to be written out in. Nothing else here measures that, so it was only
  ever noticed when someone asked why one small feature had taken all day.

  /plan-issues reads it over recently merged pull requests to see what work of
  the same kind has been costing, and /plan-architecture uses it to show
  what a pattern it found in the code has already cost.

  WHAT A LAYER IS. With no table, a path's layer is its first path segment
  (`Source`, `Content`, ...), and a file at the repo root is in "root". A
  project names its own layers in `change-footprint.layers.json` beside this
  script: an ordered list of {"name", "prefixes"}, where the first layer with a
  prefix matching the path claims it -- so a project lists a build file before
  the module that holds it, and a UI folder before the rest of its module.

  EVERY CHANGED PATH LANDS IN EXACTLY ONE LAYER. Under a table, a path matching
  no layer lands in "other" rather than being dropped -- a footprint that
  silently loses files is worse than no footprint at all.

  UNTRACKED FILES ARE COUNTED, AND THE INDEX IS NEVER TOUCHED TO DO IT.
  `git diff` is blind to a brand-new file, and the usual fix -- `git add -N .`
  -- writes an intent-to-add entry whose blob is EMPTY, which turns
  `git checkout -- <file>` into `rm` for every new file in the run. That has
  destroyed a whole run's uncommitted work before now. So new files are
  enumerated from `git status --porcelain --untracked-files=all` and counted by
  their own line count instead, and nothing is staged.

  Renames are measured as a delete plus an add (`--no-renames`). A footprint
  asks how much had to be written, and a file moved wholesale really was.

  Exit codes: 0 whenever the figures could be measured. 2 only when the
  measurement itself is broken (a base that does not resolve, a git failure) --
  that means the figures cannot be trusted, never that the change is too wide.
  This script reports; it never gates.

.PARAMETER Base
  What to measure against. Defaults to `main`.

.PARAMETER Head
  The commit to measure. Omit to measure the working tree, untracked files
  included. Give it to measure a merged pull request (`-Base <baseRefOid>
  -Head <headRefOid>`), where the working tree is not involved at all.
#>
param(
  [string]$Base = "main",
  [string]$Head = ""
)

$repo = Split-Path $PSScriptRoot -Parent

# A project's own table, when present; layer order is significant: the first prefix that matches claims the path.
$layers = $null
$tablePath = Join-Path $PSScriptRoot "change-footprint.layers.json"
if (Test-Path $tablePath) {
  $layers = [ordered]@{}
  foreach ($row in (Get-Content -Raw $tablePath | ConvertFrom-Json)) { $layers[$row.name] = @($row.prefixes) }
  $layers["other"] = @()
}

$added = [ordered]@{}
$deleted = [ordered]@{}
$files = [ordered]@{}

function Get-Layer([string]$path) {
  if (-not $layers) {
    $slash = $path.IndexOf("/")
    if ($slash -lt 0) { return "root" }
    return $path.Substring(0, $slash)
  }
  foreach ($name in $layers.Keys) {
    foreach ($prefix in $layers[$name]) {
      if ($path -eq $prefix -or $path.StartsWith($prefix)) { return $name }
    }
  }
  return "other"
}

function Add-Row([string]$path, [int]$a, [int]$d) {
  $layer = Get-Layer $path
  if (-not $files.Contains($layer)) { $added[$layer] = 0; $deleted[$layer] = 0; $files[$layer] = 0 }
  $added[$layer] = $added[$layer] + $a
  $deleted[$layer] = $deleted[$layer] + $d
  $files[$layer] = $files[$layer] + 1
}

if ($Head) {
  $numstat = & git -C $repo diff --numstat --no-renames $Base $Head 2>&1
} else {
  $numstat = & git -C $repo diff --numstat --no-renames $Base 2>&1
}
if ($LASTEXITCODE -ne 0) {
  Write-Host "change-footprint: FAIL - 'git diff' against '$Base' failed, so the footprint could not be measured: $numstat"
  exit 2
}

foreach ($line in $numstat) {
  if (-not $line) { continue }
  $parts = "$line" -split "`t"
  if ($parts.Count -lt 3) { continue }
  # A binary file reports "-" for both counts; it still cost a file to change.
  $a = 0; $d = 0
  if ($parts[0] -ne "-") { $a = [int]$parts[0] }
  if ($parts[1] -ne "-") { $d = [int]$parts[1] }
  Add-Row $parts[2] $a $d
}

# Only a working-tree measurement has untracked files to find; a commit range
# has none by construction.
if (-not $Head) {
  $status = & git -C $repo status --porcelain --untracked-files=all 2>&1
  if ($LASTEXITCODE -ne 0) {
    Write-Host "change-footprint: FAIL - 'git status' failed, so untracked files could not be counted: $status"
    exit 2
  }
  foreach ($line in $status) {
    if ("$line" -notmatch '^\?\? (.+)$') { continue }
    $path = $Matches[1].Trim('"')
    $full = Join-Path $repo $path
    $count = 0
    if (Test-Path -LiteralPath $full -PathType Leaf) {
      try { $count = ([System.IO.File]::ReadAllLines($full)).Count } catch { $count = 0 }
    }
    Add-Row $path $count 0
  }
}

$segments = @()
$totalAdded = 0; $totalDeleted = 0; $totalFiles = 0
# A table's order is the print order; derived layers print in the order first met.
$order = if ($layers) { @($layers.Keys | Where-Object { $files.Contains($_) }) } else { @($files.Keys) }
foreach ($name in $order) {
  $totalAdded += $added[$name]; $totalDeleted += $deleted[$name]; $totalFiles += $files[$name]
  if ($files[$name] -eq 0) { continue }
  $noun = if ($files[$name] -eq 1) { "file" } else { "files" }
  $segments += ("{0} +{1}/-{2} in {3} {4}" -f $name, $added[$name], $deleted[$name], $files[$name], $noun)
}

$against = if ($Head) { "$Base..$Head" } else { "$Base..worktree" }
if ($segments.Count -eq 0) {
  Write-Host "change-footprint: nothing changed against $against"
  exit 0
}

$totalNoun = if ($totalFiles -eq 1) { "file" } else { "files" }
Write-Host ("change-footprint: {0}; TOTAL +{1}/-{2} in {3} {4} (vs {5})" -f `
  ($segments -join "; "), $totalAdded, $totalDeleted, $totalFiles, $totalNoun, $against)
exit 0
