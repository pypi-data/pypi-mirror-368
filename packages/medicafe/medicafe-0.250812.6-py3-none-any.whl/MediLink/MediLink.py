# MediLink.py
import os, sys, time
import MediLink_Down
import MediLink_Up
import MediLink_ConfigLoader
import MediLink_DataMgmt

# For UI Functions
import MediLink_UI  # Import UI module for handling all user interfaces
try:
    from tqdm import tqdm
except ImportError:
    # Fallback for when tqdm is not available
    def tqdm(iterable, **kwargs):
        return iterable

# Add parent directory of the project to the Python path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from MediBot import MediBot_Preprocessor_lib
load_insurance_data_from_mains = MediBot_Preprocessor_lib.load_insurance_data_from_mains

# Retrieve insurance options with codes and descriptions
config, _ = MediLink_ConfigLoader.load_configuration()
insurance_options = config['MediLink_Config'].get('insurance_options')

# TODO There needs to be a crosswalk auditing feature right alongside where all the names get fetched during initial startup maybe? 
# This already happens when MediLink is opened.

def collect_detailed_patient_data(selected_files, config, crosswalk):
    """
    Collects detailed patient data from the selected files.
    
    DATA FLOW CLARIFICATION:
    This function processes fixed-width files through extract_and_suggest_endpoint(),
    which creates data structures with 'patient_id' field (sourced from 'CHART' field).
    This is DIFFERENT from MediBot's parse_z_dat() flow which uses 'PATID' field.
    
    :param selected_files: List of selected file paths.
    :param config: Configuration settings loaded from a JSON file.
    :param crosswalk: Crosswalk data for mapping purposes.
    :return: A list of detailed patient data with 'patient_id' field populated.
    """
    detailed_patient_data = []
    for file_path in selected_files:
        # IMPORTANT: extract_and_suggest_endpoint creates data with 'patient_id' field
        # sourced from the 'CHART' field in fixed-width files
        detailed_data = extract_and_suggest_endpoint(file_path, config, crosswalk)
        detailed_patient_data.extend(detailed_data)  # Accumulate detailed data for processing
        
    # Enrich the detailed patient data with insurance type
    # NOTE: This receives data from extract_and_suggest_endpoint with 'patient_id' field
    detailed_patient_data = enrich_with_insurance_type(detailed_patient_data, insurance_options)
    
    # Display summaries and provide an option for bulk edit
    MediLink_UI.display_patient_summaries(detailed_patient_data)

    return detailed_patient_data

