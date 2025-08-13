#update_medicafe.py
import subprocess, sys, time, platform, os, shutil, random

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

# Safe tqdm import with fallback
try:
    from tqdm import tqdm as _real_tqdm
    def tqdm(iterable, **kwargs):
        return _real_tqdm(iterable, **kwargs)
    TQDM_AVAILABLE = True
except Exception:
    TQDM_AVAILABLE = False
    def tqdm(iterable, **kwargs):
        return iterable

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
        # First try using pkg_resources directly (more reliable for Python 3.4)
        if pkg_resources:
            try:
                version = pkg_resources.get_distribution(package).version
                return version
            except pkg_resources.DistributionNotFound:
                return None
            except Exception as e:
                print("Warning: pkg_resources failed: {}".format(e))
                # Fall through to pip method
        
        # Fallback to pip show (may fail on Python 3.4 due to packaging issues)
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
            
            # Print the version with attempt information
            if attempt == 1:
                print("Latest available version: {}".format(latest_version))
            else:
                print("Latest available version: {} ({} attempt)".format(latest_version, attempt))
            
            # Check if the latest version is different from the current version
            current_version = get_installed_version(package)
            if current_version and compare_versions(latest_version, current_version) == 0:
                # If the versions are the same, perform a second request to ensure we have the latest
                time.sleep(delay)
                response = requests.get("https://pypi.org/pypi/{}/json".format(package), timeout=10)
                response.raise_for_status()
                data = response.json()
                latest_version = data['info']['version']
                print("Double-checked latest version: {}".format(latest_version))
            
            return latest_version  # Return the version after the check
        except requests.RequestException as e:
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
            print_status("Could not detect workspace path. Cache clearing skipped.", "WARNING")
            return False
        
        print("Workspace path: {}".format(workspace_path))
        
        # Directories to clear cache from
        cache_dirs = [
            os.path.join(workspace_path, 'MediCafe'),
            os.path.join(workspace_path, 'MediBot'),
            os.path.join(workspace_path, 'MediLink'),
            workspace_path  # Root workspace
        ]
        
        cleared_count = 0
        # First, remove __pycache__ directories (these are few, so prints are acceptable)
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                pycache_path = os.path.join(cache_dir, '__pycache__')
                if os.path.exists(pycache_path):
                    try:
                        shutil.rmtree(pycache_path)
                        print("Cleared cache: {}".format(pycache_path))
                        cleared_count += 1
                    except Exception as e:
                        print("Warning: Could not clear cache at {}: {}".format(pycache_path, e))

        # Next, collect all .pyc files to provide a clean progress indicator
        pyc_files = []
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                for root, dirs, files in os.walk(cache_dir):
                    for file in files:
                        if file.endswith('.pyc'):
                            pyc_files.append(os.path.join(root, file))

        # Remove .pyc files with a progress bar (tqdm if available, otherwise a single-line counter)
        if pyc_files:
            total_files = len(pyc_files)
            removed_files = 0

            if TQDM_AVAILABLE:
                for file_path in tqdm(pyc_files, desc="Removing .pyc files", unit="file"):
                    try:
                        os.remove(file_path)
                        cleared_count += 1
                        removed_files += 1
                    except Exception as e:
                        print("Warning: Could not remove .pyc file {}: {}".format(os.path.basename(file_path), e))
            else:
                # Minimal, XP-safe single-line progress indicator
                for file_path in pyc_files:
                    try:
                        os.remove(file_path)
                        cleared_count += 1
                        removed_files += 1
                    except Exception as e:
                        print("Warning: Could not remove .pyc file {}: {}".format(os.path.basename(file_path), e))
                    # Update progress on one line
                    try:
                        sys.stdout.write("\rRemoving .pyc files: {}/{}".format(removed_files, total_files))
                        sys.stdout.flush()
                    except Exception:
                        pass
                # Finish the line after completion
                try:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                except Exception:
                    pass
        
        if cleared_count > 0:
            print_status("Successfully cleared {} cache items".format(cleared_count), "SUCCESS")
            return True
        else:
            print_status("No cache files found to clear", "INFO")
            return True
            
    except Exception as e:
        print_status("Error clearing cache: {}".format(e), "ERROR")
        return False

