
import requests
from utils.logger import app_logger as logger

class ForgejoAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/') + '/api/v1'
        self.headers = {
            'Authorization': f'token {token}',
            'Content-Type': 'application/json'
        }

    def test_connection(self):
        """Tests the connection to the Forgejo instance."""
        try:
            response = requests.get(f'{self.base_url}/version', headers=self.headers, timeout=5)
            response.raise_for_status()
            logger.info(f"Successfully connected to Forgejo: {response.json().get('version')}")
            return True, response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to connect to Forgejo: {e}")
            return False, str(e)

    def create_repo(self, repo_name, description=""):
        """Creates a new repository on Forgejo."""
        payload = {
            'name': repo_name,
            'description': description,
            'private': True
        }
        try:
            response = requests.post(f'{self.base_url}/user/repos', headers=self.headers, json=payload)
            response.raise_for_status()
            logger.info(f"Successfully created repository '{repo_name}' on Forgejo.")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to create repository on Forgejo: {e.response.text}")
            return None
