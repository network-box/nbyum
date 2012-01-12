class NBYumException(Exception):
    """Generic exception that we'll raise when appropriate."""
    pass

class WTFException(Exception):
    """Exception raised when we have no idea what happened.

    This should probably never happen anyway, but the Yum API is such an
    ununderstandable and undocumented mess that I'd rather deal with this if
    it actually ever happens, rather than trying to understand why this would
    happen at the moment.
    """
    pass
