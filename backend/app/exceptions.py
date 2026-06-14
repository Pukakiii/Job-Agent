class AppError(Exception): 
    """Base for HTTP-agnostic domain errors. Services raise these; a single
    handler at the edge maps them to the response envelope."""

    status_code: int = 400 
    code: str = "app_error"

    def __init__(self, message: str) -> None: 
        self.message = message 
        super().__init__(message)

class CVNotFound(AppError):
    status_code = 404
    code = "cv_not_found"


class EmptyCVFile(AppError):
    status_code = 400
    code = "empty_cv_file"


class CVFileTooLarge(AppError):
    status_code = 413
    code = "cv_file_too_large"


class UnsupportedCVType(AppError):
    status_code = 415
    code = "unsupported_cv_type"


class LLMOutputInvalid(AppError):
    status_code = 502
    code = "llm_output_invalid"


class CVNotParsed(AppError):
    status_code = 409
    code = "cv_not_parsed"


class NoMatchesFound(AppError):
    status_code = 404
    code = "no_matches"


class SearchNotFound(AppError):
    status_code = 404
    code = "search_not_found"


class JobNotFound(AppError):
    status_code = 404
    code = "job_not_found"
