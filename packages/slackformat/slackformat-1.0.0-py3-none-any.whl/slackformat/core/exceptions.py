class SlackFormatException(Exception):
    """Base exception for the slackformat library."""
    pass

class ParsingError(SlackFormatException):
    """Raised when there is an error parsing an input format."""
    pass

class ConversionError(SlackFormatException):
    """Raised when there is an error converting between formats."""
    pass