def enrich_with_insurance_type(detailed_patient_data, patient_insurance_type_mapping=None):
    """
    Enriches the detailed patient data with insurance type based on patient ID.
    Enhanced with optional API integration and comprehensive logging.

    DATA FLOW CLARIFICATION:
    This function receives data from collect_detailed_patient_data() -> extract_and_suggest_endpoint().
    The patient ID field is 'patient_id' (NOT 'PATID').
    
    IMPORTANT: Do not confuse with MediBot's parse_z_dat() flow which uses 'PATID'.
    MediLink flow: fixed-width files -> extract_and_suggest_endpoint() -> 'patient_id' field (from 'CHART')
    MediBot flow: Z.dat files -> parse_z_dat() -> 'PATID' field

    Parameters:
    - detailed_patient_data: List of dictionaries containing detailed patient data with 'patient_id' field.
    - patient_insurance_mapping: Dictionary mapping patient IDs to their insurance types.

    Returns:
    - Enriched detailed patient data with insurance type added.
    
    TODO: Implement a function to provide `patient_insurance_mapping` from a reliable source.
    This is going to be coming soon as an API feature from United Healthcare. We'll be able to get insurance types directly via their API.
    So, while we won't be able to do it for all payerIDs, we'll be able to do it for the ones that are supported by UHC.
    So, we'll need a way to augment the associated menu here so that the user is aware of which insurance types are already pulled from
    UHC and which ones are not yet supported so they know which ones they need to edit. It is possible that we may want to isolate the 
    patient data that is already pulled from UHC so that the user can see which ones are already using the enriched data.
    """
    # Enhanced mode check with graceful degradation
    enhanced_mode = False
    
    try:
        from MediLink_insurance_utils import (
            get_feature_flag, 
            validate_insurance_type_from_config
        )
        enhanced_mode = get_feature_flag('enhanced_insurance_enrichment', default=False)
        MediLink_ConfigLoader.log("Insurance enhancement utilities loaded successfully", level="DEBUG")
    except ImportError as e:
        MediLink_ConfigLoader.log("Insurance utils not available: {}. Using legacy mode.".format(str(e)), level="INFO")
        enhanced_mode = False
    except Exception as e:
        MediLink_ConfigLoader.log("Error initializing insurance enhancements: {}. Using legacy mode.".format(str(e)), level="ERROR")
        enhanced_mode = False
    
    if patient_insurance_type_mapping is None:
        MediLink_ConfigLoader.log("No Patient:Insurance-Type mapping available.", level="INFO")
        patient_insurance_type_mapping = {}
    
    # Enhanced mode with validation
    if enhanced_mode:
        MediLink_ConfigLoader.log("Using enhanced insurance type enrichment", level="INFO")
        
        for data in detailed_patient_data:
            # FIELD NAME CLARIFICATION: Use 'patient_id' field created by extract_and_suggest_endpoint()
            # This field contains the value from the 'CHART' field in the original fixed-width file
            patient_id = data.get('patient_id')
            if patient_id:
                raw_insurance_type = patient_insurance_type_mapping.get(patient_id, '12')  # Default to '12' (PPO/SBR09)
                validated_insurance_type = validate_insurance_type_from_config(raw_insurance_type, patient_id)
                data['insurance_type'] = validated_insurance_type
                data['insurance_type_source'] = 'MANUAL' if patient_id in patient_insurance_type_mapping else 'DEFAULT'
            else:
                # Handle case where patient_id is missing or empty
                MediLink_ConfigLoader.log("No patient_id found in data record", level="WARNING")
                data['insurance_type'] = '12'  # SBR09 default PPO
                data['insurance_type_source'] = 'DEFAULT_FALLBACK'
        
    else:
        # Legacy mode (preserve existing behavior exactly)
        MediLink_ConfigLoader.log("Using legacy insurance type enrichment", level="INFO")
        for data in detailed_patient_data:
            # FIELD NAME CLARIFICATION: Use 'patient_id' field created by extract_and_suggest_endpoint()
            # This field contains the value from the 'CHART' field in the original fixed-width file
            patient_id = data.get('patient_id')
            if patient_id:
                insurance_type = patient_insurance_type_mapping.get(patient_id, '12')  # Default to '12' (PPO/SBR09)
            else:
                # Handle case where patient_id is missing or empty
                MediLink_ConfigLoader.log("No patient_id found in data record", level="WARNING")
                insurance_type = '12'  # Default when no patient ID available
            
            data['insurance_type'] = insurance_type
    
    return detailed_patient_data

