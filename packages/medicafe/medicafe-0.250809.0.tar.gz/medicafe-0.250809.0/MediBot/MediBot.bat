::MediBot.bat - Streamlined version with coordinated debug system
@echo off
setlocal enabledelayedexpansion

:: Debug mode selection
echo ========================================
echo           MediCafe Launcher
echo ========================================
echo.
echo Choose your mode:
echo 1. Normal Mode - Production
echo 2. Debug Mode - Full diagnostics (Interactive)
echo 3. Debug Mode - Full diagnostics (Non-Interactive)
echo.
set /p debug_choice="Enter your choice (1-3): "

if "!debug_choice!"=="1" goto start_normal_mode
if "!debug_choice!"=="2" goto start_debug_interactive
if "!debug_choice!"=="3" goto start_debug_noninteractive
goto start_normal_mode

:start_debug_interactive
echo.
echo ========================================
echo        DEBUG MODE (INTERACTIVE)
echo ========================================
echo Running full diagnostic suite...
echo.
set "SKIP_CLS_AFTER_DEBUG=1"
call "%~dp0full_debug_suite.bat" /interactive
echo.
goto normal_mode

:start_debug_noninteractive
echo.
echo ========================================
echo     DEBUG MODE (NON-INTERACTIVE)
echo ========================================
echo Running full diagnostic suite...
echo.
set "SKIP_CLS_AFTER_DEBUG=1"
call "%~dp0full_debug_suite.bat"
echo.
goto normal_mode

:start_normal_mode
echo Starting Normal Mode...
goto normal_mode

:normal_mode
:: Normal production mode - streamlined without excessive debug output
if not defined SKIP_CLS_AFTER_DEBUG cls
set "SKIP_CLS_AFTER_DEBUG="
echo ========================================
echo           MediBot Starting
echo ========================================
echo.

:: Define paths with local fallbacks for F: drive dependencies
set "source_folder=C:\MEDIANSI\MediCare"
set "target_folder=C:\MEDIANSI\MediCare\CSV"
set "python_script=C:\Python34\Lib\site-packages\MediBot\update_json.py"
set "python_script2=C:\Python34\Lib\site-packages\MediBot\Medibot.py"
set "medicafe_package=medicafe"

:: Priority order: 1) Local relative path, 2) F: drive path (legacy)
set "upgrade_medicafe_local=MediBot\update_medicafe.py"
set "upgrade_medicafe_legacy=F:\Medibot\update_medicafe.py"

:: Storage and config paths with local fallbacks
set "local_storage_legacy=F:\Medibot\DOWNLOADS"
set "local_storage_local=MediBot\DOWNLOADS"
set "config_file_legacy=F:\Medibot\json\config.json"
set "config_file_local=MediBot\json\config.json"
set "temp_file_legacy=F:\Medibot\last_update_timestamp.txt"
set "temp_file_local=MediBot\last_update_timestamp.txt"

:: FIXED: Always prioritize local file if it exists
if exist "%upgrade_medicafe_local%" (
    set "upgrade_medicafe=%upgrade_medicafe_local%"
    set "use_local_update=1"
) else (
    set "use_local_update=0"
)

:: Determine which paths to use based on availability
if exist "F:\Medibot" (
    set "local_storage_path=%local_storage_legacy%"
    set "config_file=%config_file_legacy%"
    set "temp_file=%temp_file_legacy%"
    
    :: Only use F: drive update script if local doesn't exist
    if "!use_local_update!"=="0" (
        if exist "%upgrade_medicafe_legacy%" (
            set "upgrade_medicafe=%upgrade_medicafe_legacy%"
        )
    )
) else (
    set "local_storage_path=%local_storage_local%"
    set "config_file=%config_file_local%"
    set "temp_file=%temp_file_local%"
    :: Ensure local directories exist
    if not exist "MediBot\json" mkdir "MediBot\json" 2>nul
    if not exist "MediBot\DOWNLOADS" mkdir "MediBot\DOWNLOADS" 2>nul
)

