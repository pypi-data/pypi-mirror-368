# core_utils.py
"""
Core utilities module for MediCafe
This module contains shared functionality between MediBot and MediLink modules
to break circular import dependencies.
"""

import os, sys

# Ensure proper path setup for imports
# Get the project root directory (parent of MediCafe directory)
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
medilink_dir = os.path.join(project_dir, 'MediLink')
medibot_dir = os.path.join(project_dir, 'MediBot')

# Add paths in order of priority - project root first, then module directories
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)
if medilink_dir not in sys.path:
    sys.path.insert(0, medilink_dir)
if medibot_dir not in sys.path:
    sys.path.insert(0, medibot_dir)

# Common constants and configurations
DEFAULT_CONFIG_PATH = os.path.join(project_dir, 'json', 'config.json')
DEFAULT_CROSSWALK_PATH = os.path.join(project_dir, 'json', 'crosswalk.json')

def setup_project_path(file_path=None):
    """
    Standard project path setup function used by all entry points.
    
    Args:
        file_path: The __file__ of the calling module. If None, uses this file's directory.
    
    Returns:
        The project directory path.
    """
    if file_path is None:
        file_path = __file__
    
    project_dir = os.path.abspath(os.path.join(os.path.dirname(file_path), ".."))
    current_dir = os.path.abspath(os.path.dirname(file_path))
    
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    return project_dir

def setup_module_paths(file_path):
    """
    Enhanced path setup for individual modules.
    Sets up both project root and module directory paths.
    
    Args:
        file_path: The __file__ of the calling module
    
    Returns:
        Tuple of (project_dir, current_dir)
    """
    project_dir = os.path.abspath(os.path.join(os.path.dirname(file_path), ".."))
    current_dir = os.path.abspath(os.path.dirname(file_path))
    
    # Add paths in order of priority
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    return project_dir, current_dir

def safe_import_with_fallback(primary_import_path, fallback_import_path=None, function_name=None):
    """
    Safely import a module or function with fallback options.
    
    Args:
        primary_import_path (str): Primary import path to try
        fallback_import_path (str): Fallback import path if primary fails
        function_name (str): Specific function name to extract from module
    
    Returns:
        The imported module or function, or None if all imports fail
    """
    try:
        if function_name:
            module = __import__(primary_import_path, fromlist=[function_name])
            return getattr(module, function_name)
        else:
            return __import__(primary_import_path)
    except ImportError:
        if fallback_import_path:
            try:
                if function_name:
                    module = __import__(fallback_import_path, fromlist=[function_name])
                    return getattr(module, function_name)
                else:
                    return __import__(fallback_import_path)
            except ImportError:
                return None
        return None

def smart_import(import_specs, default_value=None):
    """
    Enhanced import function that tries multiple import strategies intelligently.
    
    Args:
        import_specs (list): List of import specifications. Each can be:
            - String: Direct import path
            - Tuple: (import_path, function_name)
            - Dict: {'path': import_path, 'function': function_name, 'fallback': fallback_path}
        default_value: Value to return if all imports fail
    
    Returns:
        The imported module/function or default_value
    """
    for spec in import_specs:
        try:
            if isinstance(spec, str):
                # Simple string - direct import
                return __import__(spec)
            elif isinstance(spec, tuple):
                # Tuple - (path, function_name)
                path, function_name = spec
                module = __import__(path, fromlist=[function_name])
                return getattr(module, function_name)
            elif isinstance(spec, dict):
                # Dict with fallback
                path = spec['path']
                function_name = spec.get('function')
                fallback = spec.get('fallback')
                
                try:
                    if function_name:
                        module = __import__(path, fromlist=[function_name])
                        return getattr(module, function_name)
                    else:
                        return __import__(path)
                except ImportError:
                    if fallback:
                        try:
                            if function_name:
                                module = __import__(fallback, fromlist=[function_name])
                                return getattr(module, function_name)
                            else:
                                return __import__(fallback)
                        except ImportError:
                            continue
                    continue
        except ImportError:
            continue
    
    return default_value

