import json
import unittest
from unittest.mock import patch, mock_open
import urllib3

from aihub.api.conversations_api import ConversationsApi


class TestConversationsApi(unittest.TestCase):
  """ConversationsApi unit test stubs"""

  def setUp(self) -> None:
    self.api = ConversationsApi()

  def tearDown(self) -> None:
    pass

  @patch(
      'builtins.open', new_callable=mock_open, read_data='DUMMY FILE CONTENT')
  @patch.object(urllib3.PoolManager, 'request')
  def test_add_documents_to_conversation(self, mock_request,
                                         mock_file_open) -> None:
    """Test case for add_documents_to_conversation

        Upload documents to a specified conversation.
        """
    conversation_id = "123"
    files = ['doc1.pdf', 'doc2.pdf']  # Simulating file names
    expected_response = {
        "upload_status": {
            "success": [{
                "name": "doc1.pdf"
            }],
            "failure": [{
                "name": "doc2.pdf",
                "reason": "File too large"
            }]
        }
    }
    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=201)
    mock_request.return_value = mock_response

    response = self.api.add_documents_to_conversation(conversation_id, files)
    self.assertEqual(len(response.upload_status.success), 1)
    self.assertEqual(len(response.upload_status.failure), 1)

  @patch.object(urllib3.PoolManager, 'request')
  def test_converse(self, mock_request) -> None:
    """Test case for converse

        Converse with the documents in a conversation.
        """
    conversation_id = "123"
    question = "What is the main topic?"
    document_ids = [
        1, 2
    ]  # Assuming these are IDs of documents in the conversation
    expected_response = {
        "prompt_id": "abc123",
        "answer": "The main topic is machine learning."
    }

    # Mock the HTTP POST request response
    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    # Act
    response = self.api.converse(conversation_id, {
        'question': question,
        'document_ids': document_ids,
        'mode': 'default'
    })

    # Assert
    actual_method, actual_url = mock_request.call_args[0][
        0], mock_request.call_args[0][1]
    self.assertEqual(actual_method, 'POST')
    self.assertIn(
        conversation_id,
        actual_url)  # Ensure the conversation_id is part of the URL path

    # Verify that the response is correctly interpreted
    self.assertEqual(response.prompt_id, expected_response["prompt_id"])
    self.assertEqual(response.answer, expected_response["answer"])

    response = self.api.converse(conversation_id, {
        'question': question,
        'document_ids': document_ids,
        'mode': 'advanced'
    })

    # Assert
    actual_method, actual_url = mock_request.call_args[0][
        0], mock_request.call_args[0][1]
    self.assertEqual(actual_method, 'POST')
    self.assertIn(
        conversation_id,
        actual_url)  # Ensure the conversation_id is part of the URL path

    # Verify that the response is correctly interpreted
    self.assertEqual(response.prompt_id, expected_response["prompt_id"])
    self.assertEqual(response.answer, expected_response["answer"])

  @patch.object(urllib3.PoolManager, 'request')
  def test_converse_with_fast_mode(self, mock_request) -> None:
    """Test case for converse with fast mode"""
    conversation_id = "123"
    question = "What is the main topic?"
    document_ids = [1, 2]
    expected_response = {
        "prompt_id": "abc123",
        "answer": "The main topic is machine learning."
    }
    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.converse(
        conversation_id, {
            'question': question,
            'document_ids': document_ids,
            'mode': 'default',
            'fast_mode': True
        })
    self.assertEqual(response.prompt_id, expected_response["prompt_id"])
    self.assertEqual(response.answer, expected_response["answer"])

  @patch('builtins.open', new_callable=mock_open, read_data='FILE CONTENT')
  @patch.object(urllib3.PoolManager, 'request')
  def test_create_conversation(self, mock_request, mock_file_open) -> None:
    """Test case for create_conversation

        Create a new conversation and upload files.
        """
    expected_response = {
        "id": "123",
        "name": "Test Conversation",
        "upload_status": {
            "success": [{
                "name": "file1.txt"
            }],
            "failure": []
        }
    }
    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=201)
    mock_request.return_value = mock_response

    response = self.api.create_conversation(
        name="Test Conversation", files=["file1.txt"])
    self.assertEqual(response.id, expected_response["id"])
    self.assertEqual(response.name, expected_response["name"])
    self.assertTrue(len(response.upload_status.success) > 0)

  @patch('builtins.open', new_callable=mock_open, read_data='FILE CONTENT')
  @patch.object(urllib3.PoolManager, 'request')
  def test_create_conversation_with_settings(self, mock_request,
                                             mock_file_open) -> None:
    """Test case for create_conversation

        Create a new conversation and upload files.
        """
    expected_response = {
        "id": "123",
        "name": "Test Conversation",
        "upload_status": {
            "success": [{
                "name": "file1.txt"
            }],
            "failure": []
        }
    }
    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=201)
    mock_request.return_value = mock_response

    response = self.api.create_conversation(
        name="Test Conversation",
        files=["file1.txt"],
        enable_multilanguage_support=True,
        enable_multilanguage_advanced_mode=False)
    self.assertEqual(response.id, expected_response["id"])
    self.assertEqual(response.name, expected_response["name"])
    self.assertTrue(len(response.upload_status.success) > 0)

  @patch('builtins.open', new_callable=mock_open, read_data='FILE CONTENT')
  @patch.object(urllib3.PoolManager, 'request')
  def test_create_conversation_with_fast_mode(self, mock_request,
                                              mock_file_open) -> None:
    """Test case for create_conversation with fast mode"""
    expected_response = {
        "id": "123",
        "name": "Test Conversation",
        "upload_status": {
            "success": [{
                "name": "file1.txt"
            }],
            "failure": []
        }
    }
    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=201)
    mock_request.return_value = mock_response

    response = self.api.create_conversation(
        name="Test Conversation",
        files=["file1.txt"],
        fast_mode=True,
        enable_entity_detection=False,
        write_converted_image=False,
        write_thumbnail=False)
    self.assertEqual(response.id, expected_response["id"])
    self.assertEqual(response.name, expected_response["name"])
    self.assertTrue(len(response.upload_status.success) > 0)

  @patch.object(urllib3.PoolManager, 'request')
  def test_delete_documents_from_conversation(self, mock_request) -> None:
    """Test case for delete_documents_from_conversation

        Deletes specified documents from a conversation.
        """
    conversation_id = "123"
    document_ids = [456, 789]

    # Mock the HTTP DELETE request response
    mock_response = urllib3.HTTPResponse(body=b' ', status=204)
    mock_request.return_value = mock_response

    self.api.delete_documents_from_conversation(
        conversation_id, ids=document_ids)
    mock_request.assert_called_once()

  @patch.object(urllib3.PoolManager, 'request')
  def test_get_conversation(self, mock_request) -> None:
    """Test case for get_conversation

        Get the details of the conversation.
        """
    conversation_id = "123"
    expected_response = {
        "id":
        "123",
        "name":
        "Test Conversation",
        "description":
        "",
        "state":
        "COMPLETE",
        "documents": [{
            "id": 456,
            "name": "file1.txt",
            "state": "PROCESSED",
            "uploadTimestamp": None
        }],
    }
    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.get_conversation(conversation_id)
    self.assertEqual(response.id, expected_response["id"])

  @patch.object(urllib3.PoolManager, 'request')
  def test_get_conversation_document_metadata(self, mock_request) -> None:
    """Test case for get_conversation_document_metadata

        Retrieve metadata for a specified document within a conversation.
        """
    conversation_id = "123"
    document_id = 456
    expected_response = {
        "id": document_id,
        "name": "doc1.pdf",
        "ibdoc_path": "ibuser/my-repo/doc1.pdf",
        "additional_metadata": {}
    }
    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.get_conversation_document_metadata(
        conversation_id, document_id)
    self.assertEqual(response.id, expected_response["id"])
    self.assertEqual(response.name, expected_response["name"])

  @patch.object(urllib3.PoolManager, 'request')
  def test_list_conversations(self, mock_request) -> None:
    """Test case for list_conversations

        List all conversations created.
        """
    expected_response = {
        "conversations": [{
            "id": "123",
            "name": "Test Conversation"
        }]
    }
    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.list_conversations()
    self.assertTrue(len(response.conversations) > 0)
    self.assertEqual(response.conversations[0].id,
                     expected_response["conversations"][0]["id"])

  @patch.object(urllib3.PoolManager, 'request')
  def test_delete_conversation(self, mock_request) -> None:
    """Test case for delete_conversation

        Delete the requested conversation.
        """
    conversation_id = "123"
    mock_response = urllib3.HTTPResponse(body=b' ', status=204)
    mock_request.return_value = mock_response

    response = self.api.delete_conversation(conversation_id)

    # Assert
    self.assertIsNone(response)
    actual_method, actual_url = mock_request.call_args[0][
        0], mock_request.call_args[0][1]
    self.assertEqual(actual_method, 'DELETE')
    self.assertIn(
        conversation_id,
        actual_url)  # Ensure the conversation_id is part of the URL path
    mock_request.assert_called_once()


if __name__ == '__main__':
  unittest.main()
