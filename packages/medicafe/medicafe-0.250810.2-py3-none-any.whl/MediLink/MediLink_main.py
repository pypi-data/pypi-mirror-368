# MediLink.py - Orchestrating script for MediLink operations
import os, sys, time

# Add workspace directory to Python path for MediCafe imports
current_dir = os.path.dirname(os.path.abspath(__file__))
workspace_dir = os.path.dirname(current_dir)
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

# Import centralized logging configuration
try:
    from MediCafe.logging_config import PERFORMANCE_LOGGING
except ImportError:
    # Fallback to local flag if centralized config is not available
    PERFORMANCE_LOGGING = False

# Add timing for import phase
start_time = time.time()
if PERFORMANCE_LOGGING:
    print("Starting MediLink initialization...")


# Now import core utilities after path setup
from MediCafe.core_utils import get_shared_config_loader, setup_module_paths
setup_module_paths(__file__)

# Import modules after path setup
import MediLink_Down
import MediLink_Up
import MediLink_DataMgmt
import MediLink_UI  # Import UI module for handling all user interfaces
import MediLink_PatientProcessor  # Import patient processing functions

# Use core utilities for standardized config loader
MediLink_ConfigLoader = get_shared_config_loader()

try:
    from tqdm import tqdm
except ImportError:
    # Fallback for when tqdm is not available
    def tqdm(iterable, **kwargs):
        return iterable

import_time = time.time()
if PERFORMANCE_LOGGING:
    print("Import phase completed in {:.2f} seconds".format(import_time - start_time))

# NOTE: Configuration loading moved to function level to avoid import-time dependencies

# TODO There needs to be a crosswalk auditing feature right alongside where all the names get fetched during initial startup maybe? 
# Vision:
# - Fast audit pass on startup with 3s timeout: report missing names/IDs, do not block.
# - Allow manual remediation flows for Medisoft IDs; only call APIs when beneficial (missing names).
# - XP note: default to console prompts; optional UI later.
# This already happens when MediLink is opened.

