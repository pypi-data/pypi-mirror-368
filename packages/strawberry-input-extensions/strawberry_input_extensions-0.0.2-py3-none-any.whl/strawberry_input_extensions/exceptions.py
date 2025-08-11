from typing import List, Union, Type

from strawberry import Info


VALIDATION_EXCEPTION_CLASSES: List[Type[BaseException]] = [
    ValueError
]

try:
    from django.core.exceptions import ValidationError
    VALIDATION_EXCEPTION_CLASSES.append(ValidationError)
except ImportError:
    pass


def transform_path(path: List[Union[str, int]], info: Info) -> List[str]:
    return [
        info.schema.config.name_converter.apply_naming_config(str(part))
        for part in path
    ]


class InputExtensionFieldException(BaseException):
    """Represents an error that occurred during input field extension processing.

    This class captures the exception raised by an extension and the associated field path
    where the error occurred in the input data structure.
    """

    def __init__(self, exception_or_message: Union[Exception, str], path: Union[List[str], str], info: Info) -> None:
        """Initialize a new InputExtensionFieldException.

        Args:
            exception_or_message: The exception that was raised during extension processing
            path: The path to the path in the input data where the error occurred
        """
        if isinstance(path, str):
            path = [path]

        if not isinstance(exception_or_message, BaseException):
            exception = ValueError(exception_or_message)
        else:
            exception = exception_or_message

        self.exception: Exception = exception
        self.path: List[str] = transform_path(path, info)

    def __str__(self) -> str:
        """Return a string representation of the error.

        Returns:
            A string in the format 'field_path: exception_message'
        """
        return f'{self.path}: {self.exception}'


class InputExtensionException(Exception):
    """Exception raised when one or more input extensions encounter errors.

    This exception aggregates multiple InputExtensionFieldException instances that
    occurred during the processing of input data.
    """

    def __init__(self, errors: List[InputExtensionFieldException]) -> None:
        """Initialize a new InputExtensionException.

        Args:
            errors: List of InputExtensionFieldException instances that occurred
        """
        self.errors: List[InputExtensionFieldException] = errors
        message = ', '.join(str(error) for error in errors)
        super().__init__(message)
