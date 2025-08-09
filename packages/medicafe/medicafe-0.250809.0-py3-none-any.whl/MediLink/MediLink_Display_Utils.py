# MediLink_Display_Utils.py
# Display utility functions extracted from MediLink_UI.py to eliminate circular dependencies
# Provides centralized display functions for insurance options and patient summaries

from datetime import datetime

# Use core utilities for standardized imports
from MediCafe.core_utils import get_shared_config_loader
MediLink_ConfigLoader = get_shared_config_loader()

def display_insurance_options(insurance_options=None):
    """Display insurance options, loading from config if not provided"""
    
    if insurance_options is None:
        config, _ = MediLink_ConfigLoader.load_configuration()
        insurance_options = config.get('MediLink_Config', {}).get('insurance_options', {})
    
    print("\nInsurance Type Options (SBR09 Codes):")
    print("-" * 50)
    for code, description in sorted(insurance_options.items()):
        print("{:>3}: {}".format(code, description))
    print("-" * 50)
    print("Note: '12' (PPO) is the default if no selection is made.")
    print()  # Add a blank line for better readability

def display_patient_summaries(detailed_patient_data):
    """
    Displays summaries of all patients and their suggested endpoints.
    """
    print("\nSummary of patient details and suggested endpoint:")
    for index, summary in enumerate(detailed_patient_data, start=1):
        try:
            display_file_summary(index, summary)
        except KeyError as e:
            print("Summary at index {} is missing key: {}".format(index, e))
    print() # add blank line for improved readability.

def display_file_summary(index, summary):
    # Ensure surgery_date is converted to a datetime object
    surgery_date = datetime.strptime(summary['surgery_date'], "%m-%d-%y")
    
    # Add header row if it's the first index
    if index == 1:
        print("{:<3} {:5} {:<10} {:20} {:15} {:3} {:20}".format(
            "No.", "Date", "ID", "Name", "Primary Ins.", "IT", "Current Endpoint"
        ))
        print("-"*82)

    # Check if insurance_type is available; if not, set a default placeholder (this should already be '12' at this point)
    insurance_type = summary.get('insurance_type', '--')
    
    # Get the effective endpoint (confirmed > user preference > suggestion > default)
    effective_endpoint = (summary.get('confirmed_endpoint') or 
                         summary.get('user_preferred_endpoint') or 
                         summary.get('suggested_endpoint', 'AVAILITY'))

    # Format insurance type for display - handle both 2 and 3 character codes
    if insurance_type and len(insurance_type) <= 3:
        insurance_display = insurance_type
    else:
        insurance_display = insurance_type[:3] if insurance_type else '--'

    # Displays the summary of a file.
    print("{:02d}. {:5} ({:<8}) {:20} {:15} {:3} {:20}".format(
        index,
        surgery_date.strftime("%m-%d"),
        summary['patient_id'],
        summary['patient_name'][:20],
        summary['primary_insurance'][:15],
        insurance_display,
        effective_endpoint[:20])
    ) 