def extract_and_suggest_endpoint(file_path, config, crosswalk):
    """
    Reads a fixed-width file, extracts file details including surgery date, patient ID, 
    patient name, primary insurance, and other necessary details for each record. It suggests 
    an endpoint based on insurance provider information found in the crosswalk and prepares 
    detailed patient data for processing.
    
    DATA FLOW CLARIFICATION:
    This function is the PRIMARY data source for MediLink patient processing.
    It creates the 'patient_id' field by extracting the 'CHART' field from fixed-width files.
    
    IMPORTANT: This is DIFFERENT from MediBot's parse_z_dat() which extracts 'PATID'.
    
    Field mapping for MediLink flow:
    - Fixed-width file 'CHART' field -> detailed_data['patient_id']
    - This 'patient_id' is then used by enrich_with_insurance_type()
    
    Parameters:
    - file_path: Path to the fixed-width file.
    - crosswalk: Crosswalk dictionary loaded from a JSON file.

    Returns:
    - A comprehensive data structure retaining detailed patient claim details needed for processing,
      including new key-value pairs for file path, surgery date, patient name, and primary insurance.
    """
    detailed_patient_data = []
    
    # Load insurance data from MAINS to create a mapping from insurance names to their respective IDs
    insurance_to_id = load_insurance_data_from_mains(config)
    MediLink_ConfigLoader.log("Insurance data loaded from MAINS. {} insurance providers found.".format(len(insurance_to_id)), level="INFO")

    for personal_info, insurance_info, service_info, service_info_2, service_info_3 in MediLink_DataMgmt.read_fixed_width_data(file_path):
        parsed_data = MediLink_DataMgmt.parse_fixed_width_data(personal_info, insurance_info, service_info, service_info_2, service_info_3, config.get('MediLink_Config', config))
        
        primary_insurance = parsed_data.get('INAME')
               
        # Retrieve the insurance ID associated with the primary insurance
        insurance_id = insurance_to_id.get(primary_insurance)
        MediLink_ConfigLoader.log("Primary insurance ID retrieved for '{}': {}".format(primary_insurance, insurance_id))

        # Use insurance ID to retrieve the payer ID(s) associated with the insurance
        payer_ids = []
        if insurance_id:
            for payer_id, payer_data in crosswalk.get('payer_id', {}).items():
                medisoft_ids = [str(id) for id in payer_data.get('medisoft_id', [])]
                # MediLink_ConfigLoader.log("Payer ID: {}, Medisoft IDs: {}".format(payer_id, medisoft_ids))
                if str(insurance_id) in medisoft_ids:
                    payer_ids.append(payer_id)
        if payer_ids:
            MediLink_ConfigLoader.log("Payer IDs retrieved for insurance '{}': {}".format(primary_insurance, payer_ids))
        else:
            MediLink_ConfigLoader.log("No payer IDs found for insurance '{}'".format(primary_insurance))
        
        # Find the suggested endpoint from the crosswalk based on the payer IDs
        suggested_endpoint = 'AVAILITY'  # Default endpoint if no matching payer IDs found
        if payer_ids:
            payer_id = payer_ids[0]  # Select the first payer ID
            suggested_endpoint = crosswalk['payer_id'].get(payer_id, {}).get('endpoint', 'AVAILITY')
            MediLink_ConfigLoader.log("Suggested endpoint for payer ID '{}': {}".format(payer_id, suggested_endpoint))
            
            # Validate suggested endpoint against the config
            if suggested_endpoint not in config['MediLink_Config'].get('endpoints', {}):
                MediLink_ConfigLoader.log("Warning: Suggested endpoint '{}' is not defined in the configuration. Please Run MediBot. If this persists, check the crosswalk and config file.".format(suggested_endpoint), level="ERROR")
                raise ValueError("Invalid suggested endpoint: '{}' for payer ID '{}'. Please correct the configuration.".format(suggested_endpoint, payer_id))
        else:
            MediLink_ConfigLoader.log("No suggested endpoint found for payer IDs: {}".format(payer_ids))

        # Enrich detailed patient data with additional information and suggested endpoint
        detailed_data = parsed_data.copy()  # Copy parsed_data to avoid modifying the original dictionary
        detailed_data.update({
            'file_path': file_path,
            # CRITICAL FIELD MAPPING: 'CHART' field from fixed-width file becomes 'patient_id'
            # This is the field that enrich_with_insurance_type() will use
            'patient_id': parsed_data.get('CHART'),  # ← This is the key field mapping for MediLink flow
            'surgery_date': parsed_data.get('DATE'),
            'patient_name': ' '.join([parsed_data.get(key, '') for key in ['FIRST', 'MIDDLE', 'LAST']]),
            'amount': parsed_data.get('AMOUNT'),
            'primary_insurance': primary_insurance,
            'suggested_endpoint': suggested_endpoint
        })
        detailed_patient_data.append(detailed_data)

    # Return only the enriched detailed patient data, eliminating the need for a separate summary list
    return detailed_patient_data

