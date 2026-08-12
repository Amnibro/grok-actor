@echo off
setlocal EnableExtensions
set "SCRIPT_DIR=%~dp0"
if defined GROK_PLUGIN_ROOT (
  set "PLUGIN_ROOT=%GROK_PLUGIN_ROOT%"
) else if defined CLAUDE_PLUGIN_ROOT (
  set "PLUGIN_ROOT=%CLAUDE_PLUGIN_ROOT%"
) else (
  for %%I in ("%SCRIPT_DIR%..") do set "PLUGIN_ROOT=%%~fI"
)
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY where python3 >nul 2>nul && set "PY=python3"
if not defined PY exit /b 0
%PY% "%PLUGIN_ROOT%\hooks\inject_actor.py"
exit /b 0
