# Unused archive backup. This has been superceded by API_v3

import time
import requests

# Importing configuration loader
try:
    from MediLink import MediLink_ConfigLoader
except ImportError:
    import MediLink_ConfigLoader

# Class for handling API calls
class APIClient:
    def __init__(self):
        # Load configuration
        self.config, _ = MediLink_ConfigLoader.load_configuration()
        # Initialize token cache
        self.token_cache = {}

    # Method to get access token
    def get_access_token(self, endpoint_name):
        # Retrieve endpoint configuration
        endpoint_config = self.config['MediLink_Config']['endpoints'][endpoint_name]
        current_time = time.time()

        # Check if token is cached and still valid
        if endpoint_name in self.token_cache:
            cached_token = self.token_cache[endpoint_name]
            if cached_token['expires_at'] > current_time:
                return cached_token['access_token']

        # Prepare data for token request
        data = {
            'grant_type': 'client_credentials',
            'client_id': endpoint_config['client_id'],
            'client_secret': endpoint_config['client_secret'],
            'scope': 'hipaa'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        # Request token
        response = requests.post(endpoint_config['token_url'], headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data['access_token']
        expires_in = token_data.get('expires_in', 3600)

        # Cache token with expiration time adjusted
        self.token_cache[endpoint_name] = {
            'access_token': access_token,
            'expires_at': current_time + expires_in - 120
        }
        return access_token

    # Method for making API calls
    def make_api_call(self, endpoint_name, call_type, url_extension="", params=None, data=None):
        # Retrieve endpoint configuration
        endpoint_config = self.config['MediLink_Config']['endpoints'][endpoint_name]
        # Get access token
        token = self.get_access_token(endpoint_name)
        headers = {'Authorization': 'Bearer {}'.format(token), 'Accept': 'application/json'}

        # Construct full URL
        url = endpoint_config['api_url'] + url_extension

        # Make appropriate type of call
        if call_type == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif call_type == 'POST':
            headers['Content-Type'] = 'application/json'
            response = requests.post(url, headers=headers, json=data)
        elif call_type == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError("Unsupported call type")

        if response.status_code >= 400:
            print("Error {}: {}".format(response.status_code, response.text))
            response.raise_for_status()

        return response.json()

    # Method for creating coverage
    def create_coverage(self, endpoint_name, patient_info):
        return self.make_api_call(endpoint_name, 'POST', url_extension="/coverages", data=patient_info)

    # Method for getting all coverages
    def get_coverages(self, endpoint_name, params=None):
        return self.make_api_call(endpoint_name, 'GET', url_extension="/coverages", params=params)

    # Method for getting coverage by ID
    def get_coverage_by_id(self, endpoint_name, coverage_id):
        return self.make_api_call(endpoint_name, 'GET', url_extension="/coverages/{}".format(coverage_id))

    # Method for deleting coverage by ID
    def delete_coverage_by_id(self, endpoint_name, coverage_id):
        return self.make_api_call(endpoint_name, 'DELETE', url_extension="/coverages/{}".format(coverage_id))

    # Method for getting payer list
    def get_payer_list(self, endpoint_name, params=None):
        return self.make_api_call(endpoint_name, 'GET', url_extension="/availity-payer-list", params=params)

# Function to fetch payer name from API
def fetch_payer_name_from_api(payer_id, config, primary_endpoint='AVAILITY'):
    client = APIClient()

    # Step 1: Reload configuration for safety (This should be able to be replaced by APIClient())
    config, _ = MediLink_ConfigLoader.load_configuration()

    # Step 2: Check if the primary endpoint is specified and is valid 
    # (these validity checks will need to be incorporated into the main functionality)
    endpoints = config['MediLink_Config']['endpoints']
    if primary_endpoint and primary_endpoint in endpoints:
        endpoint_order = [primary_endpoint] + [endpoint for endpoint in endpoints if endpoint != primary_endpoint]
    else:
        endpoint_order = list(endpoints.keys())

    # Step 3: Iterate through available endpoints in specified order
    for endpoint_name in endpoint_order:
        endpoint_config = endpoints[endpoint_name]
        if not all(key in endpoint_config for key in ['token_url', 'client_id', 'client_secret']):
            MediLink_ConfigLoader.log("Skipping {} due to missing API keys.".format(endpoint_name), config, level="WARNING")
            continue

        try:
            response = client.get_payer_list(endpoint_name, params={'payerId': payer_id})
            if 'payers' in response and response['payers']:
                payer = response['payers'][0]
                payer_name = payer.get('displayName') or payer.get('name')
                
                MediLink_ConfigLoader.log("Successfully found payer at {} for ID {}: {}".format(endpoint_name, payer_id, payer_name), config, level="INFO")
                return payer_name
            else:
                MediLink_ConfigLoader.log("No payer found at {} for ID: {}. Trying next available endpoint.".format(endpoint_name, payer_id), config, level="INFO")
        except requests.RequestException as e:
            MediLink_ConfigLoader.log("API call failed at {} for Payer ID '{}': {}".format(endpoint_name, payer_id, str(e)), config, level="ERROR")

    error_message = "All endpoints exhausted for Payer ID {}.".format(payer_id)
    MediLink_ConfigLoader.log(error_message, config, level="CRITICAL")
    raise ValueError(error_message)

# Example usage
if __name__ == "__main__":
    client = APIClient()
    try:
        # Fetch and print payer name
        payer_name = fetch_payer_name_from_api("11347", 'config.yaml')
        print("Payer Name: {}".format(payer_name))
        
        # Example patient info
        patient_info = {
            "policyNumber": "12345", 
            "name": "John Doe", 
            "dob": "1980-01-01"
        }
        # Create coverage and print response
        response = client.create_coverage('AVAILITY', patient_info)
        print("Create Coverage Response: {}".format(response))
        
        # Get all coverages and print response
        response = client.get_coverages('AVAILITY')
        print("All Coverages: {}".format(response))
        
        # Example coverage ID
        coverage_id = "some-coverage-id"
        # Get coverage by ID and print response
        response = client.get_coverage_by_id('AVAILITY', coverage_id)
        print("Coverage by ID: {}".format(response))
        
        # Delete coverage by ID and print response
        response = client.delete_coverage_by_id('AVAILITY', coverage_id)
        print("Delete Coverage Response: {}".format(response))
        
    except Exception as e:
        # Print error if any
        print("Error: {}".format(e))
