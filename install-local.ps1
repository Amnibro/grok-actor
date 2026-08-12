# Install grok-actor into ~/.grok/plugins and enable it for /actor
$ErrorActionPreference = "Stop"
$src = Split-Path -Parent $MyInvocation.MyCommand.Path
$dstRoot = Join-Path $env:USERPROFILE ".grok\plugins"
$dst = Join-Path $dstRoot "grok-actor"
$grok = Join-Path $env:USERPROFILE ".grok\bin\grok.exe"
if (-not (Test-Path $grok)) {
  $g = Get-Command grok -ErrorAction SilentlyContinue
  if ($g) { $grok = $g.Source } else { throw "grok.exe not found" }
}
New-Item -ItemType Directory -Force -Path $dstRoot | Out-Null
Write-Host "Validating plugin at $src"
& $grok plugin validate $src
if ($LASTEXITCODE -ne 0) { Write-Host "validate returned $LASTEXITCODE (continuing if only warnings)" -ForegroundColor Yellow }
Write-Host "Installing (copy) -> $dst"
if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
Copy-Item -Recurse -Force $src $dst
@("backups","__pycache__",".git") | ForEach-Object {
  $p = Join-Path $dst $_
  if (Test-Path $p) { Remove-Item -Recurse -Force $p -ErrorAction SilentlyContinue }
}
Write-Host "CLI install --trust"
& $grok plugin install $dst --trust
Write-Host "Enable grok-actor"
& $grok plugin enable grok-actor 2>$null
# user-invocable skills at ~/.grok/skills (slash discovery)
$skillsSrc = Join-Path $src "skills"
$skillsDst = Join-Path $env:USERPROFILE ".grok\skills"
if (Test-Path $skillsSrc) {
  New-Item -ItemType Directory -Force -Path $skillsDst | Out-Null
  foreach ($sk in @("actor","gactor")) {
    $from = Join-Path $skillsSrc $sk
    $to = Join-Path $skillsDst $sk
    if (Test-Path $from) {
      if (Test-Path $to) { Remove-Item -Recurse -Force $to }
      Copy-Item -Recurse -Force $from $to
      $skillMd = Join-Path $to "SKILL.md"
      if (Test-Path $skillMd) {
        $t = Get-Content $skillMd -Raw
        $t = $t -replace "user-invocable:\s*false","user-invocable: true"
        Set-Content -Path $skillMd -Value $t -NoNewline
      }
      Write-Host "Synced skill $sk -> $to"
    }
  }
}
foreach ($cmd in @("actor-list.md","actor-set.md")) {
  $from = Join-Path $src "commands\$cmd"
  $to = Join-Path $env:USERPROFILE ".grok\commands\$cmd"
  if (Test-Path $from) {
    New-Item -ItemType Directory -Force -Path (Split-Path $to) | Out-Null
    Copy-Item $from $to -Force
  }
}
& $grok plugin list
Write-Host ""
Write-Host "Done. Restart Grok TUI or press r in /plugins to reload." -ForegroundColor Green
Write-Host "Then run:  /actor   or   /gactor" -ForegroundColor Cyan
