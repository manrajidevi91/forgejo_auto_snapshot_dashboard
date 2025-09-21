
import unittest
from unittest.mock import patch, Mock
from services.forgejo_api import ForgejoAPI

class TestForgejoAPI(unittest.TestCase):

    @patch('requests.get')
    def test_connection_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "1.21.0"}
        mock_get.return_value = mock_response

        api = ForgejoAPI(base_url="http://fake-forgejo.com", token="fake_token")
        success, data = api.test_connection()

        self.assertTrue(success)
        self.assertEqual(data['version'], "1.21.0")

if __name__ == '__main__':
    unittest.main()
