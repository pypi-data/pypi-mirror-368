import json
import unittest
from unittest.mock import patch
import urllib3

from aihub.api.jobs_api import JobsApi


class TestJobsApi(unittest.TestCase):
  """JobsApi unit test stubs"""

  def setUp(self) -> None:
    self.api = JobsApi()

  def tearDown(self) -> None:
    pass

  @patch.object(urllib3.PoolManager, 'request')
  def test_status(self, mock_request) -> None:
    """Test case for status

        Poll the status of asynchronous jobs.
        """
    job_id = "abc123"
    expected_response = {
        "state": "COMPLETE",
        "message": "Job completed successfully"
    }

    # Mock the HTTP GET request response
    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.job_status(job_id)
    mock_request.assert_called_once()

    # Assert
    self.assertEqual(response.state, expected_response['state'])
    self.assertEqual(response.message, expected_response['message'])
