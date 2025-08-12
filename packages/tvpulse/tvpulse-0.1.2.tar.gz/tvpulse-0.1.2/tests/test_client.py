import unittest
from unittest.mock import MagicMock, patch
from tvpulse.client import Client
from tvpulse.exceptions import InvalidRequestError


class TestClient(unittest.TestCase):

  def setUp(self):
    self.api_key = "test_api_key"
    self.client = Client(api_key=self.api_key)
    self.test_params = {
        "keyword": "test",
        "streams": ["TBS"],
        "start_date": "2025-01-01 00:00:00",
        "end_date": "2025-01-01 06:00:00",
        "frequency": "hour",
        "score_threshold": 0.95
    }

  @patch('tvpulse.api.API.search_voice')
  def test_get_data_asr(self, mock_search_voice):
    mock_search_voice.return_value = {"data": [], "next_page_token": None}
    response = self.client.get_data(searchTypes=["asr"], **self.test_params)
    self.assertIsNotNone(response)
    mock_search_voice.assert_called_once_with(**self.test_params)

  @patch('tvpulse.api.API.search_text')
  def test_get_data_ocr(self, mock_search_text):
    mock_search_text.return_value = {"data": [], "next_page_token": None}
    response = self.client.get_data(searchTypes=["ocr"], **self.test_params)
    self.assertIsNotNone(response)
    mock_search_text.assert_called_once_with(**self.test_params)

  def test_get_data_no_search_types(self):
    with self.assertRaises(TypeError):
      self.client.get_data(**self.test_params)

  def test_get_data_empty_search_types(self):
    with self.assertRaises(InvalidRequestError):
      self.client.get_data(searchTypes=[], **self.test_params)

  def test_get_data_multiple_search_types(self):
    with self.assertRaises(InvalidRequestError):
      self.client.get_data(searchTypes=["asr", "ocr"], **self.test_params)

  def test_get_data_invalid_search_type(self):
    with self.assertRaises(InvalidRequestError):
      self.client.get_data(searchTypes=["invalid"], **self.test_params)

  def test_get_data_invalid_stream(self):
    with self.assertRaises(InvalidRequestError):
      params = self.test_params.copy()
      params["streams"] = ["invalid"]
      self.client.get_data(searchTypes=["asr"], **params)


if __name__ == '__main__':
  unittest.main()
