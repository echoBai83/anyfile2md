@echo off
rem ============================================
rem  anyfile2md - drag & drop entry
rem  Drop file(s) onto this .bat icon.
rem  Default: convert + pandoc clean-up.
rem ============================================
setlocal
set "BASE=%~dp0"
set "PYTHONPATH=%BASE%lib"
set PYTHONUTF8=1
echo Converting, please wait...
echo.
python "%BASE%converter.py" %*
echo.
echo Done. Press any key to close...
pause >nul
endlocal
