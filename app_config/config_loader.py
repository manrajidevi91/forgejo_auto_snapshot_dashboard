import os
import json
from dotenv import load_dotenv
from jsonschema import validate, ValidationError
from utils.paths import get_project_schema_file, get_app_root_dir

class ConfigLoader:
    _instance = None
    _app_config = None
    _project_schema = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._load_configs()
        return cls._instance

    def _load_configs(self):
        # Load .env file from the application root
        dotenv_path = os.path.join(get_app_root_dir(), '.env')
        load_dotenv(dotenv_path=dotenv_path)

        # Load project configuration schema
        with open(get_project_schema_file(), 'r') as f:
            self.__class__._project_schema = json.load(f)

        # Store environment variables in the app_config dictionary
        self.__class__._app_config = {}
        self.__class__._app_config['FLASK_DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        # Add other config variables as needed
        self.__class__._app_config['FORGEJO_URL'] = os.getenv('FORGEJO_URL')
        self.__class__._app_config['FORGEJO_API_TOKEN'] = os.getenv('FORGEJO_API_TOKEN')


    def get_app_config(self):
        return self.__class__._app_config

    def validate_project_config(self, project_config):
        try:
            validate(instance=project_config, schema=self.__class__._project_schema)
            return True
        except ValidationError as e:
            print(f"Project configuration validation error: {e.message}")
            return False

# Initialize the config loader
config_loader = ConfigLoader()
