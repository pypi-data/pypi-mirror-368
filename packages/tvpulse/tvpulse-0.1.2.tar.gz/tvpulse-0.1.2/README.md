# TVPulse Python SDK

The official Python SDK for the TVPulse API.

## Installation

```bash
pip install tvpulse
```

## Usage

First, you need to initialize the `Client` with your API key. You can get your API key from the TVPulse UI.

```python
import os
from tvpulse import Client, TVPulseError

# Initialize the SDK
# It's recommended to store your API key in an environment variable.
api_key = os.environ.get("TVPULSE_API_KEY")
if not api_key:
  raise ValueError("TVPULSE_API_KEY environment variable not set.")

client = Client(api_key=api_key)
```

### Get Data

You can use the `get_data` method to retrieve data from the API. This method takes the following arguments:

- `searchTypes`: A list of search types to use. Currently, only one search type is supported at a time. Valid search types are `"asr"` and `"ocr"`.
- `keyword`: The keyword to search for.
- `streams`: A list of streams to search.
- `start_date`: The start date of the search in `YYYY-MM-DD HH:MM:SS` format.
- `end_date`: The end date of the search in `YYYY-MM-DD HH:MM:SS` format.
- `frequency`: The frequency of the search. Valid values are `"hour"` and `"day"`.
- `score_threshold`: The score threshold for the search. This should be a float between 0 and 1.

Here's an example of how to use the `get_data` method:

```python
try:
  data = client.get_data(
      searchTypes=["asr"],
      keyword="コーヒー",
      streams=["CX", "EX", "NTV", "TBS", "TX"],
      start_date="2025-01-01 00:00:00",
      end_date="2025-01-02 23:59:59",
      frequency="hour",
      score_threshold=0.95
  )
  print(data)
except TVPulseError as e:
  print(f"An error occurred: {e}")
```

### Error Handling

The SDK raises custom exceptions for different types of errors. You can catch these exceptions to handle errors gracefully.

- `TVPulseError`: The base class for all SDK errors.
- `AuthenticationError`: Raised when there is an authentication error (e.g., an invalid API key).
- `InvalidRequestError`: Raised when the request is invalid (e.g., a missing or invalid parameter).
