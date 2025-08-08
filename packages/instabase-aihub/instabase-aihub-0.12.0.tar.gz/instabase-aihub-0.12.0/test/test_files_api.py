import unittest
from unittest.mock import patch
import urllib3

from aihub.api.files_api import FilesApi


class TestFilesApi(unittest.TestCase):
  """FilesApi unit test stubs"""

  def setUp(self) -> None:
    self.api = FilesApi()

  def tearDown(self) -> None:
    pass

  @patch.object(urllib3.PoolManager, 'request')
  def test_read_file(self, mock_request) -> None:
    """Test case for read_file

        Read file.
        """
    path = 'john.aihub-internal_instabase.com/my-repo/fs/Instabase Drive/files/foo.txt'

    # Mock the HTTP PUT request response
    file_contents = b'test'
    mock_response = urllib3.HTTPResponse(body=file_contents, status=200)
    mock_request.return_value = mock_response

    # Act
    response = self.api.read_file(path, expect_node_type='file')
    mock_request.assert_called_once()
    assert response == file_contents

  @patch.object(urllib3.PoolManager, 'request')
  def test_read_file_partial(self, mock_request) -> None:
    """Test case for read_file

        Read file.
        """
    path = 'john.aihub-internal_instabase.com/my-repo/fs/Instabase Drive/files/foo.txt'

    # Mock the HTTP PUT request response
    file_contents = b'test'
    mock_response = urllib3.HTTPResponse(body=file_contents[0:3], status=206)
    mock_request.return_value = mock_response

    # Act
    response = self.api.read_file(
        path, expect_node_type='file', range='bytes=0-2')
    mock_request.assert_called_once()
    assert response == file_contents[0:3]

  @patch.object(urllib3.PoolManager, 'request')
  def test_write_file(self, mock_request) -> None:
    """Test case for write_file

        Create or overwrite file.
        """
    path = 'john.aihub-internal_instabase.com/my-repo/fs/Instabase Drive/files/foo.txt'
    file_data = b'test data'

    # Mock the HTTP PUT request response
    mock_response = urllib3.HTTPResponse(body=b' ', status=204)
    mock_request.return_value = mock_response

    # Act
    self.api.write_file(path, file_data)
    mock_request.assert_called_once()

  @patch.object(urllib3.PoolManager, 'request')
  def test_get_file_metadata(self, mock_request) -> None:
    """Test case for get_file_metadata

        Read file or folder metadata.
        """
    path = 'john.aihub-internal_instabase.com/my-repo/fs/Instabase Drive/files/foo.txt'

    # Mock the HTTP HEAD request response
    headers = {
        'Content-Type': 'application/octet-stream',
        'Content-Length': '1024',
        'last-modified': 'Wed, 21 Oct 2015 07:28:00 GMT'
    }
    mock_response = urllib3.HTTPResponse(
        body=b' ', status=200, headers=headers)
    mock_request.return_value = mock_response

    # Act
    response = self.api.get_file_metadata_with_http_info(path)
    mock_request.assert_called_once()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == headers['Content-Type']
    assert response.headers['Content-Length'] == headers['Content-Length']
    assert response.headers['last-modified'] == headers['last-modified']

  @patch.object(urllib3.PoolManager, 'request')
  def test_delete_file_or_folder(self, mock_request) -> None:
    """Test case for delete_file_or_folder

        Delete a file or folder.
        """
    path = 'john.aihub-internal_instabase.com/my-repo/fs/Instabase Drive/files/foo.txt'

    # Mock the HTTP DELETE request response
    mock_response = urllib3.HTTPResponse(
        body=b' ', status=202, headers={'Location': 'some/job/status/url'})
    mock_request.return_value = mock_response

    # Act
    self.api.delete_file_or_folder(path)
    mock_request.assert_called_once()
