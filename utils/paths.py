import os
import sys

def get_base_dir():
    """
    Returns the base directory of the application.
    This handles both running as a script and as a PyInstaller executable.
    """
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        return os.path.dirname(sys.executable)
    else:
        # Running as a script
        return os.path.dirname(os.path.abspath(__file__))

def get_app_root_dir():
    """
    Returns the root directory of the Forgejo Auto-Snapshot Dashboard application.
    This is typically one level up from the 'utils' directory.
    """
    base_dir = get_base_dir()
    # Assuming 'utils' is directly under the app root
    return os.path.abspath(os.path.join(base_dir, '..'))

def get_config_dir():
    """Returns the path to the app_config directory."""
    return os.path.join(get_app_root_dir(), 'app_config')

def get_data_dir():
    """Returns the path to the data directory."""
    return os.path.join(get_app_root_dir(), 'data')

def get_logs_dir():
    """Returns the path to the logs directory."""
    return os.path.join(get_app_root_dir(), 'logs')

def get_templates_dir():
    """Returns the path to the templates directory."""
    return os.path.join(get_app_root_dir(), 'templates')

def get_static_dir():
    """Returns the path to the static directory."""
    return os.path.join(get_app_root_dir(), 'static')

def get_scripts_dir():
    """Returns the path to the scripts directory."""
    return os.path.join(get_app_root_dir(), 'scripts')

def get_app_config_file():
    """Returns the path to the default application configuration file."""
    return os.path.join(get_config_dir(), 'defaults.json')

def get_app_schema_file():
    """Returns the path to the application configuration schema file."""
    return os.path.join(get_config_dir(), 'schemas', 'app_config.schema.json')

def get_project_schema_file():
    """Returns the path to the project configuration schema file."""
    return os.path.join(get_config_dir(), 'schemas', 'project_config.schema.json')

def get_projects_data_file():
    """Returns the path to the projects data file."""
    return os.path.join(get_data_dir(), 'projects.json')

def get_retention_policy_file():
    """Returns the path to the retention policy file."""
    return os.path.join(get_data_dir(), 'retention', 'policy.json')

def get_log_file():
    """Returns the path to the main application log file."""
    return os.path.join(get_logs_dir(), 'app.log')

def get_gitignore_template_dir():
    """Returns the path to the .gitignore templates directory."""
    return os.path.join(get_config_dir(), 'templates')

# Example usage (for testing purposes)
if __name__ == "__main__":
    print(f"Base Directory: {get_base_dir()}")
    print(f"App Root Directory: {get_app_root_dir()}")
    print(f"Config Directory: {get_config_dir()}")
    print(f"Data Directory: {get_data_dir()}")
    print(f"Logs Directory: {get_logs_dir()}")
    print(f"Templates Directory: {get_templates_dir()}")
    print(f"Static Directory: {get_static_dir()}")
    print(f"Scripts Directory: {get_scripts_dir()}")
    print(f"App Config File: {get_app_config_file()}")
    print(f"App Schema File: {get_app_schema_file()}")
    print(f"Project Schema File: {get_project_schema_file()}")
    print(f"Projects Data File: {get_projects_data_file()}")
    print(f"Retention Policy File: {get_retention_policy_file()}")
    print(f"Log File: {get_log_file()}")
    print(f"Gitignore Template Directory: {get_gitignore_template_dir()}")