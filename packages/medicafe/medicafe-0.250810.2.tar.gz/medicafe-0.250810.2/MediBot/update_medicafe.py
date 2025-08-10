#update_medicafe.py
import subprocess, sys, time, platform, os, shutil

# Safe import for pkg_resources with fallback
try:
    import pkg_resources
except ImportError:
    pkg_resources = None
    print("Warning: pkg_resources not available. Some functionality may be limited.")

# Safe import for requests with fallback
try:
    import requests
except ImportError:
    requests = None
    print("Warning: requests module not available. Some functionality may be limited.")

# Initialize console output
print("="*60)
print("MediCafe Update Started")
print("Timestamp: {}".format(time.strftime("%Y-%m-%d %H:%M:%S")))
print("Python Version: {}".format(sys.version))
print("Platform: {}".format(platform.platform()))
print("="*60)

# Global debug mode toggle (defaults to streamlined mode)
DEBUG_MODE = False

def debug_step(step_number, step_title, message=""):
    """Print step information. Only show debug output in debug mode."""
    if DEBUG_MODE:
        print("\n" + "="*60)
        print("STEP {}: {}".format(step_number, step_title))
        print("="*60)
        if message:
            print(message)
        
        # In debug mode, optionally pause for key steps
        if step_number in [1, 7, 8]:
            print("\nPress Enter to continue...")
            try:
                input()
            except:
                pass
        else:
            print("\nContinuing...")
    else:
        # Streamlined mode: no debug output, no pauses
        pass

def print_status(message, status_type="INFO"):
    """Print formatted status messages with ASCII-only visual indicators."""
    if status_type == "SUCCESS":
        print("\n" + "="*60)
        print("[SUCCESS] {}".format(message))
        print("="*60)
    elif status_type == "ERROR":
        print("\n" + "="*60)
        print("[ERROR] {}".format(message))
        print("="*60)
    elif status_type == "WARNING":
        print("\n" + "-"*60)
        print("[WARNING] {}".format(message))
        print("-"*60)
    elif status_type == "INFO":
        print("\n" + "-"*60)
        print("[INFO] {}".format(message))
        print("-"*60)
    else:
        print(message)

def print_final_result(success, message):
    """Print final result with clear visual indication."""
    if success:
        print_status("UPDATE COMPLETED SUCCESSFULLY", "SUCCESS")
        print("Final Status: {}".format(message))
    else:
        print_status("UPDATE FAILED", "ERROR")
        print("Final Status: {}".format(message))
    
    print("\nExiting in 5 seconds...")
    time.sleep(5)
    sys.exit(0 if success else 1)

