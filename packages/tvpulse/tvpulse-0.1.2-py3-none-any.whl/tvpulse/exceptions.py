class TVPulseError(Exception):
  """
  Base class for all TVPulse SDK errors.
  """
  pass


class AuthenticationError(TVPulseError):
  """
  Raised when there is an authentication error.
  """
  pass


class InvalidRequestError(TVPulseError):
  """
  Raised when the request is invalid.
  """
  pass
