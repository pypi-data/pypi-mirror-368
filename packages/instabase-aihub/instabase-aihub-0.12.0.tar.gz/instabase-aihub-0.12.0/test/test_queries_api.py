import json
import unittest
from unittest.mock import patch, MagicMock
import urllib3

from aihub.api.queries_api import QueriesApi


class TestQueryApi(unittest.TestCase):
  """QueryApi unit test stubs"""

  def setUp(self) -> None:
    self.api = QueriesApi()
    self.chatbot_id = "123"
    self.converse_id = "321"
    self.query = "What is the main topic?"
    self.query_id = "abc123"

  def tearDown(self) -> None:
    pass

  @patch.object(urllib3.PoolManager, 'request')
  def test_run_query(self, mock_request: MagicMock) -> None:
    """Test case for run query

       Run a query for a chatbot.
        """
    expected_response = {"query_id": self.query_id}

    # Mock the HTTP POST request response
    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=202)
    mock_request.return_value = mock_response

    # Act
    payload = {
        'query': self.query,
        'source_app': {
            'type': 'CHATBOT',
            'id': self.chatbot_id
        }
    }
    response = self.api.run_query(payload)

    # Assert
    actual_method = mock_request.call_args[0][0]
    self.assertEqual(actual_method, 'POST')

    # Verify that the response is correctly interpreted
    self.assertEqual(response.query_id, expected_response["query_id"])

  @patch.object(urllib3.PoolManager, 'request')
  def test_run_query_converse(self, mock_request: MagicMock) -> None:
    """Test case for run query

       Run a query for a converse.
        """
    expected_response = {"query_id": self.query_id}

    # Mock the HTTP POST request response
    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=202)
    mock_request.return_value = mock_response

    # Act
    payload = {
        'query': self.query,
        'source_app': {
            'type': 'CONVERSE',
            'id': self.converse_id
        }
    }
    response = self.api.run_query(payload)

    # Assert
    actual_method = mock_request.call_args[0][0]
    self.assertEqual(actual_method, 'POST')

    # Verify that the response is correctly interpreted
    self.assertEqual(response.query_id, expected_response["query_id"])

  @patch.object(urllib3.PoolManager, 'request')
  def test_get_query_status(self, mock_request: MagicMock) -> None:
    """
        Test case for get query response

        Get the response for a query.
        """

    expected_query_response = {
        'query_id':
        self.query_id,
        'status':
        'COMPLETE',
        'results': [{
            'response': 'The main topic is AI',
            'source_documents': [{
                'name': 'document',
                'pages': []
            }]
        }]
    }
    # Mock the HTTP POST request response
    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_query_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response
    response = self.api.get_query_status(self.query_id)

    # Assert
    actual_method, actual_url = mock_request.call_args[0][
        0], mock_request.call_args[0][1]
    self.assertEqual(actual_method, 'GET')
    self.assertIn(self.query_id,
                  actual_url)  # Ensure the query_id is part of the URL path

    # Verify that the response is correctly interpreted
    self.assertEqual(response.query_id, expected_query_response["query_id"])
    self.assertEqual(response.status, expected_query_response["status"])
    self.assertEqual(
        len(response.results), len(expected_query_response["results"]))
    self.assertIsNone(response.error)