def get_installed_version(package):
    try:
        process = subprocess.Popen(
            [sys.executable, '-m', 'pip', 'show', package],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            for line in stdout.decode().splitlines():
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()
        return None
    except Exception as e:
        print("Error retrieving installed version: {}".format(e))
        return None

def get_latest_version(package, retries=3, delay=1):
    """
    Fetch the latest version of the specified package from PyPI with retries.
    """
    if not requests:
        print("Error: requests module not available. Cannot fetch latest version.")
        return None
        
    for attempt in range(1, retries + 1):
        try:
            response = requests.get("https://pypi.org/pypi/{}/json".format(package), timeout=10)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            latest_version = data['info']['version']
            
            # Print the version with attempt information (only in debug mode)
            if DEBUG_MODE:
                if attempt == 1:
                    print("Latest available version: {}".format(latest_version))
                else:
                    print("Latest available version: {} ({} attempt)".format(latest_version, attempt))
            
            # Check if the latest version is different from the current version
            current_version = get_installed_version(package)
            if current_version and compare_versions(latest_version, current_version) == 0:
                # If the versions are the same, perform a second request
                time.sleep(delay)
                response = requests.get("https://pypi.org/pypi/{}/json".format(package), timeout=10)
                response.raise_for_status()
                data = response.json()
                latest_version = data['info']['version']
            
            return latest_version  # Return the version after the check
        except requests.RequestException as e:
            if DEBUG_MODE:
                print("Attempt {}: Error fetching latest version: {}".format(attempt, e))
                if attempt < retries:
                    print("Retrying in {} seconds...".format(delay))
            time.sleep(delay)
    return None

def check_internet_connection():
    try:
        requests.get("http://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

def clear_python_cache(workspace_path=None):
    """
    Clear Python bytecode cache files to prevent import issues after updates.
    
    Args:
        workspace_path (str, optional): Path to the workspace root. If None, 
                                      will attempt to detect automatically.
    
    Returns:
        bool: True if cache was cleared successfully, False otherwise
    """
    try:
        if DEBUG_MODE:
            print_status("Clearing Python bytecode cache...", "INFO")
        
        # If no workspace path provided, try to detect it
        if not workspace_path:
            # Try to find the MediCafe workspace by looking for common directories
            current_dir = os.getcwd()
            potential_paths = [
                current_dir,
                os.path.dirname(current_dir),
                os.path.join(current_dir, '..'),
                os.path.join(current_dir, '..', '..')
            ]
            
            for path in potential_paths:
                if os.path.exists(os.path.join(path, 'MediCafe')) and \
                   os.path.exists(os.path.join(path, 'MediBot')) and \
                   os.path.exists(os.path.join(path, 'MediLink')):
                    workspace_path = path
                    break
        
        if not workspace_path:
            if DEBUG_MODE:
                print_status("Could not detect workspace path. Cache clearing skipped.", "WARNING")
            return False
        
        if DEBUG_MODE:
            print("Workspace path: {}".format(workspace_path))
        
        # Directories to clear cache from
        cache_dirs = [
            os.path.join(workspace_path, 'MediCafe'),
            os.path.join(workspace_path, 'MediBot'),
            os.path.join(workspace_path, 'MediLink'),
            workspace_path  # Root workspace
        ]
        
        cleared_count = 0
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                # Remove __pycache__ directories
                pycache_path = os.path.join(cache_dir, '__pycache__')
                if os.path.exists(pycache_path):
                    try:
                        shutil.rmtree(pycache_path)
                        if DEBUG_MODE:
                            print("Cleared cache: {}".format(pycache_path))
                        cleared_count += 1
                    except Exception as e:
                        if DEBUG_MODE:
                            print("Warning: Could not clear cache at {}: {}".format(pycache_path, e))
                
                # Remove .pyc files
                for root, dirs, files in os.walk(cache_dir):
                    for file in files:
                        if file.endswith('.pyc'):
                            try:
                                os.remove(os.path.join(root, file))
                                if DEBUG_MODE:
                                    print("Removed .pyc file: {}".format(os.path.join(root, file)))
                                cleared_count += 1
                            except Exception as e:
                                if DEBUG_MODE:
                                    print("Warning: Could not remove .pyc file {}: {}".format(file, e))
        
        if cleared_count > 0:
            if DEBUG_MODE:
                print_status("Successfully cleared {} cache items".format(cleared_count), "SUCCESS")
            return True
        else:
            if DEBUG_MODE:
                print_status("No cache files found to clear", "INFO")
            return True
            
    except Exception as e:
        if DEBUG_MODE:
            print_status("Error clearing cache: {}".format(e), "ERROR")
        return False

def compare_versions(version1, version2):
    v1_parts = list(map(int, version1.split(".")))
    v2_parts = list(map(int, version2.split(".")))
    return (v1_parts > v2_parts) - (v1_parts < v2_parts)

def upgrade_package(package, retries=3, delay=2):  # Updated retries to 3
    """
    Attempts to upgrade the package multiple times with delays in between.
    """
    if not check_internet_connection():
        print_status("No internet connection detected. Please check your internet connection and try again.", "ERROR")
        print_final_result(False, "No internet connection available")
    
    for attempt in range(1, retries + 1):
        if DEBUG_MODE:
            print("Attempt {} to upgrade {}...".format(attempt, package))
        process = subprocess.Popen(
            [
                sys.executable, '-m', 'pip', 'install', '--upgrade',
                package, '--no-cache-dir', '--disable-pip-version-check', '-q'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            if DEBUG_MODE:
                print(stdout.decode().strip())
            new_version = get_installed_version(package)  # Get new version after upgrade
            if compare_versions(new_version, get_latest_version(package)) >= 0:  # Compare versions
                if attempt == 1:
                    print_status("Upgrade succeeded!", "SUCCESS")
                else:
                    print_status("Attempt {}: Upgrade succeeded!".format(attempt), "SUCCESS")
                time.sleep(delay)
                return True
            else:
                print_status("Upgrade failed. Current version remains: {}".format(new_version), "WARNING")
                if attempt < retries:
                    if DEBUG_MODE:
                        print("Retrying in {} seconds...".format(delay))
                    time.sleep(delay)
        else:
            if DEBUG_MODE:
                print(stderr.decode().strip())
            print_status("Attempt {}: Upgrade failed.".format(attempt), "WARNING")
            if attempt < retries:
                if DEBUG_MODE:
                    print("Retrying in {} seconds...".format(delay))
                time.sleep(delay)
    
    print_status("All upgrade attempts failed.", "ERROR")
    return False

def ensure_dependencies():
    """Ensure all dependencies listed in setup.py are installed and up-to-date."""
    # Don't try to read requirements.txt as it won't be available after installation
    # Instead, hardcode the same dependencies that are in setup.py
    required_packages = [
        'requests==2.21.0',
        'argparse==1.4.0',
        'tqdm==4.14.0',
        'python-docx==0.8.11',
        'PyYAML==5.2',
        'chardet==3.0.4',
        'msal==1.26.0'
    ]

    # Define problematic packages for Windows XP with Python 3.4
    problematic_packages = ['numpy==1.11.3', 'pandas==0.20.0', 'lxml==4.2.0']
    is_windows_py34 = sys.version_info[:2] == (3, 4) and platform.system() == 'Windows'

    if is_windows_py34:
        print_status("Detected Windows with Python 3.4", "INFO")
        print("Please ensure the following packages are installed manually:")
        for pkg in problematic_packages:
            package_name, version = pkg.split('==')
            try:
                installed_version = pkg_resources.get_distribution(package_name).version
                print("{} {} is already installed".format(package_name, installed_version))
                if installed_version != version:
                    print("Note: Installed version ({}) differs from required ({})".format(installed_version, version))
                    print("If you experience issues, consider installing version {} manually".format(version))
            except pkg_resources.DistributionNotFound:
                print("{} is not installed".format(package_name))
                print("Please install {}=={} manually using a pre-compiled wheel".format(package_name, version))
                print("Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/")
                print("Then run: pip install path\\to\\{}-{}-cp34-cp34m-win32.whl".format(package_name, version))
        print("\nContinuing with other dependencies...")
    else:
        # Add problematic packages to the list for non-Windows XP environments
        required_packages.extend(problematic_packages)

    for pkg in required_packages:
        if '==' in pkg:
            package_name, version = pkg.split('==')  # Extract package name and version
        else:
            package_name = pkg
            version = None  # No specific version required

        # Skip problematic packages on Windows XP Python 3.4
        if is_windows_py34 and any(package_name in p for p in problematic_packages):
            continue

        try:
            installed_version = pkg_resources.get_distribution(package_name).version
            if version and installed_version != version:  # Check if installed version matches required version
                print("Current version of {}: {}".format(package_name, installed_version))
                print("Required version of {}: {}".format(package_name, version))
                time.sleep(2)  # Pause for 2 seconds to allow user to read the output
                if not upgrade_package(package_name):  # Attempt to upgrade/downgrade to the required version
                    print_status("Failed to upgrade/downgrade {} to version {}.".format(package_name, version), "WARNING")
                    time.sleep(2)  # Pause for 2 seconds after failure message
            elif version and installed_version == version:  # Check if installed version matches required version
                print("All versions match for {}. No changes needed.".format(package_name))
                time.sleep(1)  # Pause for 2 seconds to allow user to read the output
            elif not version:  # If no specific version is required, check for the latest version
                latest_version = get_latest_version(package_name)
                if latest_version and installed_version != latest_version:
                    print("Current version of {}: {}".format(package_name, installed_version))
                    print("Latest version of {}: {}".format(package_name, latest_version))
                    time.sleep(2)  # Pause for 2 seconds to allow user to read the output
                    if not upgrade_package(package_name):
                        print_status("Failed to upgrade {}.".format(package_name), "WARNING")
                        time.sleep(2)  # Pause for 2 seconds after failure message
        except pkg_resources.DistributionNotFound:
            print("Package {} is not installed. Attempting to install...".format(package_name))
            time.sleep(2)  # Pause for 2 seconds before attempting installation
            if not upgrade_package(package_name):
                print_status("Failed to install {}.".format(package_name), "WARNING")
                time.sleep(2)  # Pause for 2 seconds after failure message

def check_for_updates_only():
    """
    Check if a new version is available without performing the upgrade.
    Returns a simple status message for batch script consumption.
    """
    if not check_internet_connection():
        print("ERROR")
        return
    
    package = "medicafe"
    current_version = get_installed_version(package)
    if not current_version:
        print("ERROR")
        return
    
    latest_version = get_latest_version(package)
    if not latest_version:
        print("ERROR")
        return
    
    if compare_versions(latest_version, current_version) > 0:
        print("UPDATE_AVAILABLE:" + latest_version)
    else:
        print("UP_TO_DATE")

def main():
    global DEBUG_MODE
    # Enable debug mode if requested via CLI or environment
    DEBUG_MODE = ('--debug' in sys.argv) or (os.environ.get('MEDICAFE_DEBUG', '0') in ['1', 'true', 'TRUE'])

    # Always show the header for user feedback
    print("="*60)
    print("MediCafe Update Utility")
    print("="*60)
    print("Timestamp: {}".format(time.strftime("%Y-%m-%d %H:%M:%S")))
    print("Python Version: {}".format(sys.version.split()[0]))
    print("Platform: {}".format(platform.system()))
    print("="*60)
    print()
    
    # STEP 1: Environment Information (always show basic info)
    print("STEP 1: Environment Check")
    print("-" * 40)
    print("Working Directory: {}".format(os.getcwd()))
    print("Script Location: {}".format(os.path.basename(__file__)))
    print("Python Executable: {}".format(sys.executable))
    print()
    
    # STEP 2: Check Python and pip (always verify)
    print("STEP 2: Python Environment")
    print("-" * 40)
    print("Checking Python installation...")
    try:
        process = subprocess.Popen([sys.executable, '--version'], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print("Python: {}".format(stdout.decode().strip()))
        else:
            print("Python: ERROR - {}".format(stderr.decode().strip()))
            print_final_result(False, "Python installation check failed")
    except Exception as e:
        print("Python: ERROR - {}".format(e))
        print_final_result(False, "Python installation check failed")
    
    print("Checking pip installation...")
    try:
        process = subprocess.Popen([sys.executable, '-m', 'pip', '--version'], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print("pip: {}".format(stdout.decode().strip()))
        else:
            print("pip: ERROR - {}".format(stderr.decode().strip()))
            print_final_result(False, "pip installation check failed")
    except Exception as e:
        print("pip: ERROR - {}".format(e))
        print_final_result(False, "pip installation check failed")
    print()
    
    # STEP 3: Check MediCafe package (always check)
    print("STEP 3: MediCafe Package")
    print("-" * 40)
    package = "medicafe"
    current_version = get_installed_version(package)
    if current_version:
        print("Current Version: {}".format(current_version))
    else:
        print("MediCafe: NOT INSTALLED")
        print("Attempting to install MediCafe...")
        if upgrade_package(package):
            current_version = get_installed_version(package)
            if current_version:
                print("MediCafe installed successfully: {}".format(current_version))
            else:
                print_final_result(False, "Failed to install MediCafe")
        else:
            print_final_result(False, "Failed to install MediCafe")
    print()
    
    # STEP 4: Internet connectivity (always check)
    print("STEP 4: Internet Connection")
    print("-" * 40)
    print("Testing internet connectivity...")
    if check_internet_connection():
        print("Internet: CONNECTED")
        if DEBUG_MODE:
            print("Testing PyPI connectivity...")
            try:
                response = requests.get("https://pypi.org/pypi/medicafe/json", timeout=10)
                print("PyPI: CONNECTED (Status: {})".format(response.status_code))
            except Exception as e:
                print("PyPI: ERROR - {}".format(e))
    else:
        print("Internet: NOT CONNECTED")
        print_final_result(False, "No internet connection available")
    print()
    
    # STEP 5: Check for updates (always check)
    print("STEP 5: Version Check")
    print("-" * 40)
    latest_version = get_latest_version(package)
    if latest_version:
        print("Latest Available: {}".format(latest_version))
        if current_version:
            comparison = compare_versions(latest_version, current_version)
            if comparison > 0:
                print("Status: UPDATE NEEDED")
                print("Current: {} -> Latest: {}".format(current_version, latest_version))
            elif comparison == 0:
                print("Status: UP TO DATE")
                print("Current: {} = Latest: {}".format(current_version, latest_version))
            else:
                print("Status: VERSION MISMATCH")
                print("Current: {} > Latest: {}".format(current_version, latest_version))
        else:
            print("Status: CANNOT COMPARE")
            print("Current version not available")
    else:
        print("Status: ERROR")
        print("Could not retrieve latest version")
        print_final_result(False, "Unable to fetch latest version")
    print()
    
    # STEP 6: Dependencies check (only in debug mode)
    if DEBUG_MODE:
        print("STEP 6: Dependencies Check")
        print("-" * 40)
        response = input("Check dependencies? (y/n, default=n): ").strip().lower()
        if response in ['yes', 'y']:
            ensure_dependencies()
        else:
            print("Skipping dependency check.")
        print()
    
    # STEP 7: Perform update (always show progress)
    print("STEP 7: Update Process")
    print("-" * 40)
    if current_version and latest_version and compare_versions(latest_version, current_version) > 0:
        print("Starting update process...")
        print("From: {} -> To: {}".format(current_version, latest_version))
        print()
        
        if upgrade_package(package):
            # STEP 8: Verify upgrade
            print("STEP 8: Verification")
            print("-" * 40)
            new_version = get_installed_version(package)
            print("New Version: {}".format(new_version))
            
            if compare_versions(new_version, latest_version) >= 0:
                print("Status: SUCCESS")
                
                # STEP 9: Clear cache (always do, minimal output)
                print("STEP 9: Cache Cleanup")
                print("-" * 40)
                print("Clearing Python cache...")
                if clear_python_cache():
                    print("Cache: CLEARED")
                else:
                    print("Cache: WARNING - Some files could not be cleared")
                
                print_final_result(True, "Successfully upgraded to version {}".format(new_version))
            else:
                print("Status: FAILED")
                print("Version verification failed")
                print_final_result(False, "Upgrade verification failed")
        else:
            print("Status: FAILED")
            print("Update process failed")
            print_final_result(False, "Upgrade process failed")
    else:
        print("Status: NO UPDATE NEEDED")
        print("MediCafe is already up to date.")
        print_final_result(True, "Already running latest version")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check-only":
            check_for_updates_only()
            sys.exit(0)
        elif sys.argv[1] == "--clear-cache":
            # Standalone cache clearing mode
            print_status("MediCafe Cache Clearing Utility", "INFO")
            workspace_path = sys.argv[2] if len(sys.argv) > 2 else None
            if clear_python_cache(workspace_path):
                print_status("Cache clearing completed successfully", "SUCCESS")
                sys.exit(0)
            else:
                print_status("Cache clearing failed", "ERROR")
                sys.exit(1)
    else:
        main()