def compare_versions(version1, version2):
    v1_parts = list(map(int, version1.split(".")))
    v2_parts = list(map(int, version2.split(".")))
    return (v1_parts > v2_parts) - (v1_parts < v2_parts)

def upgrade_package(package, retries=4, delay=2, target_version=None):  # Updated retries to 4
    """
    Attempts to upgrade the package multiple times with delays in between.
    """
    if not check_internet_connection():
        print_status("No internet connection detected. Please check your internet connection and try again.", "ERROR")
        print_final_result(False, "No internet connection available")
    
    # Light verbosity: show pinned target once
    if target_version:
        print("Pinned target version: {}".format(target_version))

    for attempt in range(1, retries + 1):
        print("Attempt {}/{} to upgrade {}...".format(attempt, retries, package))
        
        # Use a more compatible approach for Python 3.4
        # Try with --no-deps first to avoid dependency resolution issues
        pkg_spec = package
        if target_version:
            pkg_spec = "{}=={}".format(package, target_version)

        cmd = [
            sys.executable, '-m', 'pip', 'install', '--upgrade',
            '--no-deps', '--no-cache-dir', '--disable-pip-version-check', '-q', pkg_spec
        ]
        
        print("Using pip upgrade with --no-deps and --no-cache-dir")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print(stdout.decode().strip())
            new_version = get_installed_version(package)  # Get new version after upgrade
            expected_version = target_version or get_latest_version(package)
            if expected_version and compare_versions(new_version, expected_version) >= 0:  # Compare versions
                if attempt == 1:
                    print_status("Upgrade succeeded!", "SUCCESS")
                else:
                    print_status("Attempt {}: Upgrade succeeded!".format(attempt), "SUCCESS")
                time.sleep(delay)
                return True
            else:
                print_status("Upgrade incomplete. Current version: {} Expected at least: {}".format(new_version, expected_version), "WARNING")
                if attempt < retries:
                    print("Retrying in {} seconds...".format(delay))
                    try:
                        time.sleep(delay + (random.random() * 0.5))
                    except Exception:
                        time.sleep(delay)
        else:
            print(stderr.decode().strip())
            print_status("Attempt {}: Upgrade failed with --no-deps.".format(attempt), "WARNING")
            
            # If --no-deps failed, try with --force-reinstall to bypass dependency issues
            if attempt < retries:
                print("Fallback this attempt: retrying with --force-reinstall...")
                pkg_spec = package
                if target_version:
                    pkg_spec = "{}=={}".format(package, target_version)

                cmd = [
                    sys.executable, '-m', 'pip', 'install', '--upgrade',
                    '--force-reinstall', '--no-cache-dir', '--disable-pip-version-check', '-q', pkg_spec
                ]
                
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    print(stdout.decode().strip())
                    new_version = get_installed_version(package)
                    expected_version = target_version or get_latest_version(package)
                    if expected_version and compare_versions(new_version, expected_version) >= 0:
                        print_status("Attempt {}: Upgrade succeeded with --force-reinstall!".format(attempt), "SUCCESS")
                        time.sleep(delay)
                        return True
                    else:
                        print_status("Upgrade incomplete. Current version: {} Expected at least: {}".format(new_version, expected_version), "WARNING")
                else:
                    print(stderr.decode().strip())
                    print_status("Attempt {}: Upgrade failed with --force-reinstall.".format(attempt), "WARNING")
                
                if attempt < retries:
                    print("Retrying in {} seconds...".format(delay))
                    try:
                        time.sleep(delay + (random.random() * 0.5))
                    except Exception:
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

    print_status("MediCafe Update Utility", "INFO")
    print("Starting update process...")

    # STEP 1: Environment Information
    debug_step(1, "Environment Information",
              "Python version: {}\n"
              "Platform: {}\n"
              "Current working directory: {}\n"
              "Script location: {}\n"
              "sys.executable: {}".format(
                  sys.version, platform.platform(), os.getcwd(),
                  __file__, sys.executable))

    # STEP 2: Check Python and pip
    debug_step(2, "Python and pip Verification")
    print("Checking Python installation...")
    try:
        process = subprocess.Popen([sys.executable, '--version'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print("Python version: {}".format(stdout.decode().strip()))
        else:
            print("Error checking Python: {}".format(stderr.decode().strip()))
    except Exception as e:
        print("Error checking Python: {}".format(e))

    print("\nChecking pip installation...")
    try:
        process = subprocess.Popen([sys.executable, '-m', 'pip', '--version'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print("pip version: {}".format(stdout.decode().strip()))
        else:
            print("Error checking pip: {}".format(stderr.decode().strip()))
    except Exception as e:
        print("Error checking pip: {}".format(e))

    # STEP 3: Check MediCafe package
    debug_step(3, "MediCafe Package Check")
    package = "medicafe"
    current_version = get_installed_version(package)
    if current_version:
        print("Current MediCafe version: {}".format(current_version))
    else:
        print("MediCafe package not found or not accessible")

    # STEP 4: Internet connectivity
    debug_step(4, "Internet Connectivity Test")
    if check_internet_connection():
        print("Internet connection: OK")
        print("Testing PyPI connectivity...")
        try:
            response = requests.get("https://pypi.org/pypi/medicafe/json", timeout=10)
            print("PyPI connectivity: OK (Status: {})".format(response.status_code))
        except Exception as e:
            print("PyPI connectivity: FAILED - {}".format(e))
    else:
        print("Internet connection: FAILED")
        print_final_result(False, "No internet connection available")

    # STEP 5: Check for updates
    debug_step(5, "Version Comparison")
    latest_version = get_latest_version(package)
    if latest_version:
        print("Latest available version: {}".format(latest_version))
        if current_version:
            comparison = compare_versions(latest_version, current_version)
            if comparison > 0:
                print("Update needed: Current ({}) < Latest ({})".format(current_version, latest_version))
            elif comparison == 0:
                print("Already up to date: Current ({}) = Latest ({})".format(current_version, latest_version))
            else:
                print("Version mismatch: Current ({}) > Latest ({})".format(current_version, latest_version))
        else:
            print("Cannot compare versions - current version not available")
    else:
        print("Could not retrieve latest version information")
        print_final_result(False, "Unable to fetch latest version")

    # STEP 6: Dependencies check (skipped by default in streamlined mode)
    debug_step(6, "Dependencies Check")
    if DEBUG_MODE:
        response = input("Do you want to check dependencies? (yes/no, default/enter is no): ").strip().lower()
        if response in ['yes', 'y']:
            ensure_dependencies()
        else:
            print_status("Skipping dependency check.", "INFO")
    else:
        print_status("Skipping dependency check (streamlined mode).", "INFO")

    # STEP 7: Perform update
    debug_step(7, "Update Execution")
    if current_version and latest_version and compare_versions(latest_version, current_version) > 0:
        print_status("A newer version is available. Proceeding with upgrade.", "INFO")
        print("Current version: {}".format(current_version))
        print("Target version: {}".format(latest_version))

        if upgrade_package(package, target_version=latest_version):
            # STEP 8: Verify upgrade
            debug_step(8, "Upgrade Verification")
            new_version = get_installed_version(package)
            print("New installed version: {}".format(new_version))

            if compare_versions(new_version, latest_version) >= 0:
                print_status("Upgrade successful. New version: {}".format(new_version), "SUCCESS")

                # DEBUG STEP 9: Clear cache
                debug_step(9, "Cache Clearing")
                print_status("Clearing Python cache to prevent import issues...", "INFO")
                if clear_python_cache():
                    print_status("Cache cleared successfully. Update complete.", "SUCCESS")
                else:
                    print_status("Cache clearing failed, but update was successful.", "WARNING")

                print_final_result(True, "Successfully upgraded to version {}".format(new_version))
            else:
                print_status("Upgrade failed. Current version remains: {}".format(new_version), "ERROR")
                print_final_result(False, "Upgrade verification failed")
        else:
            print_final_result(False, "Upgrade process failed")
    else:
        print_status("You already have the latest version installed.", "SUCCESS")
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