def main_menu():
    """
    Initializes the main menu loop and handles the overall program flow,
    including loading configurations and managing user input for menu selections.
    """
    menu_start_time = time.time()
    print("Main menu function started...")
    
    # Load configuration settings and display the initial welcome message.
    config_start_time = time.time()
    if PERFORMANCE_LOGGING:
        print("Loading configuration...")
    config, crosswalk = MediLink_ConfigLoader.load_configuration() 
    config_end_time = time.time()
    if PERFORMANCE_LOGGING:
        print("Configuration loading completed in {:.2f} seconds".format(config_end_time - config_start_time))
    
    # Check to make sure payer_id key is available in crosswalk, otherwise, go through that crosswalk initialization flow
    crosswalk_check_start = time.time()
    if 'payer_id' not in crosswalk:
        print("\n" + "="*60)
        print("SETUP REQUIRED: Payer Information Database Missing")
        print("="*60)
        print("\nThe system needs to build a database of insurance company information")
        print("before it can process claims. This is a one-time setup requirement.")
        print("\nThis typically happens when:")
        print("- You're running MediLink for the first time")
        print("- The payer database was accidentally deleted or corrupted")
        print("- You're using a new installation of the system")
        print("\nTO FIX THIS:")
        print("1. Open a command prompt/terminal")
        print("2. Navigate to the MediCafe directory")
        print("3. Run: python MediBot/MediBot_Preprocessor.py --update-crosswalk")
        print("4. Wait for the process to complete (this may take a few minutes)")
        print("5. Return here and restart MediLink")
        print("\nThis will download and build the insurance company database.")
        print("="*60)
        print("\nPress Enter to exit...")
        input()
        return  # Graceful exit instead of abrupt halt
    
    crosswalk_check_end = time.time()
    if PERFORMANCE_LOGGING:
        print("Crosswalk validation completed in {:.2f} seconds".format(crosswalk_check_end - crosswalk_check_start))
    
    # Check if the application is in test mode
    test_mode_start = time.time()
    if config.get("MediLink_Config", {}).get("TestMode", False):
        print("\n--- MEDILINK TEST MODE --- \nTo enable full functionality, please update the config file \nand set 'TestMode' to 'false'.")
    test_mode_end = time.time()
    if PERFORMANCE_LOGGING:
        print("Test mode check completed in {:.2f} seconds".format(test_mode_end - test_mode_start))
    
    # Display Welcome Message
    welcome_start = time.time()
    MediLink_UI.display_welcome()
    welcome_end = time.time()
    if PERFORMANCE_LOGGING:
        print("Welcome display completed in {:.2f} seconds".format(welcome_end - welcome_start))

    # Normalize the directory path for file operations.
    path_norm_start = time.time()
    directory_path = os.path.normpath(config['MediLink_Config']['inputFilePath'])
    path_norm_end = time.time()
    if PERFORMANCE_LOGGING:
        print("Path normalization completed in {:.2f} seconds".format(path_norm_end - path_norm_start))

    # Detect files and determine if a new file is flagged.
    file_detect_start = time.time()
    if PERFORMANCE_LOGGING:
        print("Starting file detection...")
    all_files, file_flagged = MediLink_DataMgmt.detect_new_files(directory_path)
    file_detect_end = time.time()
    if PERFORMANCE_LOGGING:
        print("File detection completed in {:.2f} seconds".format(file_detect_end - file_detect_start))
        print("Found {} files, flagged: {}".format(len(all_files), file_flagged))
    MediLink_ConfigLoader.log("Found {} files, flagged: {}".format(len(all_files), file_flagged), level="INFO")

    menu_init_end = time.time()
    if PERFORMANCE_LOGGING:
        print("Main menu initialization completed in {:.2f} seconds".format(menu_init_end - menu_start_time))

    while True:
        # Define static menu options for consistent numbering
        options = ["Check for new remittances", "Submit claims", "Exit"]

        # Display the menu options.
        menu_display_start = time.time()
        MediLink_UI.display_menu(options)
        menu_display_end = time.time()
        if PERFORMANCE_LOGGING:
            print("Menu display completed in {:.2f} seconds".format(menu_display_end - menu_display_start))
        
        # Retrieve user choice and handle it.
        choice_start = time.time()
        choice = MediLink_UI.get_user_choice()
        choice_end = time.time()
        if PERFORMANCE_LOGGING:
            print("User choice retrieval completed in {:.2f} seconds".format(choice_end - choice_start))

        if choice == '1':
            # Handle remittance checking.
            remittance_start = time.time()
            MediLink_Down.check_for_new_remittances(config)
            remittance_end = time.time()
            if PERFORMANCE_LOGGING:
                print("Remittance check completed in {:.2f} seconds".format(remittance_end - remittance_start))
        elif choice == '2':
            if not all_files:
                print("No files available to submit. Please check for new remittances first.")
                continue
            # Handle the claims submission flow if any files are present.
            submission_start = time.time()
            if file_flagged:
                # Extract the newest single latest file from the list if a new file is flagged.
                selected_files = [max(all_files, key=os.path.getctime)]
            else:
                # Prompt the user to select files if no new file is flagged.
                selected_files = MediLink_UI.user_select_files(all_files)

            # Collect detailed patient data for selected files.
            patient_data_start = time.time()
            detailed_patient_data = MediLink_PatientProcessor.collect_detailed_patient_data(selected_files, config, crosswalk)
            patient_data_end = time.time()
            if PERFORMANCE_LOGGING:
                print("Patient data collection completed in {:.2f} seconds".format(patient_data_end - patient_data_start))
            
            # Process the claims submission.
            handle_submission(detailed_patient_data, config, crosswalk)
            submission_end = time.time()
            if PERFORMANCE_LOGGING:
                print("Claims submission flow completed in {:.2f} seconds".format(submission_end - submission_start))
        elif choice == '3':
            MediLink_UI.display_exit_message()
            break
        else:
            # Display an error message if the user's choice does not match any valid option.
            MediLink_UI.display_invalid_choice()

