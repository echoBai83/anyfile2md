@echo off
rem ============================================
rem  All-Format to Markdown - raw output (no clean)
rem  Same as markdown_convert.bat but skips
rem  the pandoc GFM clean-up step.
rem ============================================
setlocal
set "BASE=%~dp0"
set "PYTHONPATH=%BASE%lib"
set PYTHONUTF8=1
echo Converting (no pandoc clean-up)...
echo.
python "%BASE%converter.py" --no-clean %*
echo.
echo Done. Press any key to close...
pause >nul
endlocal
