class AvPassGenError(Exception):
    """Base exception for avpassgen."""
    pass

class CaptureError(AvPassGenError):
    """Raised when audio/video capture fails."""
    pass

class LowEntropyError(AvPassGenError):
    """Raised when collected entropy appears too low (heuristic)."""
    pass