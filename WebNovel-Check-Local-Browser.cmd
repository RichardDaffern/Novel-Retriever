@echo off
setlocal
cd /d "%~dp0"
echo.
echo WebNovel - Local Browser Access Check
echo.
echo This opens a TEMPORARY, UNMODIFIED Chromium browser.
echo Checks 3 known public chapter links without saving any chapter text.
echo No login, browser profile, cookies, EPUB export or bypass.
echo.
echo If Playwright is missing, install it in the repo environment:
echo   py -m pip install playwright
echo   py -m playwright install chromium
echo.
py -m tools.webnovel_local_browser_diagnostic ^
  --book-url "https://www.webnovel.com/book/33422293300201205" ^
  --sample "1=https://www.webnovel.com/book/33422293300201205/89735050081387238" ^
  --sample "400=https://www.webnovel.com/book/33422293300201205/94052948610440202" ^
  --sample "844=https://www.webnovel.com/book/33422293300201205/98111515671985466"
set "result=%errorlevel%"
echo.
if not "%result%"=="0" (
  echo Browser access is unverified or blocked. Please share the result JSON.
  echo Do not repeatedly retry access denials or challenges.
) else (
  echo Sampled browser pages were readable. This is NOT permission to bulk export.
)
echo.
pause
exit /b %result%