def check_for_new_remittances(config=None):
    """
    Function to check for new remittance files across all configured endpoints.
    Loads the configuration, validates it, and processes each endpoint to download and handle files.
    Accumulates results from all endpoints and processes them together at the end.
    """
    # Start the process and log the initiation
    MediLink_ConfigLoader.log("Starting check_for_new_remittances function")
    print("\nChecking for new files across all endpoints...")
    MediLink_ConfigLoader.log("Checking for new files across all endpoints...")

    # Step 1: Load and validate the configuration
    if config is None:
        config, _ = MediLink_ConfigLoader.load_configuration()

    if not config or 'MediLink_Config' not in config or 'endpoints' not in config['MediLink_Config']:
        MediLink_ConfigLoader.log("Error: Config is missing necessary sections. Aborting...", level="ERROR")
        return

    endpoints = config['MediLink_Config'].get('endpoints')
    if not isinstance(endpoints, dict):
        MediLink_ConfigLoader.log("Error: 'endpoints' is not a dictionary. Aborting...", level="ERROR")
        return

    # Lists to accumulate all consolidated records and translated files across all endpoints
    all_consolidated_records = []
    all_translated_files = []

    # Step 2: Process each endpoint and accumulate results
    for endpoint_key, endpoint_info in tqdm(endpoints.items(), desc="Processing endpoints"):
        # Validate endpoint structure
        if not endpoint_info or not isinstance(endpoint_info, dict):
            MediLink_ConfigLoader.log("Error: Invalid endpoint structure for {}. Skipping...".format(endpoint_key), level="ERROR")
            continue

        if 'remote_directory_down' in endpoint_info:
            # Process the endpoint and handle the files
            MediLink_ConfigLoader.log("Processing endpoint: {}".format(endpoint_key))
            consolidated_records, translated_files = process_endpoint(endpoint_key, endpoint_info, config)
            
            # Accumulate the results for later processing
            if consolidated_records:
                all_consolidated_records.extend(consolidated_records)
            if translated_files:
                all_translated_files.extend(translated_files)
        else:
            MediLink_ConfigLoader.log("Skipping endpoint '{}'. 'remote_directory_down' not configured.".format(endpoint_info.get('name', 'Unknown')), level="WARNING")

    # Step 3: After processing all endpoints, handle the accumulated results
    if all_consolidated_records:
        MediLink_Down.display_consolidated_records(all_consolidated_records)  # Ensure this is called only once
        MediLink_Down.prompt_csv_export(all_consolidated_records, config['MediLink_Config']['local_storage_path'])
    else:
        MediLink_ConfigLoader.log("No records to display after processing all endpoints.", level="WARNING")
        print("No records to display after processing all endpoints.")

def process_endpoint(endpoint_key, endpoint_info, config):
    """
    Helper function to process a single endpoint.
    Downloads files from the endpoint, processes them, and returns the consolidated records and translated files.
    """
    try:
        # Process the files for the given endpoint
        local_storage_path = config['MediLink_Config']['local_storage_path']
        MediLink_ConfigLoader.log("[Process Endpoint] Local storage path set to {}".format(local_storage_path))
        downloaded_files = MediLink_Down.operate_winscp("download", None, endpoint_info, local_storage_path, config)
        
        if downloaded_files:
            MediLink_ConfigLoader.log("[Process Endpoint] WinSCP Downloaded the following files: \n{}".format(downloaded_files))
            return MediLink_Down.handle_files(local_storage_path, downloaded_files)
        else:
            MediLink_ConfigLoader.log("[Process Endpoint]No files were downloaded for endpoint: {}.".format(endpoint_key), level="WARNING")
            return [], []

    except Exception as e:
        # Handle any exceptions that occur during the processing
        MediLink_ConfigLoader.log("Error processing endpoint {}: {}".format(endpoint_key, e), level="ERROR")
        return [], []

