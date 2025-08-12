from .api import API
from .exceptions import InvalidRequestError
from .models import APIResponse


class Client:
  """
  The main client for interacting with the TVPulse API.
  """

  def __init__(self, api_key: str):
    """
    Initializes the client with the given API key.

    Args:
      api_key: The API key to use for authentication.
    """
    self.api = API(api_key)

  def get_data(self, searchTypes: list, keyword: str, streams: list,
               start_date: str, end_date: str, frequency: str,
               score_threshold: float):
    """
    Gets data from the TVPulse API.

    Args:
      searchTypes: A list of search types to use.
      keyword: The keyword to search for.
      streams: A list of streams to search.
      start_date: The start date of the search.
      end_date: The end date of the search.
      frequency: The frequency of the search.
      score_threshold: The score threshold for the search.

    Returns:
      The JSON response from the API.
    """
    search_types = searchTypes
    if not isinstance(search_types, list):
      raise InvalidRequestError("searchTypes must be a list.")

    if not search_types:
      raise InvalidRequestError("searchTypes cannot be empty.")

    if not isinstance(streams, list):
      raise InvalidRequestError("streams must be a list.")

    if not streams:
      raise InvalidRequestError("streams cannot be empty.")

    supported_streams = ["cx", "ex", "mx", "nhk", "ntv", "tbs", "tx"]
    for stream in streams:
      if stream.lower() not in supported_streams:
        raise InvalidRequestError(
            f"Invalid stream: {stream}. Supported streams are: {supported_streams}"
        )

    if len(search_types) > 1:
      # For now, we only support one search type at a time.
      # This can be extended to support multiple search types in the future.
      raise InvalidRequestError("Only one search type is supported at a time.")

    search_type = search_types[0]
    if search_type == "asr":
      response = self.api.search_voice(keyword=keyword,
                                       streams=streams,
                                       start_date=start_date,
                                       end_date=end_date,
                                       frequency=frequency,
                                       score_threshold=score_threshold)
    elif search_type == "ocr":
      response = self.api.search_text(keyword=keyword,
                                      streams=streams,
                                      start_date=start_date,
                                      end_date=end_date,
                                      frequency=frequency,
                                      score_threshold=score_threshold)
    else:
      raise InvalidRequestError(f"Invalid search type: {search_type}")

    return APIResponse(**response)
