import os
import sys
import csv
from MediLink_ConfigLoader import load_configuration, log
from MediLink_DataMgmt import consolidate_csvs


"""
1. ERA File Processing: Implement robust mechanisms for reading and parsing ERA files, addressing potential file integrity issues and accommodating scenarios with multiple payer addresses within a single ERA.
2. Wildcard File Processing: Enable effective batch processing of ERA files using wildcard patterns in the `--era_file_path` argument, resulting in a unified CSV output.
3. Date of Service Parsing: Enhance the parsing logic for 'Date of Service' to accommodate different segment identifiers, improving data extraction reliability.
4. Payer Address Extraction: Fine-tune the logic for extracting payer and provider addresses from ERA files, ensuring only relevant information is captured.
5. De-persisting Intermediate Files.
"""

# ERA Parser
def parse_era_content(content):
    extracted_data = []
    normalized_content = content.replace('~\n', '~')
    lines = normalized_content.split('~')
    
    # Reset these values for each new CLP segment
    record = {}
    check_eft, payer_address = None, None
    allowed_amount, write_off, patient_responsibility, adjustment_amount = 0, 0, 0, 0
    is_payer_section = False  # Flag to identify payer section for accurate address capture
    
    for line in lines:
        segments = line.split('*')
        
        if segments[0] == 'TRN' and len(segments) > 2:
            check_eft = segments[2]
            
        # Determine the start and end of the payer section to correctly capture the payer's address
        if segments[0] == 'N1':
            if segments[1] == 'PR':  # Payer information starts
                is_payer_section = True
                # payer_name = segments[2]  # Can capture payer name here if needed
            elif segments[1] == 'PE':  # Provider information starts, ending payer section
                is_payer_section = False
        
        # Correctly capture payer address only within payer section
        if is_payer_section and segments[0] == 'N3' and len(segments) > 1:
            payer_address = segments[1]
        
        if segments[0] == 'CLP' and len(segments) >= 5:
            if record:
                if adjustment_amount == 0 and (write_off > 0 or patient_responsibility > 0):
                    adjustment_amount = write_off + patient_responsibility

                # Finalize and append the current record before starting a new one
                record.update({
                    # 'Payer Name': payer_name,
                    'Payer Address': payer_address,
                    'Allowed Amount': allowed_amount,
                    'Write Off': write_off,
                    'Patient Responsibility': patient_responsibility,
                    'Adjustment Amount': adjustment_amount, 
                })
                extracted_data.append(record)
                
                # Reset variables for the next record
                allowed_amount, write_off, patient_responsibility, adjustment_amount = 0, 0, 0, 0
                # payer_address = None  # Reset address for the next CLP segment if it changes within one ERA file (so no. disable.)
            
            # Initialize a new record
            record = {
                'Check EFT': check_eft,
                'Chart Number': segments[1],
                'Payer Address': payer_address,
                'Amount Paid': segments[4],
                'Charge': segments[3],  # Total submitted charges for the claim
            }
        
        elif segments[0] == 'CAS':
            # Parsing CAS segments for Write Off and Patient Responsibility
            if segments[1] == 'CO':  # Write Off
                write_off += float(segments[3])
            elif segments[1] == 'PR':  # Patient Responsibility
                patient_responsibility += float(segments[3])
            elif segments[1] == 'OA':  # Capture Adjustment Amount from CAS*OA segment
                adjustment_amount += float(segments[3])
        
        elif segments[0] == 'AMT' and segments[1] == 'B6':
            # Allowed Amount from AMT segment
            allowed_amount += float(segments[2])
        
        elif segments[0] == 'DTM' and (segments[1] == '232' or segments[1] == '472'):
            record['Date of Service'] = segments[2]
    

    if record:
    # Final record handling
        if adjustment_amount == 0 and (write_off > 0 or patient_responsibility > 0):
            adjustment_amount = write_off + patient_responsibility
        # Append the last record
        record.update({
            'Allowed Amount': allowed_amount,
            'Write Off': write_off,
            'Patient Responsibility': patient_responsibility,
            'Adjustment Amount': adjustment_amount, 
        })
        extracted_data.append(record)
        
    return extracted_data

def translate_era_to_csv(files, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for file_path in files:
        # Ensure the file is read correctly
        with open(file_path, 'r') as era_file:
            era_content = era_file.read()
        
        data = parse_era_content(era_content)
        # print("Parsed Data: ", data)  # DEBUG
        
        csv_file_path = os.path.join(output_directory, os.path.basename(file_path) + '.csv')
        
        try:
            # Open the CSV file with explicit newline handling
            with open(csv_file_path, 'w', newline='') as csv_file:
                fieldnames = ['Date of Service',
                              'Check EFT', 
                              'Chart Number', 
                              'Payer Address', 
                              'Amount Paid', 
                              'Adjustment Amount',
                              'Allowed Amount',
                              'Write Off',
                              'Patient Responsibility',
                              'Charge'
                              ]
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                
                writer.writeheader()
                for record in data:
                    
                    # print("Writing record: ", record)
                    
                    writer.writerow({
                        'Date of Service': record.get('Date of Service', ''),
                        'Check EFT': record.get('Check EFT', ''),
                        'Chart Number': record.get('Chart Number', ''),
                        'Payer Address': record.get('Payer Address', ''),
                        'Amount Paid': record.get('Amount Paid', ''),
                        'Adjustment Amount': record.get('Adjustment Amount', ''),
                        'Allowed Amount': record.get('Allowed Amount', ''),
                        'Write Off': record.get('Write Off', ''),
                        'Patient Responsibility': record.get('Patient Responsibility', ''),
                        'Charge': record.get('Charge', ''),
                    })
                # Explicitly flush data to ensure it's written
                csv_file.flush()
        except Exception as e:
            print("Error writing CSV: ", e)

# User Interface
def user_confirm_overwrite(chart_numbers):
    """Asks the user for confirmation to overwrite an existing file, showing Chart Numbers."""
    print("The following Chart Numbers are in the existing file:")
    for number in chart_numbers:
        print(number)
    return input("The file already exists. Do you want to overwrite it? (y/n): ").strip().lower() == 'y'

if __name__ == "__main__":
    # Load configuration
    
    config, _ = load_configuration()
    
    # Setup logger
    local_storage_path = config['MediLink_Config']['local_storage_path']
    
    # Define output directory
    output_directory = os.path.join(local_storage_path, "translated_csvs")
    
    # Retrieve ERA files from command line arguments
    files = sys.argv[1:]  # Exclude the script name
    if not files:
        log("No ERA files provided as arguments.")
        sys.exit(1)

    # Translate ERA files to CSV format
    translate_era_to_csv(files, output_directory)
    
    # Consolidate CSVs
    consolidate_csv_path = consolidate_csvs(output_directory)
    if consolidate_csv_path:
        print("Consolidated CSV File Created: {}".format(consolidate_csv_path))
    else:
        print("No CSV file was created.")