def user_decision_on_suggestions(detailed_patient_data, config, insurance_edited, crosswalk):
    """
    Presents the user with all patient summaries and suggested endpoints,
    then asks for confirmation to proceed with all or specify adjustments manually.
    
    FIXED: Display now properly shows effective endpoints (user preferences over original suggestions)
    """
    if insurance_edited:
        # Display summaries only if insurance types were edited
        MediLink_UI.display_patient_summaries(detailed_patient_data)

    while True:
        proceed_input = input("Do you want to proceed with all suggested endpoints? (Y/N): ").strip().lower()
        if proceed_input in ['y', 'yes']:
            proceed = True
            break
        elif proceed_input in ['n', 'no']:
            proceed = False
            break
        else:
            print("Invalid input. Please enter 'Y' for yes or 'N' for no.")

    # If the user agrees to proceed with all suggested endpoints, confirm them.
    if proceed:
        return MediLink_DataMgmt.confirm_all_suggested_endpoints(detailed_patient_data), crosswalk
    # Otherwise, allow the user to adjust the endpoints manually.
    else:
        return select_and_adjust_files(detailed_patient_data, config, crosswalk)
   
def select_and_adjust_files(detailed_patient_data, config, crosswalk):
    """
    Allows users to select patients and adjust their endpoints by interfacing with UI functions.
    
    FIXED: Now properly updates suggested_endpoint and persists user preferences to crosswalk.
    """
    # Display options for patients
    MediLink_UI.display_patient_options(detailed_patient_data)

    # Get user-selected indices for adjustment
    selected_indices = MediLink_UI.get_selected_indices(len(detailed_patient_data))
    
    # Get an ordered list of endpoint keys
    endpoint_keys = list(config['MediLink_Config']['endpoints'].keys())
    
    # Iterate over each selected index and process endpoint changes
    for i in selected_indices:
        data = detailed_patient_data[i]
        current_effective_endpoint = get_effective_endpoint(data)
        MediLink_UI.display_patient_for_adjustment(data['patient_name'], current_effective_endpoint)
        
        endpoint_change = MediLink_UI.get_endpoint_decision()
        if endpoint_change == 'y':
            MediLink_UI.display_endpoint_options(config['MediLink_Config']['endpoints'])
            endpoint_index = int(MediLink_UI.get_new_endpoint_choice()) - 1  # Adjusting for zero-based index
            
            if 0 <= endpoint_index < len(endpoint_keys):
                selected_endpoint_key = endpoint_keys[endpoint_index]
                print("Endpoint changed to {0} for patient {1}.".format(config['MediLink_Config']['endpoints'][selected_endpoint_key]['name'], data['patient_name']))
                
                # Use the new endpoint management system
                updated_crosswalk = update_suggested_endpoint_with_user_preference(
                    detailed_patient_data, i, selected_endpoint_key, config, crosswalk
                )
                if updated_crosswalk:
                    crosswalk = updated_crosswalk
            else:
                print("Invalid selection. Keeping the current endpoint.")
                data['confirmed_endpoint'] = current_effective_endpoint
        else:
            data['confirmed_endpoint'] = current_effective_endpoint

    return detailed_patient_data, crosswalk

