class AppException(Exception):
    """Base application exception with HTTP status code mapping."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ScrapingError(AppException):
    """Raised when job description or company page scraping fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=502)


class ResumeParsingError(AppException):
    """Raised when resume parsing fails or extracted text is invalid."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class LLMGenerationError(AppException):
    """Raised when LLM analysis or variant generation encounters an unrecoverable failure."""
    def __init__(self, message: str):
        super().__init__(message, status_code=503)