set "firefox_path=C:\Program Files\Mozilla Firefox\firefox.exe"
set "claims_status_script=..\MediLink\MediLink_ClaimStatus.py"
set "deductible_script=..\MediLink\MediLink_Deductible.py"
set "package_version="
set PYTHONWARNINGS=ignore

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please run in Debug Mode to diagnose Python issues.
    pause
    exit /b 1
)

:: Check if critical directories exist
if not exist "%source_folder%" (
    echo [WARNING] Source folder not found at: %source_folder%
    set /p provide_alt_source="Enter 'Y' to provide alternate path, or any other key to continue: "
    if /i "!provide_alt_source!"=="Y" (
        set /p alt_source_folder="Enter the alternate source folder path: "
        if not "!alt_source_folder!"=="" set "source_folder=!alt_source_folder!"
    )
)

if not exist "%target_folder%" (
    mkdir "%target_folder%" 2>nul
)

:: Check if the MediCafe package is installed
python -c "import pkg_resources; print('MediCafe=='+pkg_resources.get_distribution('medicafe').version)" 2>nul
if errorlevel 1 (
    echo [WARNING] MediCafe package not found. Attempting to install...
    python -m pip install medicafe --upgrade
    if errorlevel 1 (
        echo [ERROR] Failed to install MediCafe package.
        echo Please run in Debug Mode to diagnose package issues.
        pause
        exit /b 1
    )
)

:: Determine installed MediCafe version
set "package_version="
set "medicafe_version="
python -c "import pkg_resources; print('MediCafe=='+pkg_resources.get_distribution('medicafe').version)" > temp.txt 2>nul
set /p package_version=<temp.txt
if exist temp.txt del temp.txt
if not defined package_version (
    rem Fallback: try importing MediCafe and reading __version__
    python -c "import sys;\ntry:\n import MediCafe;\n print('MediCafe=='+getattr(MediCafe, '__version__','unknown'))\nexcept Exception as e:\n print('')" > temp.txt 2>nul
    set /p package_version=<temp.txt
    if exist temp.txt del temp.txt
)
if defined package_version (
    for /f "tokens=2 delims==" %%a in ("%package_version%") do set "medicafe_version=%%a"
) else (
    set "medicafe_version=unknown"
)

:: Check for internet connectivity
ping -n 1 google.com >nul 2>&1
if errorlevel 1 (
    set "internet_available=0"
) else (
    set "internet_available=1"
    echo Internet connection detected.
)

:: Common pre-menu setup
echo Setting up the environment...
if not exist "%config_file%" (
    echo Configuration file missing.
    echo.
    echo Expected configuration file path: %config_file%
    echo.
    echo Would you like to provide an alternate path for the configuration file?
    set /p provide_alt="Enter 'Y' to provide alternate path, or any other key to exit: "
    if /i "!provide_alt!"=="Y" (
        echo.
        echo Please enter the full path to your configuration file.
        echo Example: C:\MediBot\config\config.json
        echo Example with spaces: "G:\My Drive\MediBot\config\config.json"
        echo.
        echo Note: If your path contains spaces, please include quotes around the entire path.
        echo.
        set /p alt_config_path="Enter configuration file path: "
        :: Remove any surrounding quotes from user input and re-add them for consistency
        set "alt_config_path=!alt_config_path:"=!"
        if exist "!alt_config_path!" (
            echo Configuration file found at: !alt_config_path!
            set "config_file=!alt_config_path!"
            goto config_check_complete
        ) else (
            echo Configuration file not found at: !alt_config_path!
            echo.
            set /p retry="Would you like to try another path? (Y/N): "
            if /i "!retry!"=="Y" (
                goto retry_config_path
            ) else (
                goto end_script
            )
        )
    ) else (
        goto end_script
    )
) else (
    goto config_check_complete
)

:retry_config_path
echo.
echo Please enter the full path to your configuration file.
echo Example: C:\MediBot\config\config.json
echo Example with spaces: "G:\My Drive\MediBot\config\config.json"
echo.
echo Note: If your path contains spaces, please include quotes around the entire path.
echo.
set /p alt_config_path="Enter configuration file path: "
:: Remove any surrounding quotes from user input and re-add them for consistency
set "alt_config_path=!alt_config_path:"=!"
if exist "!alt_config_path!" (
    echo Configuration file found at: !alt_config_path!
    set "config_file=!alt_config_path!"
) else (
    echo Configuration file not found at: !alt_config_path!
    echo.
    set /p retry="Would you like to try another path? (Y/N): "
    if /i "!retry!"=="Y" (
        goto retry_config_path
    ) else (
        goto end_script
    )
)

