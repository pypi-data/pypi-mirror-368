# MediLink_Gmail.py
import sys, os, subprocess, time, webbrowser, requests, json, ssl, signal

# Set up Python path to find MediCafe when running directly
def setup_python_path():
    """Set up Python path to find MediCafe package"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(current_dir)
    
    # Add workspace root to Python path if not already present
    if workspace_root not in sys.path:
        sys.path.insert(0, workspace_root)

# Set up paths before importing MediCafe
setup_python_path()

from MediCafe.core_utils import get_shared_config_loader

# Get shared config loader
MediLink_ConfigLoader = get_shared_config_loader()
if MediLink_ConfigLoader:
    load_configuration = MediLink_ConfigLoader.load_configuration
    log = MediLink_ConfigLoader.log
else:
    # Fallback functions if config loader is not available
    def load_configuration():
        return {}, {}
    def log(message, level="INFO"):
        print("[{}] {}".format(level, message))
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread, Event
import platform
import ctypes

config, _ = load_configuration()
local_storage_path = config['MediLink_Config']['local_storage_path']
downloaded_emails_file = os.path.join(local_storage_path, 'downloaded_emails.txt')

server_port = 8000
cert_file = 'server.cert'
key_file = 'server.key'
# Try to find openssl.cnf in various locations
openssl_cnf = 'openssl.cnf'  # Use relative path since we're running from MediLink directory
if not os.path.exists(openssl_cnf):
    log("Could not find openssl.cnf at: " + os.path.abspath(openssl_cnf))
    # Try MediLink directory
    medilink_dir = os.path.dirname(os.path.abspath(__file__))
    medilink_openssl = os.path.join(medilink_dir, 'openssl.cnf')
    log("Trying MediLink directory: " + medilink_openssl)
    if os.path.exists(medilink_openssl):
        openssl_cnf = medilink_openssl
        log("Found openssl.cnf at: " + openssl_cnf)
    else:
        # Try one directory up
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alternative_path = os.path.join(parent_dir, 'MediBot', 'openssl.cnf')
        log("Trying alternative path: " + alternative_path)
        if os.path.exists(alternative_path):
            openssl_cnf = alternative_path
            log("Found openssl.cnf at: " + openssl_cnf)
        else:
            log("Could not find openssl.cnf at alternative path either")

httpd = None  # Global variable for the HTTP server
shutdown_event = Event()  # Event to signal shutdown

# Define the scopes for the Gmail API and other required APIs
SCOPES = ' '.join([
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/script.external_request',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/script.scriptapp',
    'https://www.googleapis.com/auth/drive'
])

# Path to token.json file
TOKEN_PATH = 'token.json'

# Determine the operating system and version
os_name = platform.system()
os_version = platform.release()

# Set the credentials path based on the OS and version
if os_name == 'Windows' and 'XP' in os_version:
    CREDENTIALS_PATH = 'F:\\Medibot\\json\\credentials.json'
else:
    CREDENTIALS_PATH = 'json\\credentials.json'

# Log the selected path for verification
log("Using CREDENTIALS_PATH: {}".format(CREDENTIALS_PATH), config, level="INFO")

REDIRECT_URI = 'https://127.0.0.1:8000'

def get_authorization_url():
    with open(CREDENTIALS_PATH, 'r') as credentials_file:
        credentials = json.load(credentials_file)
    client_id = credentials['web']['client_id']
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "response_type=code&"
        "client_id={}&"
        "redirect_uri={}&"
        "scope={}&"
        "access_type=offline&"  # Requesting offline access allows the application to obtain a refresh token, enabling it to access resources even when the user is not actively using the app. This is useful for long-lived sessions.
        # To improve user experience, consider changing this to 'online' if you don't need offline access:
        # "access_type=online&"  # Use this if you only need access while the user is actively using the app and don't require a refresh token.
        
        "prompt=consent"  # This forces the user to re-consent to the requested scopes every time they authenticate. While this is useful for ensuring the user is aware of the permissions being granted, it can be modified to 'none' or omitted entirely if the application is functioning correctly and tokens are being refreshed properly.
        # To improve user experience, consider changing this to 'none' if you want to avoid showing the consent screen every time:
        # "prompt=none"  # Use this if you want to skip the consent screen for users who have already granted permissions.
        # Alternatively, you can omit the prompt parameter entirely to use the default behavior:
        # # "prompt="  # Omitting this will show the consent screen only when necessary.
    ).format(client_id, REDIRECT_URI, SCOPES)
    log("Generated authorization URL: {}".format(auth_url))
    return auth_url

def exchange_code_for_token(auth_code, retries=3):
    for attempt in range(retries):
        try:
            with open(CREDENTIALS_PATH, 'r') as credentials_file:
                credentials = json.load(credentials_file)
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                'code': auth_code,
                'client_id': credentials['web']['client_id'],
                'client_secret': credentials['web']['client_secret'],
                'redirect_uri': REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
            response = requests.post(token_url, data=data)
            log("Token exchange response: Status code {}, Body: {}".format(response.status_code, response.text))
            token_response = response.json()
            if response.status_code == 200:
                token_response['token_time'] = time.time()
                return token_response
            else:
                log("Token exchange failed: {}".format(token_response))
                if attempt < retries - 1:
                    log("Retrying token exchange... (Attempt {}/{})".format(attempt + 1, retries))
        except Exception as e:
            log("Error during token exchange: {}".format(e))
    return {}

def get_access_token():
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'r') as token_file:
            token_data = json.load(token_file)
            log("Loaded token data:\n {}".format(token_data))
            
            if 'access_token' in token_data and 'expires_in' in token_data:
                try:
                    # Use current time if 'token_time' is missing
                    token_time = token_data.get('token_time', time.time())
                    token_expiry_time = token_time + token_data['expires_in']
                
                except KeyError as e:
                    log("KeyError while accessing token data: {}".format(e))
                    return None
                
                if token_expiry_time > time.time():
                    log("Access token is still valid. Expires in {} seconds.".format(token_expiry_time - time.time()))
                    return token_data['access_token']
                else:
                    log("Access token has expired. Current time: {}, Expiry time: {}".format(time.time(), token_expiry_time))
                    new_token_data = refresh_access_token(token_data.get('refresh_token'))
                    if 'access_token' in new_token_data:
                        new_token_data['token_time'] = time.time()
                        with open(TOKEN_PATH, 'w') as token_file:
                            json.dump(new_token_data, token_file)
                        log("Access token refreshed successfully. New token data: {}".format(new_token_data))
                        return new_token_data['access_token']
                    else:
                        log("Failed to refresh access token. New token data: {}".format(new_token_data))
                        return None
    log("Access token not found. Please authenticate.")
    return None

def refresh_access_token(refresh_token):
    log("Refreshing access token.")
    with open(CREDENTIALS_PATH, 'r') as credentials_file:
        credentials = json.load(credentials_file)
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'client_id': credentials['web']['client_id'],
        'client_secret': credentials['web']['client_secret'],
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    response = requests.post(token_url, data=data)
    log("Refresh token response: Status code {}, Body:\n {}".format(response.status_code, response.text))
    if response.status_code == 200:
        log("Access token refreshed successfully.")
        return response.json()
    else:
        log("Failed to refresh access token. Status code: {}".format(response.status_code))
        return {}

def bring_window_to_foreground():
    """Brings the current window to the foreground on Windows."""
    try:
        if platform.system() == 'Windows':
            # Get the current process ID
            pid = os.getpid()
            # Get the window handle for the current process
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            # Get the process ID of the window
            current_pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(current_pid))
            
            # If the window is not ours, try to bring it to front
            if current_pid.value != pid:
                # Try to set the window to foreground
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                # If that fails, try the alternative method
                if ctypes.windll.user32.GetForegroundWindow() != hwnd:
                    ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE = 9
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception as e:
        log("Error bringing window to foreground: {}".format(e))

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-type', 'application/json')

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_headers()
        self.end_headers()

    def do_POST(self):
        if self.path == '/download':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            links = data.get('links', [])

            # Log the content of links
            log("Received links: {}".format(links))

            file_ids = [link.get('fileId', None) for link in links if link.get('fileId')]
            log("File IDs received from client: {}".format(file_ids))
            
            # Proceed with downloading files
            download_docx_files(links)
            self.send_response(200)
            self._set_headers()  # Include CORS headers
            self.end_headers()
            response = json.dumps({"status": "success", "message": "All files downloaded", "fileIds": file_ids})
            self.wfile.write(response.encode('utf-8'))
            shutdown_event.set()
            bring_window_to_foreground()  # Bring window to foreground after download
        elif self.path == '/shutdown':
            log("Shutdown request received.")
            self.send_response(200)
            self._set_headers()
            self.end_headers()
            response = json.dumps({"status": "success", "message": "Server is shutting down."})
            self.wfile.write(response.encode('utf-8'))
            shutdown_event.set()  # Signal shutdown event instead of calling stop_server directly
        elif self.path == '/delete-files':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            file_ids = data.get('fileIds', [])
            log("File IDs to delete received from client: {}".format(file_ids))
            
            if not isinstance(file_ids, list):
                self.send_response(400)
                self._set_headers()
                self.end_headers()
                response = json.dumps({"status": "error", "message": "Invalid fileIds parameter."})
                self.wfile.write(response.encode('utf-8'))
                return
            
            self.send_response(200)
            self._set_headers()  # Include CORS headers
            self.end_headers()
            response = json.dumps({"status": "success", "message": "Files deleted successfully."})
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        log("Full request path: {}".format(self.path))  # Log the full path for debugging
        if self.path.startswith("/?code="):
            auth_code = self.path.split('=')[1].split('&')[0]
            auth_code = requests.utils.unquote(auth_code)  # Decode if URL-encoded
            log("Received authorization code: {}".format(auth_code))
            if is_valid_authorization_code(auth_code):
                try:
                    token_response = exchange_code_for_token(auth_code)
                    if 'access_token' not in token_response:
                        # Check for specific error message
                        if token_response.get("status") == "error":
                            self.send_response(400)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            self.wfile.write(token_response["message"].encode())
                            return
                        # Handle other cases
                        raise ValueError("Access token not found in response.")
                except Exception as e:
                    log("Error during token exchange: {}".format(e))
                    self.send_response(500)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write("An error occurred during authentication. Please try again.".encode())
                else:
                    log("Token response: {}".format(token_response))  # Add this line
                    if 'access_token' in token_response:
                        with open(TOKEN_PATH, 'w') as token_file:
                            json.dump(token_response, token_file)
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write("Authentication successful. You can close this window now.".encode())
                        initiate_link_retrieval(config)  # Pass config here
                    else:
                        log("Authentication failed with response: {}".format(token_response))  # Log the full response
                        if 'error' in token_response:
                            error_description = token_response.get('error_description', 'No description provided.')
                            log("Error details: {}".format(error_description))  # Log specific error details

                        # Provide user feedback based on the error
                        if token_response.get('error') == 'invalid_grant':
                            log("Invalid grant error encountered. Authorization code: {}, Response: {}".format(auth_code, token_response))
                            check_invalid_grant_causes(auth_code)
                            clear_token_cache()  # Clear the cache on invalid grant
                            user_message = "Authentication failed: Invalid or expired authorization code. Please try again."
                        else:
                            user_message = "Authentication failed. Please check the logs for more details."

                        self.send_response(400)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(user_message.encode())
                        shutdown_event.set()  # Signal shutdown event after failed authentication
            else:
                log("Invalid authorization code format: {}".format(auth_code))
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write("Invalid authorization code format. Please try again.".encode())
                shutdown_event.set()  # Signal shutdown event after failed authentication
        elif self.path == '/downloaded-emails':
            self.send_response(200)
            self._set_headers()
            self.end_headers()
            downloaded_emails = load_downloaded_emails()
            response = json.dumps({"downloadedEmails": list(downloaded_emails)})
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'HTTPS server is running.')

def generate_self_signed_cert(cert_file, key_file):
    log("Checking if certificate file exists: " + cert_file)
    log("Checking if key file exists: " + key_file)
    
    # Check if certificate exists and is not expired
    cert_needs_regeneration = True
    if os.path.exists(cert_file):
        try:
            # Check certificate expiration
            check_cmd = ['openssl', 'x509', '-in', cert_file, '-checkend', '86400', '-noout']  # Check if expires in next 24 hours
            result = subprocess.call(check_cmd)
            if result == 0:
                log("Certificate is still valid")
                cert_needs_regeneration = False
            else:
                log("Certificate is expired or will expire soon")
                # Delete expired certificate and key files
                try:
                    if os.path.exists(cert_file):
                        os.remove(cert_file)
                        log("Deleted expired certificate file: {}".format(cert_file))
                    if os.path.exists(key_file):
                        os.remove(key_file)
                        log("Deleted expired key file: {}".format(key_file))
                except Exception as e:
                    log("Error deleting expired certificate files: {}".format(e))
        except Exception as e:
            log("Error checking certificate expiration: {}".format(e))
    
    if cert_needs_regeneration:
        log("Generating self-signed SSL certificate...")
        cmd = [
            'openssl', 'req', '-config', openssl_cnf, '-nodes', '-new', '-x509',
            '-keyout', key_file,
            '-out', cert_file,
            '-days', '365',
            '-sha256'  # Use SHA-256 for better security
            #'-subj', '/C=US/ST=...' The openssl.cnf file contains default values for these fields, but they can be overridden by the -subj option.
        ]
        try:
            log("Running command: " + ' '.join(cmd))
            result = subprocess.call(cmd)
            log("Command finished with result: " + str(result))
            if result != 0:
                raise RuntimeError("Failed to generate self-signed certificate")
            
            # Verify the certificate was generated correctly
            verify_cmd = ['openssl', 'x509', '-in', cert_file, '-text', '-noout']
            verify_result = subprocess.call(verify_cmd)
            if verify_result != 0:
                raise RuntimeError("Generated certificate verification failed")
                
            log("Self-signed SSL certificate generated and verified successfully.")
        except Exception as e:
            log("Error generating self-signed certificate: {}".format(e))
            raise

def run_server():
    global httpd
    try:
        log("Attempting to start server on port " + str(server_port))
        server_address = ('0.0.0.0', server_port)  # Bind to all interfaces
        httpd = HTTPServer(server_address, RequestHandler)
        log("Attempting to wrap socket with SSL. cert_file=" + cert_file + ", key_file=" + key_file)
        
        if not os.path.exists(cert_file):
            log("Error: Certificate file not found: " + cert_file)
        if not os.path.exists(key_file):
            log("Error: Key file not found: " + key_file)
        
        httpd.socket = ssl.wrap_socket(httpd.socket, certfile=cert_file, keyfile=key_file, server_side=True)
        log("Starting HTTPS server on port {}".format(server_port))
        httpd.serve_forever()
    except Exception as e:
        log("Error in serving: {}".format(e))
        stop_server()

def stop_server():
    global httpd
    if httpd:
        log("Stopping HTTPS server.")
        httpd.shutdown()
        httpd.server_close()
        log("HTTPS server stopped.")
    shutdown_event.set()  # Signal shutdown event
    bring_window_to_foreground()  # Bring window to foreground after shutdown

def load_downloaded_emails():
    downloaded_emails = set()
    if os.path.exists(downloaded_emails_file):
        with open(downloaded_emails_file, 'r') as file:
            downloaded_emails = set(line.strip() for line in file)
    log("Loaded downloaded emails: {}".format(downloaded_emails))
    return downloaded_emails

def download_docx_files(links):
    # Load the set of downloaded emails
    # TODO (LOW-MEDIUM PRIORITY - CSV File Detection and Routing):
    # PROBLEM: Downloaded files may include CSV files that need special handling and routing.
    # Currently all files are treated the same regardless of extension.
    #
    # IMPLEMENTATION REQUIREMENTS:
    # 1. File Extension Detection:
    #    - Check each downloaded file for .csv extension (case-insensitive)
    #    - Also check for common CSV variants: .txt, .tsv, .dat (based on content)
    #    - Handle files with multiple extensions like "report.csv.zip"
    #
    # 2. Content-Based Detection (Advanced):
    #    - For files without clear extensions, peek at content
    #    - Look for CSV patterns: comma-separated values, consistent column counts
    #    - Handle Excel files that might be CSV exports (.xlsx with CSV content)
    #
    # 3. CSV Routing Logic:
    #    - Move CSV files to dedicated CSV processing directory
    #    - Maintain file naming conventions for downstream processing
    #    - Log CSV file movements for audit trail
    #    - Preserve original file permissions and timestamps
    #
    # IMPLEMENTATION STEPS:
    # 1. Add helper function detect_csv_files(downloaded_files) -> list
    # 2. Add helper function move_csv_to_processing_dir(csv_file, destination_dir)
    # 3. Add configuration for CSV destination directory in config file
    # 4. Update this function to call CSV detection and routing after download
    # 5. Add error handling for file movement failures
    # 6. Add logging for all CSV file operations
    #
    # CONFIGURATION NEEDED:
    # - config['csv_processing_dir']: Where to move detected CSV files
    # - config['csv_file_extensions']: List of extensions to treat as CSV
    # - config['csv_content_detection']: Boolean to enable content-based detection
    #
    # ERROR HANDLING:
    # - Handle permission errors when moving files
    # - Handle disk space issues
    # - Gracefully handle corrupted or locked files
    # - Provide fallback options when CSV directory is unavailable
    #
    # TESTING SCENARIOS:
    # - Mixed file types: .docx, .csv, .pdf in same download batch
    # - CSV files with unusual extensions (.txt, .dat)
    # - Large CSV files (>100MB)
    # - CSV files in ZIP archives
    #
    # FILES TO MODIFY: This file (download_docx_files function)
    # RELATED: May need updates to CSV processing modules that expect files in specific locations
    downloaded_emails = load_downloaded_emails()

    for link in links:
        try:
            url = link.get('url', '')
            filename = link.get('filename', '')
            
            # Log the variables to debug
            log("Processing link: url='{}', filename='{}'".format(url, filename))
            
            # CSV ROUTING PLACEHOLDER:
            # - Detect CSV-like extensions before download and log the intended routing decision.
            # - This is a no-op for now to avoid side-effects until the pipeline is verified on XP.
            lower_name = (filename or '').lower()
            looks_like_csv = any(lower_name.endswith(ext) for ext in ['.csv', '.tsv', '.txt', '.dat'])
            if looks_like_csv:
                log("[CSV Routing Preview] Detected CSV-like filename: {}. Would route to CSV processing directory.".format(filename))
            
            # Skip if email already downloaded
            if filename in downloaded_emails:
                log("Skipping already downloaded email: {}".format(filename))
                continue

            log("Downloading .docx file from URL: {}".format(url))
            response = requests.get(url, verify=False)  # Set verify to False for self-signed certs
            if response.status_code == 200:
                file_path = os.path.join(local_storage_path, filename)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                log("Downloaded .docx file: {}".format(filename))
                # Add to the set and save the updated list
                downloaded_emails.add(filename)
                with open(downloaded_emails_file, 'a') as file:
                    file.write(filename + '\n')
            else:
                log("Failed to download .docx file from URL: {}. Status code: {}".format(url, response.status_code))
        except Exception as e:
            log("Error downloading .docx file from URL: {}. Error: {}".format(url, e))

def open_browser_with_executable(url, browser_path=None):
    try:
        if browser_path:
            log("Attempting to open URL with provided executable: {} {}".format(browser_path, url))
            process = subprocess.Popen([browser_path, url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                log("Browser opened with provided executable path using subprocess.Popen.")
            else:
                log("Browser failed to open using subprocess.Popen. Return code: {}. Stderr: {}".format(process.returncode, stderr))
        else:
            log("No browser path provided. Attempting to open URL with default browser: {}".format(url))
            webbrowser.open(url)
            log("Default browser opened.")
    except Exception as e:
        log("Failed to open browser: {}".format(e))

def initiate_link_retrieval(config):
    log("Initiating browser via implicit GET.")
    url_get = "https://script.google.com/macros/s/{}/exec?action=get_link".format(config['MediLink_Config']['webapp_deployment_id'])  # Use config here
    open_browser_with_executable(url_get)
    
    log("Preparing POST call.")
    url = "https://script.google.com/macros/s/{}/exec".format(config['MediLink_Config']['webapp_deployment_id'])  # Use config here
    downloaded_emails = list(load_downloaded_emails())
    payload = {
        "downloadedEmails": downloaded_emails
    }

    access_token = get_access_token()
    if not access_token:
        log("Access token not found. Please authenticate first.")
        shutdown_event.set()  # Signal shutdown event if token is not found
        return

    # Inspect the token to check its validity and permissions
    token_info = inspect_token(access_token)
    if token_info is None:
        log("Access token is invalid. Please re-authenticate.")
        shutdown_event.set()  # Signal shutdown event if token is invalid
        return

    # Proceed with the rest of the function if the token is valid
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'Content-Type': 'application/json'
    }
    
    log("Request headers: {}".format(headers))
    log("Request payload: {}".format(payload))

    handle_post_response(url, payload, headers)
        
def handle_post_response(url, payload, headers):
    try:
        response = requests.post(url, json=payload, headers=headers)
        log("Response status code: {}".format(response.status_code))
        log("Response body: {}".format(response.text))

        if response.status_code == 200:
            response_data = response.json()
            log("Parsed response data: {}".format(response_data))  # Log the parsed response data
            if response_data.get("status") == "error":
                log("Error message from server: {}".format(response_data.get("message")))
                print("Error: {}".format(response_data.get("message")))
                shutdown_event.set()  # Signal shutdown event after error
            else:
                log("Link retrieval initiated successfully.")
        elif response.status_code == 401:
            log("Unauthorized. Check if the token has the necessary scopes.Response body: {}".format(response.text))
            # Inspect the token to log its details
            token_info = inspect_token(headers['Authorization'].split(' ')[1])
            log("Token details: {}".format(token_info))
            shutdown_event.set()
        elif response.status_code == 403:
            log("Forbidden access. Ensure that the OAuth client has the correct permissions. Response body: {}".format(response.text))
            shutdown_event.set()
        elif response.status_code == 404:
            log("Not Found. Verify the URL and ensure the Apps Script is deployed correctly. Response body: {}".format(response.text))
            shutdown_event.set()
        else:
            log("Failed to initiate link retrieval. Unexpected status code: {}. Response body: {}".format(response.status_code, response.text))
            shutdown_event.set()
    except requests.exceptions.RequestException as e:
        log("RequestException during link retrieval initiation: {}".format(e))
        shutdown_event.set()
    except Exception as e:
        log("Unexpected error during link retrieval initiation: {}".format(e))
        shutdown_event.set()

def inspect_token(access_token):
    info_url = "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}".format(access_token)
    try:
        response = requests.get(info_url)
        log("Token info: Status code {}, Body: {}".format(response.status_code, response.text))
        
        if response.status_code == 200:
            return response.json()
        else:
            log("Failed to inspect token. Status code: {}, Body: {}".format(response.status_code, response.text))
            # Check for invalid token
            if response.status_code == 400 and "invalid_token" in response.text:
                log("Access token is invalid. Deleting token.json and stopping the server.")
                delete_token_file()  # Delete the token.json file
                print("Access token is invalid. Please re-authenticate and restart the server.")
                stop_server()  # Stop the server
                return None  # Return None for invalid tokens
            return None  # Return None for other invalid tokens
    except Exception as e:
        log("Exception during token inspection: {}".format(e))
        return None

def delete_token_file():
    try:
        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH)
            log("Deleted token.json successfully.")
        else:
            log("token.json does not exist.")
    except Exception as e:
        log("Error deleting token.json: {}".format(e))

def signal_handler(sig, frame):
    log("Signal received: {}. Initiating shutdown.".format(sig))
    stop_server()
    sys.exit(0)

def auth_and_retrieval():
    access_token = get_access_token()
    if not access_token:
        log("Access token not found or expired. Please authenticate first.")
        #print("If the browser does not open automatically, please open the following URL in your browser to authorize the application:")
        auth_url = get_authorization_url()
        #print(auth_url)
        open_browser_with_executable(auth_url)
        shutdown_event.wait()  # Wait for the shutdown event to be set after authentication
    else:
        log("Access token found. Proceeding.")
        initiate_link_retrieval(config)  # Pass config here
        shutdown_event.wait()  # Wait for the shutdown event to be set

def is_valid_authorization_code(auth_code):
    # Check if the authorization code is not None and is a non-empty string
    if auth_code and isinstance(auth_code, str) and len(auth_code) > 0:  # Check for non-empty string
        return True
    log("Invalid authorization code format: {}".format(auth_code))
    return False

def clear_token_cache():
    if os.path.exists(TOKEN_PATH):
        os.remove(TOKEN_PATH)
        log("Cleared token cache.")

def check_invalid_grant_causes(auth_code):
    # TODO Implement this function in the future to check for common causes of invalid_grant error
    # Log potential causes for invalid_grant
    # XP/Network NOTE: On older systems, clock skew and reused codes are frequent causes.
    log("FUTURE IMPLEMENTATION: Checking common causes for invalid_grant error with auth code: {}".format(auth_code))
    # Suggested checks (to be implemented when plumbing is ready):
    # - Has authorization code already been used?
    # - Does redirect URI exactly match the one registered (case and trailing slashes)?
    # - Is system clock skewed? Compare to Google time; log skew if detected.
    # - Are the requested scopes enabled for this OAuth client?
    # - Did the user revoke access between code issuance and token exchange?
    # Each of these would produce a specific log to speed up troubleshooting on XP.
"""
if is_code_used(auth_code):
        log("Authorization code has already been used.")
    if not is_redirect_uri_correct():
        log("Redirect URI does not match the registered URI.")
"""

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Generate SSL certificate if it doesn't exist
        generate_self_signed_cert(cert_file, key_file)

        from threading import Thread
        log("Starting server thread.")
        server_thread = Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()

        auth_and_retrieval()

        log("Stopping HTTPS server.")
        stop_server()  # Ensure the server is stopped
        log("Waiting for server thread to finish.")
        server_thread.join()  # Wait for the server thread to finish
    except KeyboardInterrupt:
        log("KeyboardInterrupt received, stopping server.")
        stop_server()
        sys.exit(0)
    except Exception as e:
        log("An error occurred: {}".format(e))
        stop_server()
        sys.exit(1)