def import_medibot_module(module_name, function_name=None):
    """
    Centralized function to import MediBot modules with intelligent fallbacks.
    
    Args:
        module_name (str): Name of the MediBot module (e.g., 'MediBot_dataformat_library')
        function_name (str): Specific function to extract (optional)
    
    Returns:
        The imported module/function or None
    """
    import_specs = [
        # Direct import first
        module_name,
        # Then try with MediBot prefix
        'MediBot.{}'.format(module_name),
        # Then try relative import
        '.{}'.format(module_name),
        # Finally try as a submodule
        {'path': 'MediBot.{}'.format(module_name), 'fallback': module_name}
    ]
    
    if function_name:
        # If we need a specific function, modify specs to extract it
        function_specs = []
        for spec in import_specs:
            if isinstance(spec, str):
                function_specs.append((spec, function_name))
            elif isinstance(spec, dict):
                function_specs.append({
                    'path': spec['path'],
                    'function': function_name,
                    'fallback': spec.get('fallback')
                })
        return smart_import(function_specs)
    else:
        return smart_import(import_specs)

def import_medibot_module_with_debug(module_name, function_name=None):
    """
    Enhanced version of import_medibot_module with debugging information.
    
    Args:
        module_name (str): Name of the MediBot module
        function_name (str): Specific function to extract (optional)
    
    Returns:
        The imported module/function or None
    """
    # Try the standard import first
    result = import_medibot_module(module_name, function_name)
    if result is not None:
        return result
    
    # If that fails, try additional strategies with debugging
    additional_specs = [
        # Try as a direct file import
        '{}.py'.format(module_name),
        # Try with full path resolution
        'MediBot.{}.py'.format(module_name),
        # Try importing from current directory
        './{}'.format(module_name),
        # Try importing from parent directory
        '../{}'.format(module_name)
    ]
    
    for spec in additional_specs:
        try:
            if function_name:
                module = __import__(spec, fromlist=[function_name])
                return getattr(module, function_name)
            else:
                return __import__(spec)
        except ImportError:
            continue
    
    # If all else fails, log the failure
    config_loader = get_shared_config_loader()
    if config_loader:
        config_loader.log("Failed to import MediBot module: {}".format(module_name), level="WARNING")
    else:
        print("[WARNING] Failed to import MediBot module: {}".format(module_name))
    
    return None

def import_medilink_module(module_name, function_name=None):
    """
    Centralized function to import MediLink modules with intelligent fallbacks.
    
    Args:
        module_name (str): Name of the MediLink module
        function_name (str): Specific function to extract (optional)
    
    Returns:
        The imported module/function or None
    """
    import_specs = [
        # Direct import first
        module_name,
        # Then try with MediLink prefix
        'MediLink.{}'.format(module_name),
        # Then try relative import
        '.{}'.format(module_name),
        # Finally try as a submodule
        {'path': 'MediLink.{}'.format(module_name), 'fallback': module_name}
    ]
    
    if function_name:
        # If we need a specific function, modify specs to extract it
        function_specs = []
        for spec in import_specs:
            if isinstance(spec, str):
                function_specs.append((spec, function_name))
            elif isinstance(spec, dict):
                function_specs.append({
                    'path': spec['path'],
                    'function': function_name,
                    'fallback': spec.get('fallback')
                })
        return smart_import(function_specs)
    else:
        return smart_import(import_specs)

def get_shared_config_loader():
    """
    Returns the MediLink_ConfigLoader module using safe import patterns.
    This is used by both MediBot and MediLink modules.
    """
    # Try multiple import strategies - now including the new MediCafe location
    try:
        # First try to import directly from MediCafe package
        from MediCafe import MediLink_ConfigLoader
        return MediLink_ConfigLoader
    except ImportError:
        try:
            # Try direct import from MediCafe directory
            import MediLink_ConfigLoader
            return MediLink_ConfigLoader
        except ImportError:
            try:
                # Try relative import from current directory
                from . import MediLink_ConfigLoader
                return MediLink_ConfigLoader
            except ImportError:
                return None

