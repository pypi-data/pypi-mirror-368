# Unused archive backup. This has been superceded by API_v2

import time, requests
try:
    from MediLink import MediLink_ConfigLoader
except ImportError:
    import MediLink_ConfigLoader

# Fetches the payer name from API based on the payer ID.
def fetch_payer_name_from_api(payer_id, config, primary_endpoint='AVAILITY'):
    """
    Fetches the payer name from the API using the provided payer ID.

    Args:
        payer_id (str): The ID of the payer.
        config (dict): Configuration settings.
        primary_endpoint (str): The primary endpoint for resolving payer information.

    Raises:
        ValueError: If all endpoints are exhausted without finding the payer.

    Returns:
        str: The fetched payer name.
    """
    # Reload for safety
    config, _ = MediLink_ConfigLoader.load_configuration()
    
    # Step 1: Retrieve endpoint configurations
    endpoints = config['MediLink_Config']['endpoints']
    tried_endpoints = []

    # Step 2: Check if the primary endpoint is specified and is valid
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

        # Step 4: Get access token for the endpoint
        token = get_access_token(endpoint_config)
        api_url = endpoint_config.get("api_url", "")
        headers = {'Authorization': 'Bearer {}'.format(token), 'Accept': 'application/json'}
        params = {'payerId': payer_id}

        try:
            # Step 5: Make API call to fetch payer name
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if 'payers' in data and data['payers']:
                payer = data['payers'][0]
                payer_name = payer.get('displayName') or payer.get('name')
                
                # Log successful match
                MediLink_ConfigLoader.log("Successfully found payer at {} for ID {}: {}".format(endpoint_name, payer_id, payer_name), config, level="INFO")
                
                return payer_name
            else:
                MediLink_ConfigLoader.log("No payer found at {} for ID: {}. Trying next available endpoint.".format(endpoint_name, payer_id), config, level="INFO")
        except requests.RequestException as e:
            # Step 6: Log API call failure
            MediLink_ConfigLoader.log("API call failed at {} for Payer ID '{}': {}".format(endpoint_name, payer_id, str(e)), config, level="ERROR")
            tried_endpoints.append(endpoint_name)
    
    # Step 7: Log all endpoints exhaustion and raise error
    error_message = "All endpoints exhausted for Payer ID {}. Endpoints tried: {}".format(payer_id, ', '.join(tried_endpoints))
    MediLink_ConfigLoader.log(error_message, config, level="CRITICAL")
    raise ValueError(error_message)

# Test Case for API fetch
#payer_id = "11347"
#config = load_configuration() 
#payer_name = fetch_payer_name_from_api(payer_id, config, endpoint='AVAILITY')
#print(payer_id, payer_name)

# Initialize a global dictionary to store the access token and its expiry time
# TODO (Low API) This will need to get setup for each endpoint separately. 
token_cache = {
    'access_token': None,
    'expires_at': 0  # Timestamp of when the token expires
}

def get_access_token(endpoint_config):
    current_time = time.time()
    
    # Check if the cached token is still valid
    if token_cache['access_token'] and token_cache['expires_at'] > current_time:
        return token_cache['access_token']

    # Validate endpoint configuration
    if not endpoint_config or not all(k in endpoint_config for k in ['client_id', 'client_secret', 'token_url']):
        raise ValueError("Endpoint configuration is incomplete or missing necessary fields.")

    # Extract credentials and URL from the config
    CLIENT_ID = endpoint_config.get("client_id")
    CLIENT_SECRET = endpoint_config.get("client_secret")
    url = endpoint_config.get("token_url")

    # Setup the data payload and headers for the HTTP request
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'hipaa'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        # Perform the HTTP request to get the access token
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # This will raise an exception for HTTP error statuses
        json_response = response.json()
        access_token = json_response.get('access_token')
        expires_in = json_response.get('expires_in', 3600)  # Default to 3600 seconds if not provided

        if not access_token:
            raise ValueError("No access token returned by the server.")
        
        # Store the access token and calculate the expiry time
        token_cache['access_token'] = access_token
        token_cache['expires_at'] = current_time + expires_in - 120  # Subtracting 120 seconds to provide buffer

        return access_token
    except requests.RequestException as e:
        # Handle HTTP errors (e.g., network problems, invalid response)
        error_msg = "Failed to retrieve access token: {0}. Response status: {1}".format(str(e), response.status_code if response else 'No response')
        raise Exception(error_msg)
    except ValueError as e:
        # Handle specific errors like missing access token
        raise Exception("Configuration or server response error: {0}".format(str(e)))