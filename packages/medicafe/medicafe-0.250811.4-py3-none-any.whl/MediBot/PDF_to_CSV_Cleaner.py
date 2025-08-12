import pandas as pd
import re

def load_csv(file_path):
    # Loads a CSV file and returns a pandas DataFrame
    return pd.read_csv(file_path, header=None)

def segment_data(data):
    # Segments the data into individual patient records
    
    patient_records = []
    current_record = []
    
    for line in data.itertuples(index=False):
        # Convert the tuple to a list to process it easier
        line = list(line)
        # Flatten the list and filter out NaN values
        line = [item for item in line if pd.notna(item)]
        
        if line:  # Make sure there is data in the line
            # Check for the delimiter indicating a new patient record
            if 'PATIENT INFORMATION' in line[0]:
                if current_record:
                    # If there's an existing record, this means we've reached a new one
                    # Save the current record and start a new one
                    patient_records.append(current_record)
                    current_record = []
            # Add the line to the current patient record
            current_record.extend(line)
    
    # Don't forget to add the last record after exiting the loop
    if current_record:
        patient_records.append(current_record)
    
    return patient_records

# Function to extract key-value pairs from a patient record segment
def extract_patient_data(patient_record):
    patient_data = {
        "Name": None,
        "Patient ID": None,
        "Address": None,
        "Home Phone": None,
        "DOB": None,
        "Gender": None
    }
    
    # Function to extract value after a specific key in the patient record
    def extract_value_after_key(lines, key):
        for index, line in enumerate(lines):
            if key in line:
                try:
                    split_line = line.split('\n')
                    if len(split_line) > 1:
                        # Return the value only if it exists after the newline character
                        return split_line[1].strip()                
                except AttributeError:
                    # Handle the case where 'line' is not a string and doesn't have the 'split' method
                    print("Error extracting value after key:", line)
                    pass     
    
    # For each key in patient_data, extract its value from the patient_record
    for key in patient_data.keys():
        patient_data[key] = extract_value_after_key(patient_record, key)
    return patient_data


def parse_insurance_info(patient_record):
    insurance_data = {
        "Primary Insurance": None,
        "Primary Policy Number": None,
        "Primary Group Number": None,
        "Secondary Insurance": None,
        "Secondary Policy Number": None,
        "Secondary Group Number": None
    }

    insurance_section_started = False
    secondary_insurance_detected = False
    group_header_detected = False

    for element in patient_record:
        if 'INSURANCE INFORMATION' in element:
            insurance_section_started = True
            secondary_insurance_detected = False
            continue

        if insurance_section_started:
            split_element = element.split('\n')
            if 'Primary Insurance' in element:
                insurance_data["Primary Insurance"] = element.split('\n')[1].strip() if len(element.split('\n')) > 1 else None
            elif 'Secondary Insurance' in element and len(split_element) > 1 and split_element[1].strip():
                insurance_data["Secondary Insurance"] = element.split('\n')[1].strip() if len(element.split('\n')) > 1 else None
                secondary_insurance_detected = True
            elif 'Policy Number' in element:
                split_element = element.split('\n')
                if len(split_element) > 1:
                    if not insurance_data["Primary Policy Number"]:
                        insurance_data["Primary Policy Number"] = split_element[1].strip()
                    elif secondary_insurance_detected and not insurance_data["Secondary Policy Number"]:
                        insurance_data["Secondary Policy Number"] = split_element[1].strip()
            elif 'Group Number' in element:
                #print("Group Detected: ", element, secondary_insurance_detected)
                group_header_detected = not group_header_detected # toggle between T/F to proxy as first or second position.
                split_element = element.split('\n')
                if len(split_element) > 1:
                    if not insurance_data["Primary Group Number"] and group_header_detected:
                        insurance_data["Primary Group Number"] = split_element[1].strip()
                    elif secondary_insurance_detected and not insurance_data["Secondary Group Number"] and not group_header_detected:
                        insurance_data["Secondary Group Number"] = split_element[1].strip()

    return insurance_data

def structure_data(patient_data_list):
    # Define the column headers based on the sample data provided earlier
    column_headers = [
        "Name", 
        "Patient ID", 
        "Address", 
        "Home Phone", 
        "DOB", 
        "Gender", 
        "Primary Insurance", 
        "Primary Policy Number", 
        "Primary Group Number",
        "Secondary Insurance", 
        "Secondary Policy Number",
        "Secondary Group Number"
    ]

    # Initialize a list to hold structured patient records
    structured_patient_records = []

    # Iterate over each patient record in the list
    for patient_record in patient_data_list:
        # Extract the basic patient data
        patient_data = extract_patient_data(patient_record)
        # Extract the insurance information
        insurance_data = parse_insurance_info(patient_record)
        # Merge the two dictionaries
        full_patient_data = {**patient_data, **insurance_data}
        
        # Add the cleaned and transformed data to the list
        structured_patient_records.append(full_patient_data)

    # Create the DataFrame with the structured patient data
    structured_patient_df = pd.DataFrame(structured_patient_records, columns=column_headers)

    # Return the structured DataFrame
    return structured_patient_df

def validate_data(data_frame):
    # Performing Quality Assurance and Validation checks on the structured data

    # Completeness Check: Check for missing values in critical fields
    missing_values_check = data_frame.isnull().sum()

    # Consistency Check: Ensure data formats are consistent
    date_format_check = data_frame['DOB'].apply(lambda x: bool(re.match(r'\d{4}-\d{2}-\d{2}', x)) if pd.notnull(x) else True)
    phone_format_check = data_frame['Home Phone'].apply(lambda x: bool(re.match(r'\+\d-\d{3}-\d{3}-\d{4}', x)) if pd.notnull(x) else True)

    # Anomaly Detection: This can be complex and domain-specific. As a basic check, we can look for outliers in data like dates.
    dob_anomalies_check = data_frame['DOB'].describe()

    # Compile the results of the checks
    validation_results = {
        "Missing Values Check": missing_values_check,
        "Date Format Consistency": all(date_format_check),
        "Phone Format Consistency": all(phone_format_check),
        "DOB Anomalies Check": dob_anomalies_check
    }
    
    print(validation_results)  # Display validation results
    return data_frame  # Return the validated DataFrame


# Main function to orchestrate the cleaning process
def clean_patient_data(file_path):
    # Load the CSV file
    sxpatient_data = load_csv(file_path)

    # Segment the data
    segmented_patient_records = segment_data(sxpatient_data)

    # Structure the data
    structured_data_frame = structure_data(segmented_patient_records)

    # Validate the data
    validated_data = validate_data(structured_data_frame)
    
    return validated_data

# Path to the CSV file with escaped backslashes
file_path_sxpatient = 'C:\\Users\\danie\\OneDrive\\Desktop\\CSV02012024.CSV'
# Define the file path for the output CSV file
output_file_path = 'G:\\My Drive\\CocoWave\\XP typing bot\\cleaned_FEB01SXcsv_group.csv'

# Call the main function to clean the patient data
cleaned_patient_data = clean_patient_data(file_path_sxpatient)

# Display the first few rows of the cleaned and validated data to verify the output
print(cleaned_patient_data.head())

# Save the processed data to a CSV file
cleaned_patient_data.to_csv(output_file_path, index=False)

print(f"Processed data saved to {output_file_path}")

# Development Roadmap

# Do not delete leading zeros from insurance numbers