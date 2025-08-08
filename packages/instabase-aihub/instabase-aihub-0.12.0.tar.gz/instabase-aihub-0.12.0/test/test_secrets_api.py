import json
import unittest
from unittest.mock import patch
import urllib3

from aihub.api.secrets_api import SecretsApi


class TestSecretsApi(unittest.TestCase):
  """SecretsApi unit test stubs"""

  def setUp(self) -> None:
    self.api = SecretsApi()

  def tearDown(self) -> None:
    pass

  @patch.object(urllib3.PoolManager, 'request')
  def test_update_secret(self, mock_request) -> None:
    """Test case for update_secret

        Update an existing secret
        """
    expected_response = {}

    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.update_secret(
        update_secret_request={
            'alias': 'my_secret',
            'value': 'new_password',
            'description': 'Updated secret description',
            'allowed_workspaces_type': 'ALL'
        })
    self.assertIsNone(response, 'Response should be None for update request')

  @patch.object(urllib3.PoolManager, 'request')
  def test_update_secret_with_specific_workspaces(self, mock_request) -> None:
    """Test case for update_secret with specific workspace permissions"""
    expected_response = {}

    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.update_secret(
        update_secret_request={
            'alias': 'my_secret',
            'value': 'new_password',
            'description': 'Limited access secret',
            'allowed_workspaces_type': 'SOME',
            'allowed_workspaces': ['workspace1', 'workspace2']
        })
    self.assertIsNone(response, 'response should be none for update')

  @patch.object(urllib3.PoolManager, 'request')
  def test_delete_secret(self, mock_request) -> None:
    """Test case for delete_secret

        Delete a secret
        """
    expected_response = {}

    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.delete_secret(
        delete_secret_request={'alias': 'my_secret'})
    self.assertIsNone(response, 'response for delete should be none')

  @patch.object(urllib3.PoolManager, 'request')
  def test_list_secrets(self, mock_request) -> None:
    """Test case for list_secrets

        List all secrets
        """
    expected_response = {
        "secrets": [{
            "alias": "my_secret",
            "description": "Test secret",
            "allowed_workspaces_type": "ALL",
            "allowed_workspaces": [],
            "created_at": 1740787483000,
            "updated_at": 1740787483000
        }, {
            "alias": "limited_secret",
            "description": "Limited access secret",
            "allowed_workspaces_type": "SOME",
            "allowed_workspaces": ["workspace1"],
            "created_at": 1737584389000,
            "updated_at": 1737584389000
        }]
    }

    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.list_secrets()
    self.assertEqual(len(response.secrets), 2)
    self.assertEqual(response.secrets[0].alias, "my_secret")
    self.assertEqual(response.secrets[0].allowed_workspaces_type, "ALL")
    self.assertEqual(response.secrets[1].alias, "limited_secret")
    self.assertEqual(response.secrets[1].allowed_workspaces_type, "SOME")
    self.assertEqual(len(response.secrets[1].allowed_workspaces), 1)

  @patch.object(urllib3.PoolManager, 'request')
  def test_get_secret(self, mock_request) -> None:
    """Test case for get_secret

        Get a specific secret's metadata
        """
    expected_response = {
        "secrets": [{
            "alias": "my_secret",
            "description": "Test secret",
            "allowed_workspaces_type": "ALL",
            "allowed_workspaces": [],
            "created_at": 1740787483000,
            "updated_at": 1740787483000
        }]
    }

    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.list_secrets(alias='my_secret')
    secret = response.secrets[0]
    self.assertEqual(secret.alias, "my_secret")
    self.assertEqual(secret.description, "Test secret")
    self.assertEqual(secret.allowed_workspaces_type, "ALL")
    self.assertEqual(len(secret.allowed_workspaces), 0)


if __name__ == '__main__':
  unittest.main()