:config_check_complete

:: Check if the file exists and attempt to copy it to the local directory
echo Checking for the update script...
ping -n 2 127.0.0.1 >nul

:: Continue with existing logic but with enhanced error reporting
:: First check if we already have it locally
if exist "%upgrade_medicafe_local%" (
    echo Found update_medicafe.py in local directory. No action needed.
    ping -n 2 127.0.0.1 >nul
) else (
    if exist "C:\Python34\Lib\site-packages\MediBot\update_medicafe.py" (
        echo Found update_medicafe.py in site-packages. Copying to local directory...
        ping -n 2 127.0.0.1 >nul
        :: Ensure MediBot directory exists
        if not exist "MediBot" mkdir "MediBot"
        copy "C:\Python34\Lib\site-packages\MediBot\update_medicafe.py" "%upgrade_medicafe_local%" >nul 2>&1
        if %errorlevel% neq 0 (
            echo Copy to local directory failed. Error code: %errorlevel%
            echo [DIAGNOSTIC] Attempting copy to F: drive - detailed error reporting
            ping -n 2 127.0.0.1 >nul
            :: Ensure F:\Medibot directory exists (only if F: drive is accessible)
            if exist "F:\" (
                if not exist "F:\Medibot" (
                    echo [DIAGNOSTIC] Creating F:\Medibot directory...
                    mkdir "F:\Medibot" 2>nul
                    if not exist "F:\Medibot" (
                        echo [ERROR] Failed to create F:\Medibot - Permission denied or read-only drive
                    )
                )
                if exist "F:\Medibot" (
                    echo [DIAGNOSTIC] Attempting file copy to F:\Medibot...
                    copy "C:\Python34\Lib\site-packages\MediBot\update_medicafe.py" "%upgrade_medicafe_legacy%" 2>nul
                    if %errorlevel% neq 0 (
                        echo [ERROR] Copy to F:\Medibot failed with error code: %errorlevel%
                        echo [ERROR] Possible causes:
                        echo    - Permission denied [insufficient write access]
                        echo    - Disk full
                        echo    - File locked by another process
                        echo    - Antivirus blocking the operation
                    ) else (
                        echo [SUCCESS] File copied to F:\Medibot successfully
                    )
                )
            ) else (
                echo [ERROR] F: drive not accessible - skipping F: drive copy attempt
            )
        ) else (
            echo File copied to local directory successfully.
            ping -n 2 127.0.0.1 >nul
        )
    ) else (
        if exist "%upgrade_medicafe_legacy%" (
            echo Found update_medicafe.py in legacy F: drive location.
            echo [DIAGNOSTIC] Verifying F: drive file accessibility...
            type "%upgrade_medicafe_legacy%" | find "#update_medicafe.py" >nul 2>&1
            if %errorlevel% equ 0 (
                echo [OK] F: drive file is accessible and readable
            ) else (
                echo [ERROR] F: drive file exists but cannot be read [permission/lock issue]
            )
            ping -n 2 127.0.0.1 >nul
        ) else (
            echo update_medicafe.py not detected in any known location.
            echo.
            echo Checked locations:
            echo   - Site-packages: C:\Python34\Lib\site-packages\MediBot\update_medicafe.py
            echo   - Local: %upgrade_medicafe_local%
            echo   - Legacy: %upgrade_medicafe_legacy%
            echo.
            echo [DIAGNOSTIC] Current working directory:
            cd
            echo [DIAGNOSTIC] Current directory contents:
            dir /b
            echo.
            echo [DIAGNOSTIC] MediBot directory contents:
            dir /b MediBot\ 2>nul || echo MediBot directory not found
            echo.
            echo Continuing without update script...
            ping -n 2 127.0.0.1 >nul
        )
    )
)