def update_suggested_endpoint_with_user_preference(detailed_patient_data, patient_index, new_endpoint, config, crosswalk):
    """
    Updates the suggested endpoint for a patient and optionally updates the crosswalk 
    for future patients with the same insurance.
    
    :param detailed_patient_data: List of patient data dictionaries
    :param patient_index: Index of the patient being updated
    :param new_endpoint: The new endpoint selected by the user
    :param config: Configuration settings
    :param crosswalk: Crosswalk data for in-memory updates
    :return: Updated crosswalk if changes were made, None otherwise
    """
    data = detailed_patient_data[patient_index]
    original_suggested = data.get('suggested_endpoint')
    
    # Update the patient's endpoint preference
    data['user_preferred_endpoint'] = new_endpoint
    data['confirmed_endpoint'] = new_endpoint
    
    # If user changed from the original suggestion, offer to update crosswalk
    if original_suggested != new_endpoint:
        primary_insurance = data.get('primary_insurance')
        patient_name = data.get('patient_name')
        
        print("\nYou changed the endpoint for {} from {} to {}.".format(patient_name, original_suggested, new_endpoint))
        update_future = input("Would you like to use {} as the default endpoint for future patients with {}? (Y/N): ".format(new_endpoint, primary_insurance)).strip().lower()
        
        if update_future in ['y', 'yes']:
            # Find the payer ID associated with this insurance
            insurance_to_id = load_insurance_data_from_mains(config)
            insurance_id = insurance_to_id.get(primary_insurance)
            
            if insurance_id:
                # Find the payer ID in crosswalk and update it
                updated = False
                for payer_id, payer_data in crosswalk.get('payer_id', {}).items():
                    medisoft_ids = [str(id) for id in payer_data.get('medisoft_id', [])]
                    if str(insurance_id) in medisoft_ids:
                        # Update the crosswalk in memory
                        crosswalk['payer_id'][payer_id]['endpoint'] = new_endpoint
                        MediLink_ConfigLoader.log("Updated crosswalk in memory: Payer ID {} ({}) now defaults to {}".format(payer_id, primary_insurance, new_endpoint), level="INFO")
                        
                        # Update suggested_endpoint for other patients with same insurance in current batch
                        for other_data in detailed_patient_data:
                            if (other_data.get('primary_insurance') == primary_insurance and 
                                'user_preferred_endpoint' not in other_data):
                                other_data['suggested_endpoint'] = new_endpoint
                        
                        updated = True
                        break
                
                if updated:
                    # Save the updated crosswalk to disk immediately using API bypass mode
                    if save_crosswalk_immediately(config, crosswalk):
                        print("Updated default endpoint for {} to {}".format(primary_insurance, new_endpoint))
                    else:
                        print("Updated endpoint preference (will be saved during next crosswalk update)")
                    return crosswalk
                else:
                    MediLink_ConfigLoader.log("Could not find payer ID in crosswalk for insurance {}".format(primary_insurance), level="WARNING")
            else:
                MediLink_ConfigLoader.log("Could not find insurance ID for {} to update crosswalk".format(primary_insurance), level="WARNING")
    
    return None

def save_crosswalk_immediately(config, crosswalk):
    """
    Saves the crosswalk to disk immediately using API bypass mode.
    
    :param config: Configuration settings
    :param crosswalk: Crosswalk data to save
    :return: True if saved successfully, False otherwise
    """
    try:
        # Import the crosswalk library
        from MediBot import MediBot_Crosswalk_Library
        
        # Save using API bypass mode (no client needed, skip API operations)
        success = MediBot_Crosswalk_Library.save_crosswalk(None, config, crosswalk, skip_api_operations=True)
        
        if success:
            MediLink_ConfigLoader.log("Successfully saved crosswalk with updated endpoint preferences", level="INFO")
        else:
            MediLink_ConfigLoader.log("Failed to save crosswalk - preferences will be saved during next crosswalk update", level="WARNING")
            
        return success
        
    except ImportError:
        MediLink_ConfigLoader.log("Could not import MediBot_Crosswalk_Library for saving crosswalk", level="ERROR")
        return False
    except Exception as e:
        MediLink_ConfigLoader.log("Error saving crosswalk: {}".format(e), level="ERROR")
        return False

