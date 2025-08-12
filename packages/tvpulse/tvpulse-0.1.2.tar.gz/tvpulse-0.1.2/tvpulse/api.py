import requests


class API:
  """
  A wrapper for the TVPulse API.
  """
  BASE_URL = "https://gateway.dev.sdio.co.jp/v1/api"

  def __init__(self, api_key: str):
    """
    Initializes the API client with the given API key.

    Args:
      api_key: The API key to use for authentication.
    """
    self.api_key = api_key
    self.headers = {"X-API-KEY": self.api_key}

  def _request(self, method: str, endpoint: str, **kwargs):
    """
    Makes a request to the API.

    Args:
      method: The HTTP method to use (e.g., "GET", "POST").
      endpoint: The API endpoint to call.
      **kwargs: Additional keyword arguments to pass to the request.

    Returns:
      The JSON response from the API.
    """
    url = f"{self.BASE_URL}/{endpoint}"
    response = requests.request(method, url, headers=self.headers, **kwargs)
    print(f"Request URL: {response.url}"
          )  # Debugging line to print the request URL
    print(f"Response Status Code: {response.status_code}")  # Debugging line to
    if response.status_code == 403:
      from .exceptions import AuthenticationError
      raise AuthenticationError("Invalid API key or insufficient permissions.")
    response.raise_for_status()
    return response.json()

  def search_text(self, keyword: str, streams: list, start_date: str, end_date: str, frequency: str, score_threshold: float):
    """
    Performs a text search.
    """
    payload = {
        "keyword": keyword,
        "streams": streams,
        "start_date": start_date,
        "end_date": end_date,
        "frequency": frequency,
        "score_threshold": score_threshold,
    }
    return self._request("POST", "text/search", json=payload)

  def search_voice(self, keyword: str, streams: list, start_date: str, end_date: str, frequency: str, score_threshold: float):
    """
    Performs a voice search.
    """
    payload = {
        "keyword": keyword,
        "streams": streams,
        "start_date": start_date,
        "end_date": end_date,
        "frequency": frequency,
        "score_threshold": score_threshold,
    }
    return self._request("POST", "voice/search", json=payload)