:: Main menu
:main_menu
cls
echo Version: %medicafe_version%
echo --------------------------------------------------------------
echo              .//*  Welcome to MediBot  *\\. 
echo --------------------------------------------------------------
echo. 

if "!internet_available!"=="0" (
echo NOTE: No internet detected. Options 1-5 require internet.
    echo.
)
echo Please select an option:
echo.
echo 1. Update MediCafe
echo.
echo 2. Download Email de Carol
echo.
echo 3. MediLink Claims
echo.
echo 4. ^[United^] Claims Status
echo.
echo 5. ^[United^] Deductible
echo.
echo 6. Run MediBot
echo.
echo 7. Troubleshooting
echo.
echo 9. Toggle Performance Logging (session)
echo.
echo 8. Exit
echo.
set /p choice=Enter your choice:  

:: Update option numbers
if "!choice!"=="8" goto end_script
if "!choice!"=="7" goto troubleshooting_menu
if "!choice!"=="6" goto medibot_flow
if "!choice!"=="5" goto united_deductible
if "!choice!"=="4" goto united_claims_status
if "!choice!"=="3" goto medilink_flow
if "!choice!"=="2" goto download_emails
if "!choice!"=="1" goto check_updates
if "!choice!"=="9" goto toggle_perf_logging
if "!choice!"=="0" goto end_script

echo Invalid choice. Please try again.
pause
goto main_menu

:: Medicafe Update
:check_updates
if "!internet_available!"=="0" (
    echo [WARNING] No internet connection available.
    goto main_menu
)

echo ========================================
echo Starting MediCafe Update Process
echo ========================================
echo.

:: Step 1: Check if update_medicafe.py exists in expected location
echo.
echo ========================================
echo DEBUG STEP 1: Checking for update script
echo ========================================
echo.
echo Checking for update script - priority: local first, then legacy path
if exist "%upgrade_medicafe_local%" (
    echo [SUCCESS] Found update script at: %upgrade_medicafe_local%
    echo File size: 
    dir "%upgrade_medicafe_local%" | find "update_medicafe.py"
    set "upgrade_medicafe=%upgrade_medicafe_local%"
) else (
    if exist "%upgrade_medicafe_legacy%" (
        echo [SUCCESS] Found update script at legacy location: %upgrade_medicafe_legacy%
        echo File size: 
        dir "%upgrade_medicafe_legacy%" | find "update_medicafe.py"
        set "upgrade_medicafe=%upgrade_medicafe_legacy%"
    ) else (
        echo [FAILED] Update script not found in either location:
        echo   - Local: %upgrade_medicafe_local%
        echo   - Legacy: %upgrade_medicafe_legacy%
        echo.
        echo Available files in current directory:
        dir /b
        echo.
        echo Available files in MediBot directory:
        dir /b MediBot\ 2>nul || echo MediBot directory not found
    )
)
echo.
echo Press Enter to continue to step 2...
pause >nul

:: Step 2: Verify Python installation and path
echo.
echo ========================================
echo DEBUG STEP 2: Python Environment Check
echo ========================================
echo.
echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH
    echo Current PATH: %PATH%
) else (
    echo [SUCCESS] Python found
    echo Python executable:
    python -c "import sys; print(sys.executable)"
    echo Python version:
    python --version
)
echo.
echo Checking pip installation...
python -m pip --version
if %errorlevel% neq 0 (
    echo [ERROR] pip not found
) else (
    echo [SUCCESS] pip found
    echo pip version:
    python -m pip --version
)
echo.
echo Press Enter to continue to step 3...
pause >nul

:: Step 3: Check MediCafe package installation
echo.
echo ========================================
echo DEBUG STEP 3: MediCafe Package Check
echo ========================================
echo.
echo Checking MediCafe package installation...
python -c "import pkg_resources; print('MediCafe=='+pkg_resources.get_distribution('medicafe').version)" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] MediCafe package not found or error accessing
    echo.
    echo Checking if MediCafe is importable...
    python -c "import MediCafe; print('MediCafe module found')" 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] MediCafe module not importable
    ) else (
        echo [SUCCESS] MediCafe module is importable
    )
) else (
    echo [SUCCESS] MediCafe package found
    echo Package version: %package_version%
)
echo.
echo Press Enter to continue to step 4...
pause >nul