def get_effective_endpoint(patient_data):
    """
    Returns the most appropriate endpoint for a patient based on the hierarchy:
    1. Confirmed endpoint (final decision)
    2. User preferred endpoint (if user made a change)
    3. Original suggested endpoint
    4. Default (AVAILITY)
    
    :param patient_data: Individual patient data dictionary
    :return: The effective endpoint to use for this patient
    """
    return (patient_data.get('confirmed_endpoint') or 
            patient_data.get('user_preferred_endpoint') or 
            patient_data.get('suggested_endpoint', 'AVAILITY'))



def main_menu():
    """
    Initializes the main menu loop and handles the overall program flow,
    including loading configurations and managing user input for menu selections.
    """
    # Load configuration settings and display the initial welcome message.
    config, crosswalk = MediLink_ConfigLoader.load_configuration() 
    
    # Check to make sure payer_id key is available in crosswalk, otherwise, go through that crosswalk initialization flow
    if 'payer_id' not in crosswalk:
        print("\n" + "="*60)
        print("SETUP REQUIRED: Payer Information Database Missing")
        print("="*60)
        print("\nThe system needs to build a database of insurance company information")
        print("before it can process claims. This is a one-time setup requirement.")
        print("\nThis typically happens when:")
        print("• You're running MediLink for the first time")
        print("• The payer database was accidentally deleted or corrupted")
        print("• You're using a new installation of the system")
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
    
    # Check if the application is in test mode
    if config.get("MediLink_Config", {}).get("TestMode", False):
        print("\n--- MEDILINK TEST MODE --- \nTo enable full functionality, please update the config file \nand set 'TestMode' to 'false'.")
    
    # Display Welcome Message
    MediLink_UI.display_welcome()

    # Normalize the directory path for file operations.
    directory_path = os.path.normpath(config['MediLink_Config']['inputFilePath'])

    # Detect files and determine if a new file is flagged.
    all_files, file_flagged = MediLink_DataMgmt.detect_new_files(directory_path)

    while True:
        # Define the menu options. Base options include checking remittances and exiting the program.
        options = ["Check for new remittances", "Exit"]
        # If any files are detected, add the option to submit claims.
        if all_files:
            options.insert(1, "Submit claims")

        # Display the dynamically adjusted menu options.
        MediLink_UI.display_menu(options)
        # Retrieve user choice and handle it.
        choice = MediLink_UI.get_user_choice()

        if choice == '1':
            # Handle remittance checking.
            check_for_new_remittances(config)
        elif choice == '2' and all_files:
            # Handle the claims submission flow if any files are present.
            if file_flagged:
                # Extract the newest single latest file from the list if a new file is flagged.
                selected_files = [max(all_files, key=os.path.getctime)]
            else:
                # Prompt the user to select files if no new file is flagged.
                selected_files = MediLink_UI.user_select_files(all_files)

            # Collect detailed patient data for selected files.
            detailed_patient_data = collect_detailed_patient_data(selected_files, config, crosswalk)
            
            # Process the claims submission.
            handle_submission(detailed_patient_data, config, crosswalk)
        elif choice == '3' or (choice == '2' and not all_files):
            # Exit the program if the user chooses to exit or if no files are present.
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
        while True:
            # Bulk edit insurance types
            MediLink_DataMgmt.bulk_edit_insurance_types(detailed_patient_data, insurance_options)
    
            # Review and confirm changes
            if MediLink_DataMgmt.review_and_confirm_changes(detailed_patient_data, insurance_options):
                break  # Exit the loop if changes are confirmed
            else:
                print("Returning to bulk edit insurance types.")
    
    # Initiate user interaction to confirm or adjust suggested endpoints.
    adjusted_data, updated_crosswalk = user_decision_on_suggestions(detailed_patient_data, config, insurance_edited, crosswalk)
    
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
            else:
                # Notify the user of an internet connection error.
                print("Internet connection error. Please ensure you're connected and try again.")
        else:
            # Notify the user if the submission is cancelled.
            print("Submission cancelled. No changes were made.")

if __name__ == "__main__":
    main_menu()