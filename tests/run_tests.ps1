$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Write-Host "== unit tests =="
python -m unittest discover -s (Join-Path $Root "tests") -p "test_*.py" -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "== CLI validate =="
python (Join-Path $Root "scripts\actor_cli.py") validate
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "== grok plugin validate =="
grok plugin validate $Root
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "ALL VALIDATED"
