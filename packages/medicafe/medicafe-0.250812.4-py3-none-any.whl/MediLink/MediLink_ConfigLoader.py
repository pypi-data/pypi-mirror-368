# MediLink_ConfigLoader.py
import os, json, logging, sys, platform, yaml
from datetime import datetime
from collections import OrderedDict

"""
This function should be generalizable to have a initialization script over all the Medi* functions
"""
def load_configuration(config_path=os.path.join(os.path.dirname(__file__), '..', 'json', 'config.json'), crosswalk_path=os.path.join(os.path.dirname(__file__), '..', 'json', 'crosswalk.json')):
    """
    Loads endpoint configuration, credentials, and other settings from JSON or YAML files.
        
    Returns: A tuple containing dictionaries with configuration settings for the main config and crosswalk.
    """
    # TODO (Low Config Upgrade) The Medicare / Private differentiator flag probably needs to be pulled or passed to this.
    # BUG Hardcode sucks. This should probably be some local env variable. 
    # Detect the operating system
    if platform.system() == 'Windows' and platform.release() == 'XP':
        # Use F: paths for Windows XP
        config_path = "F:\\Medibot\\json\\config.json"
        crosswalk_path = "F:\\Medibot\\json\\crosswalk.json"
    else:
        # Use G: paths for other versions of Windows
        config_path = "G:\\My Drive\\Codes\\MediCafe\\json\\config.json"
        crosswalk_path = "G:\\My Drive\\Codes\\MediCafe\\json\\crosswalk.json"
    
    try:
        with open(config_path, 'r') as config_file:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config = yaml.safe_load(config_file)
            elif config_path.endswith('.json'):
                config = json.load(config_file, object_pairs_hook=OrderedDict)
            else:
                raise ValueError("Unsupported configuration format.")
            
            if 'MediLink_Config' not in config:
                raise KeyError("MediLink_Config key is missing from the loaded configuration.")

        with open(crosswalk_path, 'r') as crosswalk_file:
            crosswalk = json.load(crosswalk_file)

        return config, crosswalk
    except ValueError as e:
        if isinstance(e, UnicodeDecodeError):
            print("Error decoding file: {}".format(e))
        else:
            print("Error parsing file: {}".format(e))
        sys.exit(1)  # Exit the script due to a critical error in configuration loading
    except FileNotFoundError:
        print("One or both configuration files not found. Config: {}, Crosswalk: {}".format(config_path, crosswalk_path))
        sys.exit(1)  # Exit the script due to a critical error in configuration loading
    except KeyError as e:
        print("Critical configuration is missing: {}".format(e))
        sys.exit(1)  # Exit the script due to a critical error in configuration loading
    except Exception as e:
        print("An unexpected error occurred while loading the configuration: {}".format(e))
        sys.exit(1)  # Exit the script due to a critical error in configuration loading
        
# Logs messages with optional error type and claim data.
def log(message, config=None, level="INFO", error_type=None, claim=None, verbose=False):
    
    # If config is not provided, load it
    if config is None:
        config, _ = load_configuration()
    
    # Setup logger if not already configured
    if not logging.root.handlers:
        local_storage_path = config['MediLink_Config'].get('local_storage_path', '.') if isinstance(config, dict) else '.'
        log_filename = datetime.now().strftime("Log_%m%d%Y.log")
        log_filepath = os.path.join(local_storage_path, log_filename)
        
        # Set logging level based on verbosity
        logging_level = logging.DEBUG if verbose else logging.INFO
        
        logging.basicConfig(level=logging_level,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            filename=log_filepath,
                            filemode='a')
    
    # Prepare log message
    claim_data = " - Claim Data: {}".format(claim) if claim else ""
    error_info = " - Error Type: {}".format(error_type) if error_type else ""
    full_message = "{} {}{}".format(message, claim_data, error_info)

    # Log the message
    logger = logging.getLogger()
    getattr(logger, level.lower())(full_message)