def create_fallback_logger():
    """
    Creates a minimal fallback logger when MediLink_ConfigLoader is unavailable.
    
    Returns:
        A simple logger object with a log method
    """
    class FallbackLogger:
        def log(self, message, level="INFO"):
            print("[{}] {}".format(level, message))
    
    return FallbackLogger()

def get_config_loader_with_fallback():
    """
    Get MediLink_ConfigLoader with automatic fallback to simple logger.
    
    Returns:
        MediLink_ConfigLoader or FallbackLogger
    """
    config_loader = get_shared_config_loader()
    if config_loader is None:
        return create_fallback_logger()
    return config_loader

def log_import_error(module_name, error, level="WARNING"):
    """
    Centralized logging for import errors.
    
    Args:
        module_name (str): Name of the module that failed to import
        error (Exception): The import error that occurred
        level (str): Log level (WARNING, ERROR, etc.)
    """
    config_loader = get_shared_config_loader()
    if config_loader and hasattr(config_loader, 'log'):
        config_loader.log("Failed to import {}: {}".format(module_name, error), level=level)
    else:
        print("[{}] Failed to import {}: {}".format(level, module_name, error))

def create_config_cache():
    """
    Creates a lazy configuration loading pattern for modules.
    Returns a tuple of (get_config_function, cache_variables).
    
    Usage:
        _get_config, (_config_cache, _crosswalk_cache) = create_config_cache()
        
        # Later in functions:
        config, crosswalk = _get_config()
    """
    _config_cache = None
    _crosswalk_cache = None
    
    def _get_config():
        nonlocal _config_cache, _crosswalk_cache
        if _config_cache is None:
            config_loader = get_shared_config_loader()
            if config_loader:
                _config_cache, _crosswalk_cache = config_loader.load_configuration()
            else:
                _config_cache, _crosswalk_cache = {}, {}
        return _config_cache, _crosswalk_cache
    
    return _get_config, (_config_cache, _crosswalk_cache)

# Common import patterns used throughout the codebase
def import_with_alternatives(import_specs):
    """
    Import a module using multiple alternative paths.
    
    Args:
        import_specs (list): List of tuples containing (import_path, function_name_or_None)
    
    Returns:
        The first successfully imported module or function
    """
    for import_path, function_name in import_specs:
        result = safe_import_with_fallback(import_path, function_name=function_name)
        if result is not None:
            return result
    return None

# API Client Factory Integration
def get_api_client_factory():
    """
    Get configured API client factory using shared configuration.
    
    Returns:
        APIClientFactory: Configured factory instance or None if unavailable
    """
    # Try multiple import paths for factory
    import_specs = [
        ('MediCafe.api_factory', 'APIClientFactory'),
        ('MediLink.MediLink_API_Factory', 'APIClientFactory'),  # Legacy fallback
        ('MediLink_API_Factory', 'APIClientFactory')  # Legacy fallback
    ]
    
    APIClientFactory = import_with_alternatives(import_specs)
    if not APIClientFactory:
        log_import_error('MediCafe.api_factory', Exception("All import paths failed"))
        return None
    
    try:
        config_loader = get_shared_config_loader()
        if config_loader:
            try:
                config, _ = config_loader.load_configuration()
                factory_config = config.get('API_Factory_Config', {})
                return APIClientFactory(factory_config)
            except Exception:
                # Fall back to default configuration
                return APIClientFactory()
        else:
            return APIClientFactory()
    except Exception as e:
        # Don't log error here - just return None silently
        return None

def get_api_client(**kwargs):
    """
    Convenience function to get API client directly.
    
    Args:
        **kwargs: Additional parameters
        
    Returns:
        APIClient: v3 API client instance or None if unavailable
    """
    factory = get_api_client_factory()
    if factory:
        return factory.get_client(**kwargs)
    return None

def get_api_core_client(**kwargs):
    """
    Get API client from MediCafe core API module.
    
    Args:
        **kwargs: Additional parameters
        
    Returns:
        APIClient: Core API client instance or None if unavailable
    """
    try:
        from MediCafe.api_core import APIClient
        return APIClient(**kwargs)
    except ImportError:
        # Don't log error here - just return None silently
        return None