class BaseInvokerError(Exception):
    """Base exception class for all gllm_inference invoker errors."""
    def __init__(self, class_name: str, message: str) -> None:
        """Initialize the base exception.

        Args:
            class_name (str): The name of the class that raised the error.
            message (str): The error message.
        """

class ProviderInvalidArgsError(BaseInvokerError):
    """Exception for bad or malformed requests, invalid parameters or structure.

    Corresponds to HTTP 400 status code.
    """
    def __init__(self, class_name: str) -> None:
        """Initialize ProviderInvalidArgsError.

        Args:
            class_name (str): The name of the class that raised the error.
            message (str): The error message.
        """

class ProviderAuthError(BaseInvokerError):
    """Exception for authorization failures due to API key issues.

    Corresponds to HTTP 401-403 status codes.
    """
    def __init__(self, class_name: str) -> None:
        """Initialize ProviderAuthError.

        Args:
            class_name (str): The name of the class that raised the error.
            message (str): The error message.
        """

class ProviderRateLimitError(BaseInvokerError):
    """Exception for rate limit violations.

    Corresponds to HTTP 429 status code.
    """
    def __init__(self, class_name: str) -> None:
        """Initialize ProviderRateLimitError.

        Args:
            message (str): The error message.
            class_name (str): The name of the class that raised the error.
        """

class ProviderInternalError(BaseInvokerError):
    """Exception for unexpected server-side errors.

    Corresponds to HTTP 500 status code.
    """
    def __init__(self, class_name: str) -> None:
        """Initialize ProviderInternalError.

        Args:
            message (str): The error message.
            class_name (str): The name of the class that raised the error.
        """

class ProviderOverloadedError(BaseInvokerError):
    """Exception for when the engine is currently overloaded.

    Corresponds to HTTP 503, 529 status codes.
    """
    def __init__(self, class_name: str) -> None:
        """Initialize ProviderOverloadedError.

        Args:
            class_name (str): The name of the class that raised the error.
            message (str): The error message.
        """

class ModelNotFoundError(BaseInvokerError):
    """Exception for authorization failures due to API key issues.

    Corresponds to HTTP 401-403 status codes.
    """
    def __init__(self, class_name: str) -> None:
        """Initialize ProviderAuthError.

        Args:
            class_name (str): The name of the class that raised the error.
            message (str): The error message.
        """

class InvokerRuntimeError(BaseInvokerError):
    """Exception for runtime errors that occur during the invocation of the model.

    Corresponds to HTTP status codes other than the ones defined in HTTP_STATUS_TO_EXCEPTION_MAP.
    """
    def __init__(self, class_name: str, message: str) -> None:
        """Initialize the InvokerRuntimeError.

        Args:
            class_name (str): The name of the class that raised the error.
            message (str): The error message describing what went wrong.
        """
