import keyring
from utils.logger import app_logger as logger

# The service name we'll use to store the credential in Windows Credential Manager
SERVICE_NAME = "ForgejoAutoSnapshotDashboard"

class CredentialsService:
    def save_token(self, username, token):
        """
        Saves a token securely in the system's credential manager.
        
        :param username: The username associated with the token (e.g., your Forgejo username).
        :param token: The Personal Access Token to save.
        """
        try:
            keyring.set_password(SERVICE_NAME, username, token)
            logger.info(f"Successfully saved token for user '{username}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to save token for user '{username}': {e}")
            return False

    def get_token(self, username):
        """
        Retrieves a token from the system's credential manager.
        
        :param username: The username whose token you want to retrieve.
        :return: The token if found, otherwise None.
        """
        try:
            token = keyring.get_password(SERVICE_NAME, username)
            if token:
                logger.info(f"Successfully retrieved token for user '{username}'.")
                return token
            else:
                logger.warning(f"No token found for user '{username}'.")
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve token for user '{username}': {e}")
            return None

    def delete_token(self, username):
        """
        Deletes a token from the system's credential manager.
        
        :param username: The username whose token you want to delete.
        """
        try:
            keyring.delete_password(SERVICE_NAME, username)
            logger.info(f"Successfully deleted token for user '{username}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete token for user '{username}': {e}")
            return False

# Singleton instance
credentials_service = CredentialsService()