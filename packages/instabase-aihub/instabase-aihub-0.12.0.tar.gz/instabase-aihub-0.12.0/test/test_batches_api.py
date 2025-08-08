import json
import unittest
from unittest.mock import patch
import urllib3

from aihub.api.batches_api import BatchesApi
from aihub.models.batch import Batch


class TestBatchesApi(unittest.TestCase):
    """BatchesApi unit test stubs"""

    def setUp(self) -> None:
        self.api = BatchesApi()

    def tearDown(self) -> None:
        pass

    @patch.object(urllib3.PoolManager, 'request')
    def test_add_file_to_batch(self, mock_request) -> None:
        """Test case for add_file_to_batch

        Upload a file to the batch.
        """
        batch_id = 10
        filename = 'file.txt'
        file_content = b'File content'

        # Mock the HTTP PUT request response
        mock_response = urllib3.HTTPResponse(body=b' ', status=204)
        mock_request.return_value = mock_response

        # Act
        self.api.add_file_to_batch(batch_id, filename, file_content)
        mock_request.assert_called_once()


    @patch.object(urllib3.PoolManager, 'request')
    def test_list_files(self, mock_request) -> None:
        """Test case for list_files

        List files in a batch.
        """
        batch_id = 10
        expected_response = {"nodes": [{"name": "file.txt", "size": 100, "type": "file"}]}

        # Mock the HTTP GET request response
        mock_response = urllib3.HTTPResponse(
            body=bytes(json.dumps(expected_response), 'utf-8'),
            status=200
        )
        mock_request.return_value = mock_response

        # Act
        response = self.api.list_files(batch_id)
        mock_request.assert_called_once()

        # Assert
        self.assertEqual(response.nodes[0].name, expected_response['nodes'][0]['name'])
        self.assertEqual(1, len(response.nodes))

    @patch.object(urllib3.PoolManager, 'request')
    def test_create_batch(self, mock_request) -> None:
        """Test case for create_batch

        Create a new batch.
        """
        expected_response = {"id": 10}

        # Mock the HTTP POST request response
        mock_response = urllib3.HTTPResponse(
            body=bytes(json.dumps(expected_response), 'utf-8'),
            status=200
        )
        mock_request.return_value = mock_response

        # Act
        response = self.api.create_batch({ "name": "test batch" })
        mock_request.assert_called_once()

        # Assert
        self.assertEqual(response.id, expected_response['id'])

    @patch.object(urllib3.PoolManager, 'request')
    def test_delete_batch(self, mock_request) -> None:
        """Test case for delete_batch

        Delete a batch and all of its files.
        """
        batch_id = 10
        expected_response = {"job_id": "AA"}

        # Mock the HTTP DELETE request response
        mock_response = urllib3.HTTPResponse(
            body=bytes(json.dumps(expected_response), 'utf-8'),
            status=202
        )
        mock_request.return_value = mock_response

        # Act
        response = self.api.delete_batch(batch_id)
        mock_request.assert_called_once()

        # Assert
        self.assertEqual(response.job_id, expected_response['job_id'])

    @patch.object(urllib3.PoolManager, 'request')
    def test_delete_file_from_batch(self, mock_request) -> None:
        """Test case for delete_file_from_batch

        Delete a file from a batch.
        """
        batch_id = 10
        filename = 'file.txt'

        # Mock the HTTP DELETE request response
        mock_response = urllib3.HTTPResponse(body=b' ', status=202)
        mock_request.return_value = mock_response

        # Act
        self.api.delete_file_from_batch(batch_id, filename)

        # Inspect the call arguments
        actual_method, actual_url = mock_request.call_args[0][0], mock_request.call_args[0][1]

        # Assert method and URL
        self.assertEqual(actual_method, 'DELETE')
        self.assertEqual(actual_url, f'{self.api.api_client.configuration.host}/v2/batches/{batch_id}/files/{filename}')

    @patch.object(urllib3.PoolManager, 'request')
    def test_get_batch(self, mock_request) -> None:
        """Test case for get_batch

        Retrieve information about a batch.
        """
        batch_id = 10
        expected_response = {"id": 10, "name": "test batch"}

        # Mock the HTTP GET request response
        mock_response = urllib3.HTTPResponse(
            body=bytes(json.dumps(expected_response), 'utf-8'),
            status=200
        )
        mock_request.return_value = mock_response

        # Act
        response = self.api.get_batch(batch_id)
        mock_request.assert_called_once()

        # Assert
        self.assertEqual(response.id, expected_response['id'])
        self.assertEqual(response.name, expected_response['name'])

    @patch.object(urllib3.PoolManager, 'request')
    def test_list_batches(self, mock_request) -> None:
        """Test case for list_batches

        Return a list of batches.
        """
        expected_response = {"batches": [{"id": 10, "name": "test batch"}]}

        # Mock the HTTP GET request response
        mock_response = urllib3.HTTPResponse(
            body=bytes(json.dumps(expected_response), 'utf-8'),
            status=200
        )
        mock_request.return_value = mock_response

        # Act
        response = self.api.list_batches()
        mock_request.assert_called_once()

        # Assert
        self.assertEqual(len(response.batches), 1)
        self.assertEqual(response.batches[0].id, expected_response['batches'][0]['id'])
        self.assertEqual(response.batches[0].name, expected_response['batches'][0]['name'])


    @patch.object(urllib3.PoolManager, 'request')
    def test_poll_batches_job(self, mock_request) -> None:
        """Test case for poll_batches_job

        Poll the status of asynchronous jobs for batches.
        """
        job_id = "abc123"
        expected_response = {"state": "COMPLETE", "message": "Job completed successfully"}

        # Mock the HTTP GET request response
        mock_response = urllib3.HTTPResponse(
            body=bytes(json.dumps(expected_response), 'utf-8'),
            status=200
        )
        mock_request.return_value = mock_response

        # Act
        response = self.api.poll_batches_job(job_id)
        mock_request.assert_called_once()

        # Assert
        self.assertEqual(response.state, expected_response['state'])
        self.assertEqual(response.message, expected_response['message'])


if __name__ == '__main__':
    unittest.main()
