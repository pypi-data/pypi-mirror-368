import json
import unittest
from unittest.mock import patch
import urllib3

from aihub.api.runs_api import RunsApi


class TestRunsApi(unittest.TestCase):
  """RunsApi unit test stubs"""

  def setUp(self) -> None:
    self.api = RunsApi()

  def tearDown(self) -> None:
    pass

  @patch.object(urllib3.PoolManager, 'request')
  def test_get_run_results(self, mock_request) -> None:
    """Test case for get_run_results

        Retrieve run results
        """
    run_id = "run123"
    expected_response = {
        'has_more':
        False,
        'batch_id':
        '12937',
        'files': [{
            'original_file_name':
            'new_file.txt',
            'input_file_path':
            'test_user/my-repo/fs/Instabase Drive/input/new_file.txt',
            'documents': [{
                'class_name':
                'Other',
                'page_numbers': [1, 2],
                'fields': [{
                    'value':
                    '1234 1234 1234 1234',
                    'type':
                    'TEXT',
                    'confidence': {
                        'model': 0.9998947,
                        'ocr': 0.9998947
                    },
                    'edit_history': [],
                    'source_coordinates': [{
                        'top_x': 393.71,
                        'top_y': 132.91,
                        'bottom_x': 465.15000244140623,
                        'bottom_y': 149.08,
                        'page_number': 0
                    }, {
                        'top_x': 474.6,
                        'top_y': 132.91,
                        'bottom_x': 546.0400024414063,
                        'bottom_y': 149.08,
                        'page_number': 0
                    }, {
                        'top_x': 555.49,
                        'top_y': 132.91,
                        'bottom_x': 626.9300024414063,
                        'bottom_y': 149.08,
                        'page_number': 0
                    }, {
                        'top_x': 636.38,
                        'top_y': 132.91,
                        'bottom_x': 707.8200024414062,
                        'bottom_y': 149.08,
                        'page_number': 0
                    }],
                    'validations':
                    None,
                    'field_name':
                    'account_number'
                }, {
                    'field_name': 'account_number',
                    'value': 'ERROR',
                    'error_msg': 'dummy error message',
                }],
                'post_processed_paths': [
                    'test_user/my-repo/fs/Instabase Drive/app-runs/976bf734-6271-44c3-860d-ea75c0c93f2c/ef0d286a-3da1-4330-b13a-059257b646ea/s1_process_files/images/new_file.txt_p0.jpeg'
                ],
                'review_completed':
                False,
                'class_edit_history': [],
                'validations': {
                    'final_result_pass': None
                },
                'classification_confidence': {
                    'model': 0.9998947
                }
            }]
        }],
        'review_completed':
        False,
        "keys": {
            "custom": {}
        }
    }

    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.get_run_results(run_id)
    self.assertFalse(response.has_more)
    # Assert results file structure
    self.assertEqual(len(response.files), 1)
    self.assertEqual(response.files[0].original_file_name, "new_file.txt")
    self.assertEqual(
        response.files[0].input_file_path,
        "test_user/my-repo/fs/Instabase Drive/input/new_file.txt")
    # Assert document structure
    self.assertEqual(len(response.files[0].documents), 1)
    self.assertEqual(len(response.files[0].documents[0].fields), 2)
    # Assert page numbers
    self.assertEqual(response.files[0].documents[0].page_numbers, [1, 2])
    # Assert field structure
    self.assertEqual(response.files[0].documents[0].fields[0].field_name,
                     "account_number")
    self.assertEqual(response.files[0].documents[0].fields[0].value,
                     "1234 1234 1234 1234")
    self.assertEqual(response.files[0].documents[0].fields[0].type, "TEXT")
    self.assertEqual(response.files[0].documents[0].fields[0].confidence.model,
                     0.9998947)
    self.assertEqual(response.files[0].documents[0].fields[0].confidence.ocr,
                     0.9998947)
    self.assertEqual(
        len(response.files[0].documents[0].fields[0].source_coordinates), 4)
    self.assertEqual(
        len(response.files[0].documents[0].post_processed_paths), 1)
    # Assert other document fields
    self.assertEqual(response.files[0].documents[0].class_name, "Other")
    self.assertEqual(response.files[0].documents[0].review_completed, False)
    self.assertEqual(
        response.files[0].documents[0].validations.final_result_pass, None)
    self.assertEqual(
        response.files[0].documents[0].classification_confidence.model,
        0.9998947)
    self.assertEqual(response.review_completed, False)
    self.assertEqual(response.batch_id, '12937')
    # Assert error message
    self.assertEqual(response.files[0].documents[0].fields[1].error_msg,
                     "dummy error message")

  @patch.object(urllib3.PoolManager, 'request')
  def test_get_run_results_all_flags(self, mock_request) -> None:
    """Test case for get_run_results

        Retrieve run results for all options
        """
    run_id = "run123"
    post_processed_pdf_path = "test_user/my-repo/fs/Instabase Drive/app-runs/976bf734-6271-44c3-860d-ea75c0c93f2c/ef0d286a-3da1-4330-b13a-059257b646ea/s1_process_files/images/new_file.txt.pdf"
    expected_response = {
        "has_more":
        False,
        "batch_id":
        '1251',
        "files": [{
            "original_file_name":
            "willy.pdf",
            "input_file_path":
            "instabase-sandbox-org/support-testing.aihubuat-orguser_instabase.com/fs/S3 Test Drive/app-runs/5faf5dc6-dd97-42cb-8b8e-28a63066887e/1716916997868/input/s1_process_files/images/W2_Multi_Sample_Data_input_ADP1_clean_15517-19 (1).pdf",
            "documents": [{
                "class_name":
                "Wage And Tax Statement",
                "fields": [{
                    "field_name": "field_1",
                    "value": "other",
                    "type": "TEXT",
                    "confidence": {
                        "model": 0.12,
                        "ocr": 0.12
                    },
                    "edit_history": [],
                    "source_coordinates": [],
                    "validations": {
                        "valid": True,
                        "alerts": []
                    }
                }, {
                    "field_name":
                    "employers_address_and_ZIP_code",
                    "value":
                    "757 Martin Hill Suite 056 East Kyle SC 74614-1778",
                    "type":
                    "TEXT",
                    "confidence": {
                        "model": 0.70431864,
                        "ocr": 0.70431864
                    },
                    "edit_history": [{
                        "modification_timestamp":
                        "2024-07-01 16:00:00",
                        "user_id":
                        "willy",
                        "modifications": [{
                            "message": "edited to 'X'"
                        }]
                    }],
                    "source_coordinates": [{
                        "top_x": 153.0,
                        "top_y": 573.33,
                        "bottom_x": 191.69999885559082,
                        "bottom_y": 584.08,
                        "page_number": 0
                    }, {
                        "top_x": 205.0,
                        "top_y": 573.33,
                        "bottom_x": 282.39999771118164,
                        "bottom_y": 584.08,
                        "page_number": 0
                    }],
                    "validations": {
                        "valid":
                        False,
                        "alerts": [{
                            "alert_level": "failure",
                            "msg":
                            "Field [Wage And Tax Statement.employers_address_and_ZIP_code] confidence value was lower than threshold 0.95",
                            "blocked": False,
                            "type": "confidence",
                            "locations": []
                        }]
                    }
                }],
                "post_processed_paths": [
                    "instabase-sandbox-org/support-testing.aihubuat-orguser_instabase.com/fs/S3 Test Drive/app-runs/5faf5dc6-dd97-42cb-8b8e-28a63066887e/1716916997868/output/s1_process_files/images/W2_Multi_Sample_Data_input_ADP1_clean_15517-19 (1).pdf_p0.JPEG.jpeg",
                    "instabase-sandbox-org/support-testing.aihubuat-orguser_instabase.com/fs/S3 Test Drive/app-runs/5faf5dc6-dd97-42cb-8b8e-28a63066887e/1716916997868/output/s1_process_files/images/W2_Multi_Sample_Data_input_ADP1_clean_15517-19 (1).pdf_p1.JPEG.jpeg",
                    "instabase-sandbox-org/support-testing.aihubuat-orguser_instabase.com/fs/S3 Test Drive/app-runs/5faf5dc6-dd97-42cb-8b8e-28a63066887e/1716916997868/output/s1_process_files/images/W2_Multi_Sample_Data_input_ADP1_clean_15517-19 (1).pdf_p2.JPEG.jpeg"
                ],
                'post_processed_pdf_path':
                post_processed_pdf_path,
                "review_completed":
                False,
                "class_edit_history": [],
                "classification_confidence": {
                    "model": 0.70431864
                },
                "validations": {
                    "final_result_pass": False
                }
            }]
        }],
        "review_completed":
        False,
        "keys": {
            "custom": {}
        }
    }

    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.get_run_results(
        run_id,
        include_confidence_scores=True,
        include_source_info=True,
        include_review_results=True,
        include_validation_results=True,
        file_offset=0)
    self.assertFalse(response.has_more)
    self.assertEqual(response.review_completed, False)
    self.assertEqual(len(response.files), 1)
    self.assertEqual(response.files[0].original_file_name, "willy.pdf")
    self.assertEqual(
        response.files[0].input_file_path,
        "instabase-sandbox-org/support-testing.aihubuat-orguser_instabase.com/fs/S3 Test Drive/app-runs/5faf5dc6-dd97-42cb-8b8e-28a63066887e/1716916997868/input/s1_process_files/images/W2_Multi_Sample_Data_input_ADP1_clean_15517-19 (1).pdf"
    )
    self.assertEqual(len(response.files[0].documents), 1)
    self.assertEqual(len(response.files[0].documents[0].fields), 2)
    self.assertEqual(
        len(response.files[0].documents[0].post_processed_paths), 3)
    self.assertEqual(response.files[0].documents[0].post_processed_pdf_path,
                     post_processed_pdf_path)

    # first field
    first_field = response.files[0].documents[0].fields[0]
    self.assertEqual(first_field.field_name, 'field_1')
    self.assertEqual(first_field.value, 'other')
    self.assertEqual(first_field.confidence.model, 0.12)
    self.assertEqual(first_field.validations.valid, True)
    self.assertEqual(len(first_field.source_coordinates), 0)
    self.assertEqual(len(first_field.edit_history), 0)

    # second field
    second_field = response.files[0].documents[0].fields[1]
    self.assertEqual(second_field.field_name, 'employers_address_and_ZIP_code')
    self.assertEqual(second_field.value,
                     '757 Martin Hill Suite 056 East Kyle SC 74614-1778')
    self.assertEqual(second_field.confidence.model, 0.70431864)
    self.assertEqual(second_field.validations.valid, False)
    self.assertEqual(
        second_field.validations.alerts[0].msg,
        "Field [Wage And Tax Statement.employers_address_and_ZIP_code] confidence value was lower than threshold 0.95"
    )
    self.assertEqual(len(second_field.source_coordinates), 2)
    self.assertEqual(len(second_field.edit_history), 1)
    self.assertEqual(second_field.edit_history[0].modifications[0].message,
                     "edited to 'X'")

  @patch.object(urllib3.PoolManager, 'request')
  def test_get_run_status(self, mock_request) -> None:
    """Test case for get_run_status

        Get the status of a run.
        """
    run_id = "run123"
    expected_response = {"id": run_id, "status": "COMPLETE"}

    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.get_run_status(run_id)
    self.assertEqual(response.id, run_id)
    self.assertEqual(response.status, "COMPLETE")

  @patch.object(urllib3.PoolManager, 'request')
  def test_run_app(self, mock_request) -> None:
    """Test case for run_app

        Run a given app.
        """
    app_id = "app123"
    batch_id = 123
    expected_response = {"id": "run123", "status": "RUNNING"}

    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.run_app({'app_id': app_id, 'batch_id': batch_id})
    self.assertEqual(response.id, "run123")
    self.assertEqual(response.status, "RUNNING")

  @patch.object(urllib3.PoolManager, 'request')
  def test_run_app_input_dir(self, mock_request) -> None:
    """Test case for run_app

        Run a given app.
        """
    app_id = "app123"
    expected_response = {"id": "run123", "status": "RUNNING"}

    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.run_app({
        'app_id': app_id,
        'input_dir': 'ib/my-repo/Instabase Drive'
    })
    self.assertEqual(response.id, "run123")
    self.assertEqual(response.status, "RUNNING")

  @patch.object(urllib3.PoolManager, 'request')
  def test_run_deployment_with_batch(self, mock_request) -> None:
    """Test case for run_deployment with a batch

    Run deployment
    """
    deployment_id = "deployment123"
    batch_id = 123
    expected_response = {
        "id": "run123",
        "status": "RUNNING",
        "msg": "",
        "start_timestamp": 100,
        "finish_timestamp": 200
    }

    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=202)
    mock_request.return_value = mock_response

    response = self.api.run_deployment(deployment_id, {'batch_id': batch_id})
    self.assertEqual(response.id, "run123")
    self.assertEqual(response.status, "RUNNING")
    self.assertEqual(response.msg, "")
    self.assertEqual(response.start_timestamp, 100)
    self.assertEqual(response.finish_timestamp, 200)

  @patch.object(urllib3.PoolManager, 'request')
  def test_run_deployment_with_upstream_integration(self,
                                                    mock_request) -> None:
    """Test case for run_deployment with an upstream integration

    Run deployment
    """
    deployment_id = "deployment123"
    expected_response = {
        "id": "run123",
        "status": "RUNNING",
        "msg": "",
        "start_timestamp": 100,
        "finish_timestamp": 200
    }

    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=202)
    mock_request.return_value = mock_response

    response = self.api.run_deployment(
        deployment_id, {
            'manual_upstream_integration': True,
            'from_timestamp': 0,
            'to_timestamp': 1734133834
        })
    self.assertEqual(response.id, "run123")
    self.assertEqual(response.status, "RUNNING")
    self.assertEqual(response.msg, "")
    self.assertEqual(response.start_timestamp, 100)
    self.assertEqual(response.finish_timestamp, 200)

  @patch.object(urllib3.PoolManager, 'request')
  def test_list_runs(self, mock_request) -> None:
    """Test case for list_runs

        List all runs.
        """
    expected_response = {
        "runs": [{
            "id": "run123",
            "status": "RUNNING",
            "msg": "",
            "start_timestamp": 100,
            "finish_timestamp": 200
        }]
    }

    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=200)
    mock_request.return_value = mock_response

    response = self.api.list_runs()
    self.assertEqual(len(response.runs), 1)
    self.assertEqual(response.runs[0].id, "run123")
    self.assertEqual(response.runs[0].status, "RUNNING")

  @patch.object(urllib3.PoolManager, 'request')
  def test_delete_run(self, mock_request) -> None:
    """Test case for delete_run

        Delete run
        """
    run_id = "run123"
    expected_response = {
        "delete_input_dir_job_id": "job123",
        "delete_output_dir_job_id": "job124",
        "delete_log_dir_job_id": "job125"
    }

    mock_response = urllib3.HTTPResponse(
        body=bytes(json.dumps(expected_response), 'utf-8'), status=202)
    mock_request.return_value = mock_response

    response = self.api.delete_run(run_id)
    self.assertEqual(response.delete_input_dir_job_id, "job123")
    self.assertEqual(response.delete_output_dir_job_id, "job124")
    self.assertEqual(response.delete_log_dir_job_id, "job125")


if __name__ == '__main__':
  unittest.main()