:: Step 4: Check internet connectivity
echo.
echo ========================================
echo DEBUG STEP 4: Internet Connectivity
echo ========================================
echo.
echo Testing internet connectivity...
ping -n 1 google.com >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No internet connection detected
    echo Cannot proceed with update without internet
    echo.
    echo Press Enter to return to main menu...
    pause >nul
    goto main_menu
)

echo Starting update process...
echo Update script: %upgrade_medicafe%
echo.

:: Check if update_medicafe.py exists using the new priority system
if exist "%upgrade_medicafe_local%" (
    echo [INFO] Using local update script at: %upgrade_medicafe_local%
    echo Command: python "%upgrade_medicafe_local%" %package_version%
    
    :: Pre-execution diagnostics
    echo.
    echo [DIAGNOSTIC] Pre-execution checks for local script:
    echo [DIAGNOSTIC] File size and permissions:
    dir "%upgrade_medicafe_local%" 2>nul || echo [!] Cannot read file details
    echo [DIAGNOSTIC] Testing Python access to file:
    python -c "import os; print('[OK] Python can access file') if os.path.exists('%upgrade_medicafe_local%') else print('[ERROR] Python cannot access file')" 2>nul || echo [!] Python test failed
    
    echo.
    echo Press Enter to execute update command...
    pause >nul
    echo.
    echo Executing update command...
    echo.
    echo The update window will open and show detailed progress.
    echo All output will be displayed on screen.
    echo.
    start "Medicafe Update" cmd /v:on /c "echo [DIAGNOSTIC] About to execute: python \"%upgrade_medicafe_local%\" %package_version% & echo. & python \"%upgrade_medicafe_local%\" %package_version% & echo. & echo [DIAGNOSTIC] Python exit code: !ERRORLEVEL! & echo Update process completed. Press any key to close... & pause >nul" && (
        echo %DATE% %TIME% Upgrade initiated successfully - local. >> "%temp_file%"
        echo [SUCCESS] Update process started successfully
        echo All output will be displayed in the update window.
    ) || (
        echo %DATE% %TIME% Update failed - local. >> "%temp_file%"
        echo [ERROR] Upgrade failed. Check the update window for details.
        echo [DIAGNOSTIC] Possible causes for local script failure:
        echo    - Python not in PATH
        echo    - Script syntax error
        echo    - Missing Python dependencies
        echo    - File corruption
    )
) else (
    if exist "%upgrade_medicafe_legacy%" (
        echo [INFO] Using legacy update script at: %upgrade_medicafe_legacy%
        echo Command: python "%upgrade_medicafe_legacy%" %package_version%
        
        :: Pre-execution diagnostics for F: drive
        echo.
        echo [DIAGNOSTIC] Pre-execution checks for F: drive script:
        echo [DIAGNOSTIC] File size and permissions:
        dir "%upgrade_medicafe_legacy%" 2>nul || echo [!] Cannot read file details
        echo [DIAGNOSTIC] Testing Python access to F: drive file:
        python -c "import os; print('[OK] Python can access F: drive file') if os.path.exists('%upgrade_medicafe_legacy%') else print('[ERROR] Python cannot access F: drive file')" 2>nul || echo [!] Python F: drive test failed
        echo [DIAGNOSTIC] Testing file read permissions:
        type "%upgrade_medicafe_legacy%" | find "#update_medicafe.py" >nul 2>&1 && echo [OK] File content readable || echo [ERROR] Cannot read file content
        
        echo.
        echo Press Enter to execute update command...
        pause >nul
        echo.
        echo Executing update command...
        start "Medicafe Update" cmd /v:on /c "echo [DIAGNOSTIC] About to execute: python \"%upgrade_medicafe_legacy%\" %package_version% & echo [DIAGNOSTIC] F: drive accessibility test... & dir F:\ ^| find \"Directory of\" ^>nul 2^>^&1 ^&^& echo [OK] F: drive accessible ^|^| echo [ERROR] F: drive access lost & echo. & python \"%upgrade_medicafe_legacy%\" %package_version% & echo. & echo [DIAGNOSTIC] Python exit code: !ERRORLEVEL! & echo Update process completed. Press any key to close... & pause >nul" && (
            echo %DATE% %TIME% Upgrade initiated successfully - legacy. >> "%temp_file%"
            echo [SUCCESS] Update process started successfully
            echo All output will be displayed in the update window.
        ) || (
        echo %DATE% %TIME% Update failed - legacy. >> "%temp_file%"
        echo [ERROR] Upgrade failed. Check the update window for details.
        echo [DIAGNOSTIC] Possible causes for F: drive script failure:
        echo    - F: drive disconnected during execution
        echo    - Permission denied accessing F: drive
        echo    - F: drive file locked by antivirus
        echo    - Network drive timeout
        echo    - Python cannot access network paths
    )
) else (
    echo [ERROR] update_medicafe.py not found in either location
    echo Expected locations:
    echo   - Local: %upgrade_medicafe_local%
    echo   - Legacy: %upgrade_medicafe_legacy%
    echo.
    echo Current directory contents:
    dir /b
    echo.
    echo MediBot directory contents:
    dir /b MediBot\ 2>nul || echo MediBot directory not found
    echo.
    echo %DATE% %TIME% Update failed - script not found. >> "%temp_file%"
    echo.
    echo Press Enter to return to main menu...
    pause >nul
    goto main_menu
)

echo.
echo Update process has been initiated.
echo All output will be displayed in the update window.
echo.
pause
goto main_menu

:: Download Carol's Emails
:download_emails
if "!internet_available!"=="0" (
    echo [WARNING] No internet connection available.
    goto main_menu
)

call "%~dp0process_csvs.bat"
cls
echo Starting email download via MediCafe...
cd /d "%~dp0.."
python -m MediCafe download_emails
if errorlevel 1 (
    echo [ERROR] Failed to download emails.
    pause
)

pause
goto main_menu

:: MediBot Flow
:medibot_flow
cls
echo Starting MediBot flow...
cd /d "%~dp0.."
python -m MediCafe medibot
if errorlevel 1 (
    echo [ERROR] Failed to start MediBot flow.
    pause
)

pause
goto main_menu

:: MediLink Flow
:medilink_flow
cls
echo Starting MediLink flow...
cd /d "%~dp0.."
python -m MediCafe medilink
if errorlevel 1 (
    echo [ERROR] Failed to start MediLink flow.
    pause
)

pause
goto main_menu

:toggle_perf_logging
cls
echo ========================================
echo Performance Logging (session toggle)
echo ========================================
echo.
if /I "%MEDICAFE_PERFORMANCE_LOGGING%"=="1" (
  set "MEDICAFE_PERFORMANCE_LOGGING=0"
  echo Turned OFF performance logging for this session.
) else (
  set "MEDICAFE_PERFORMANCE_LOGGING=1"
  echo Turned ON performance logging for this session.
)
echo.
echo Note: This affects current session only. To persist, set in config.json.
pause
goto main_menu

:: United Claims Status
:united_claims_status
cls
echo Starting United Claims Status...
cd /d "%~dp0.."
python -m MediCafe claims_status
if errorlevel 1 (
    echo [ERROR] Failed to start United Claims Status.
    pause
)

pause
goto main_menu

:: United Deductible
:united_deductible
cls
echo Starting United Deductible...
cd /d "%~dp0.."
python -m MediCafe deductible
if errorlevel 1 (
    echo [ERROR] Failed to start United Deductible.
    pause
)

pause
goto main_menu

:: Process CSV Files moved to external script
:process_csvs
call "%~dp0process_csvs.bat"
goto :eof

REM [removed legacy :clear_cache block in favor of :clear_cache_menu]

REM [removed duplicate :clear_cache quick block; use :clear_cache_menu instead]

:: Clear Cache submenu (Quick vs Deep)
:clear_cache_menu
cls
echo ========================================
echo Clear Python Cache
echo ========================================
echo.
echo 1. Quick clear - compileall + delete __pycache__
echo 2. Deep clear via update_medicafe.py
echo 3. Back
echo.
set /p cc_choice=Enter your choice: 
if "%cc_choice%"=="1" goto clear_cache_quick
if "%cc_choice%"=="2" goto clear_cache_deep
if "%cc_choice%"=="3" goto troubleshooting_menu
echo Invalid choice. Press any key to continue...
pause >nul
goto clear_cache_menu

:clear_cache_quick
echo Running quick cache clear...
call "%~dp0clear_cache.bat" --quick
pause
goto troubleshooting_menu

:clear_cache_deep
cls
echo Deep cache clear using update_medicafe.py...
echo.
call "%~dp0clear_cache.bat" --deep
pause
goto troubleshooting_menu

:: Troubleshooting Submenu
:troubleshooting_menu
cls
echo Troubleshooting Options:
echo.
echo 1. Open Latest Log File
echo 2. Clear Python Cache
echo 3. Forced MediCafe version rollback - no dependencies
echo 4. Back to Main Menu
echo.
set /p tchoice=Enter your choice: 
if "%tchoice%"=="1" goto open_latest_log
if "%tchoice%"=="2" goto clear_cache_menu
if "%tchoice%"=="3" goto forced_version_rollback
if "%tchoice%"=="4" goto main_menu
echo Invalid choice. Please try again.
pause
goto troubleshooting_menu

:: Open Latest Log (streamlined)
:open_latest_log
echo Opening the latest log file...
set "latest_log="
for /f "delims=" %%a in ('dir /b /a-d /o-d "%local_storage_path%\*.log" 2^>nul') do (
    set "latest_log=%%a"
    goto open_log_found
)

echo No log files found in %local_storage_path%.
pause
goto troubleshooting_menu

:: End Script
:end_script
echo Exiting MediBot
exit /b 0

:: Full Debug Mode moved to external script full_debug_suite.bat

:: Opened log file handling and helpers
:open_log_found
echo Found log file: %latest_log%
start notepad "%local_storage_path%\%latest_log%" >nul 2>&1
if %errorlevel% neq 0 (
    start write "%local_storage_path%\%latest_log%" >nul 2>&1
)
if %errorlevel% neq 0 (
    call :tail "%local_storage_path%\%latest_log%" 50
)
pause
goto troubleshooting_menu

:: Forced version rollback for MediCafe (hardcoded version placeholder)
:forced_version_rollback
cls
echo ========================================
echo Forced MediCafe Version Rollback
echo ========================================
echo.
if "!internet_available!"=="0" (
    echo No internet connection available.
    echo Cannot proceed with rollback without internet.
    pause >nul
    goto troubleshooting_menu
)
set "rollback_version=0.250529.2"
echo Forcing reinstall of %medicafe_package%==%rollback_version% with no dependencies...
python -m pip install --no-deps --force-reinstall %medicafe_package%==%rollback_version%
if errorlevel 1 (
    echo.
    echo [ERROR] Forced rollback failed.
    pause >nul
    goto troubleshooting_menu
)

:: Refresh displayed MediCafe version
set "package_version="
python -c "import pkg_resources; print('MediCafe=='+pkg_resources.get_distribution('medicafe').version)" > temp.txt 2>nul
set /p package_version=<temp.txt
if exist temp.txt del temp.txt
if defined package_version (
    for /f "tokens=2 delims==" %%a in ("%package_version%") do (
        set "medicafe_version=%%a"
    )
)
echo.
echo Rollback complete. Current MediCafe version: %medicafe_version%
pause >nul
goto troubleshooting_menu

:: Subroutine to display the last N lines of a file
:tail
:: Usage: call :tail filename number_of_lines
setlocal
set "file=%~1"
set /a lines=%~2

:: Get total line count robustly (avoid prefixed output)
set "count=0"
for /f %%a in ('type "%file%" ^| find /v /c ""') do set count=%%a

:: Compute starting line; clamp to 1
set /a start=count-lines+1
if !start! lss 1 set start=1

for /f "tokens=1* delims=:" %%a in ('findstr /n .* "%file%"') do (
    if %%a geq !start! echo %%b
)
endlocal & goto :eof