class FormatError(Exception):
    """Exception raised for errors in the input format."""
    pass


class MaxAttemptsExceededError(Exception):
    """Throws an exception when the maximum number of attempts is exceeded."""
    pass


class OptionError(Exception):
    """Exception caused by wrong option."""
    pass


class LoadError(Exception):
    """Exception thrown when loading fails."""
    pass