def handle_submission(detailed_patient_data, config, crosswalk):
    """
    Handles the submission process for claims based on detailed patient data.
    This function orchestrates the flow from user decision on endpoint suggestions to the actual submission of claims.
    """
    insurance_edited = False  # Flag to track if insurance types were edited

    # Ask the user if they want to edit insurance types
    edit_insurance = input("Do you want to edit insurance types? (y/n): ").strip().lower()
    if edit_insurance in ['y', 'yes', '']:
        insurance_edited = True  # User chose to edit insurance types
        
        # Get insurance options from config
        insurance_options = config['MediLink_Config'].get('insurance_options', {})
        
        while True:
            # Bulk edit insurance types
            MediLink_DataMgmt.bulk_edit_insurance_types(detailed_patient_data, insurance_options)
    
            # Review and confirm changes
            if MediLink_DataMgmt.review_and_confirm_changes(detailed_patient_data, insurance_options):
                break  # Exit the loop if changes are confirmed
            else:
                print("Returning to bulk edit insurance types.")
    
    # Initiate user interaction to confirm or adjust suggested endpoints.
    adjusted_data, updated_crosswalk = MediLink_UI.user_decision_on_suggestions(detailed_patient_data, config, insurance_edited, crosswalk)
    
    # Update crosswalk reference if it was modified
    if updated_crosswalk:
        crosswalk = updated_crosswalk
    
    # Confirm all remaining suggested endpoints.
    confirmed_data = MediLink_DataMgmt.confirm_all_suggested_endpoints(adjusted_data)
    if confirmed_data:  # Proceed if there are confirmed data entries.
        # Organize data by confirmed endpoints for submission.
        organized_data = MediLink_DataMgmt.organize_patient_data_by_endpoint(confirmed_data)
        # Confirm transmission with the user and check for internet connectivity.
        if MediLink_Up.confirm_transmission(organized_data):
            if MediLink_Up.check_internet_connection():
                # Submit claims if internet connectivity is confirmed.
                _ = MediLink_Up.submit_claims(organized_data, config, crosswalk)
                # TODO submit_claims will have a receipt return in the future.
                # PLAN: submit_claims should return a structure like:
                #   {'endpoint': ep, 'files': [{'path': p, 'status': 'ok'|'error', 'receipt_id': '...', 'timestamp': ...}], 'errors': [...]} 
                # Callers can log and optionally display the receipt IDs or open an acknowledgment view.
                # Backward-compatibility: if None/empty is returned, proceed as today.
            else:
                # Notify the user of an internet connection error.
                print("Internet connection error. Please ensure you're connected and try again.")
        else:
            # Notify the user if the submission is cancelled.
            print("Submission cancelled. No changes were made.")

if __name__ == "__main__":
    total_start_time = time.time()
    exit_code = 0
    try:
        main_menu()
    except ValueError as e:
        # Graceful domain error: show concise message without traceback, then exit
        sys.stderr.write("\n" + "="*60 + "\n")
        sys.stderr.write("PROCESS HALTED\n")
        sys.stderr.write("="*60 + "\n")
        sys.stderr.write(str(e) + "\n")
        sys.stderr.write("\nPress Enter to exit...\n")
        try:
            input()
        except Exception:
            pass
        exit_code = 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        exit_code = 1
    except Exception as e:
        # Unexpected error: still avoid full traceback, present succinct notice
        sys.stderr.write("An unexpected error occurred; process halted.\n")
        sys.stderr.write(str(e) + "\n")
        sys.stderr.write("\nPress Enter to exit...\n")
        try:
            input()
        except Exception:
            pass
        exit_code = 1
    finally:
        if exit_code == 0 and PERFORMANCE_LOGGING:
            total_end_time = time.time()
            print("Total MediLink execution time: {:.2f} seconds".format(total_end_time - total_start_time))
    sys.exit(exit_code)