import csv
import os
import sys

"""
This script processes a 277 healthcare claim status response file, extracting and structuring key information
about each claim into a CSV format. The goal is to interpret acknowledgment returns and provide a readable receipt
of claim statuses for further analysis or record-keeping.

Extracted fields and their sources from the 277 transaction set include:
- Clearing House: Extracted from 'NM1' segment where entity identifier code is '41' (payer) as the clearinghouse or payer name.
- Received Date: Extracted from the 'DTP' segment with qualifier '050' indicating the date claim information was received.
- Claim Status Tracking #: Extracted from the 'TRN' segment, representing a unique identifier used to track the claim.
- Billed Amount: Extracted from the 'AMT' segment with qualifier 'YU' representing the total billed amount.
- Date of Service: Extracted from the 'DTP' segment with qualifier '472', indicating the date services were rendered.
- Last and First Name: Extracted from 'NM1' segment where entity identifier is 'QC' (patient) to obtain patient's last and first names.
- Acknowledged Amount: Extracted from the 'STC' segment, specifically the monetary amount acknowledged.
- Status: Extracted from the 'STC' segment, indicating the processing status of the claim.

Each record corresponds to a single claim, and the script consolidates these records from the raw 277 file into a structured CSV file.
The CSV output contains headers corresponding to the above fields for ease of review and use in subsequent processes.

Prerequisites:
- Python 3.x
- Access to a filesystem for reading input files and writing output CSV files.

Usage:
The script requires the path to the 277 file as input and specifies an output directory for the CSV files.
Example command-line usage:
    python3 MediLink_277_decoder.py input_file.txt output_directory
"""

def parse_277_content(content):
    segments = content.split('~')
    records = []
    current_record = {}
    for segment in segments:
        parts = segment.split('*')
        if parts[0] == 'HL':
            if current_record:
                records.append(current_record)
                current_record = {}
        elif parts[0] == 'NM1':
            if parts[1] == 'QC':  # Patient information
                current_record['Last'] = parts[3]
                current_record['First'] = parts[4]
            elif parts[1] == '41':  # Payer information
                current_record['Clearing House'] = parts[3]
        elif parts[0] == 'TRN':
            current_record['Claim Status Tracking #'] = parts[2]
        elif parts[0] == 'STC':
            current_record['Status'] = parts[1]
            current_record['Acknowledged Amt'] = parts[4]
        elif parts[0] == 'DTP':
            if parts[1] == '472':  # Service date
                current_record['Date of Service'] = parts[3]
            elif parts[1] == '050':  # Received date
                current_record['Received Date'] = parts[3]
        elif parts[0] == 'AMT':
            if parts[1] == 'YU':
                current_record['Billed Amt'] = parts[2]
    
    if current_record:
        records.append(current_record)
    
    return records

def write_records_to_csv(records, output_file_path):
    with open(output_file_path, 'w', newline='') as csvfile:
        fieldnames = ['Clearing House', 'Received Date', 'Claim Status Tracking #', 'Billed Amt', 'Date of Service', 'Last', 'First', 'Acknowledged Amt', 'Status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record)

def main(file_path, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    output_file_path = os.path.join(output_directory, os.path.basename(file_path) + '_decoded.csv')
    
    with open(file_path, 'r') as file:
        content = file.read().replace('\n', '')
    
    records = parse_277_content(content)
    write_records_to_csv(records, output_file_path)
    print("Decoded data written to {}".format(output_file_path))

if __name__ == "__main__":
    file_path = sys.argv[1]
    output_directory = 'output'
    main(file_path, output_directory)