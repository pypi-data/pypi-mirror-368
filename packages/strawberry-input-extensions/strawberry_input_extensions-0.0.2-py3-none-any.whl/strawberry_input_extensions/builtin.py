from typing import Annotated, Optional, Union

from .extension import InputExtension


class NonNullableOptional(InputExtension):
    """Extension that ensures an Optional field cannot receive a null value.
    
    While the field's type may be Optional, this extension will reject null values
    during runtime validation.
    
    Example:
        ```python
        @strawberry.type
        class MyInput:
            name: NonNullableOptional[str] # Will raise error if null
        ```
    """
    def resolve(self, value, info, next_, path):
        if value is None:
            raise ValueError("This field cannot be null")
        return next_(value)

    def __class_getitem__(cls, type_):
        return Annotated[Optional[type_], cls()]


class MinValue(InputExtension):
    """Extension that enforces a minimum value for numeric inputs.
    
    Args:
        minimum (Union[int, float]): The minimum allowed value (inclusive)
    
    Example:
        ```python
        @strawberry.type
        class MyInput:
            age: MinValue[int, 18] # Must be 18 or greater
        ```
    """
    def __init__(self, minimum: Union[int, float]):
        self.minimum = minimum

    def resolve(self, value, info, next_, path):
        if value < self.minimum:
            raise ValueError(f"Value must be greater than or equal to {self.minimum}")
        return next_(value)


class MaxValue(InputExtension):
    """Extension that enforces a maximum value for numeric inputs.
    
    Args:
        maximum (Union[int, float]): The maximum allowed value (inclusive)
    
    Example:
        ```python
        @strawberry.type
        class MyInput:
            rating: MaxValue[float, 5.0] # Must be 5.0 or less
        ```
    """
    def __init__(self, maximum: Union[int, float]):
        self.maximum = maximum

    def resolve(self, value, info, next_, path):
        if value > self.maximum:
            raise ValueError(f"Value must be less than or equal to {self.maximum}")
        return next_(value)


class BetweenValue(InputExtension):
    """Extension that ensures a numeric value falls within a specified range.
    
    Args:
        minimum (Union[int, float]): The minimum allowed value (inclusive)
        maximum (Union[int, float]): The maximum allowed value (inclusive)
    
    Example:
        ```python
        @strawberry.type
        class MyInput:
            score: BetweenValue[int, 0, 100] # Must be between 0 and 100
        ```
    """
    def __init__(self, minimum: Union[int, float], maximum: Union[int, float]):
        self.minimum = minimum
        self.maximum = maximum

    def resolve(self, value, info, next_, path):
        if value > self.maximum or value < self.minimum:
            raise ValueError(f"Value must be between {self.minimum} and {self.maximum}")
        return next_(value)


class MinLength(InputExtension):
    """Extension that enforces a minimum length for strings or sequences.
    
    Args:
        minimum (int): The minimum allowed length
    
    Example:
        ```python
        @strawberry.type
        class MyInput:
            password: MinLength[str, 8] # Must be at least 8 chars
        ```
    """
    def __init__(self, minimum: int):
        self.minimum = minimum

    def resolve(self, value, info, next_, path):
        if len(value) < self.minimum:
            raise ValueError(f"Length must be greater than or equal to {self.minimum}")
        return next_(value)


class MaxLength(InputExtension):
    """Extension that enforces a maximum length for strings or sequences.
    
    Args:
        maximum (int): The maximum allowed length
    
    Example:
        ```python
        @strawberry.type
        class MyInput:
            username: MaxLength[str, 20]  # Must be 20 chars or less
        ```
    """
    def __init__(self, maximum: int):
        self.maximum = maximum

    def resolve(self, value, info, next_, path):
        if len(value) > self.maximum:
            raise ValueError(f"Length must be less than or equal to {self.maximum}")
        return next_(value)


class BetweenLength(InputExtension):
    """Extension that ensures the length of a string or sequence falls within a specified range.
    
    Args:
        minimum (int): The minimum allowed length (inclusive)
        maximum (int): The maximum allowed length (inclusive)
    
    Example:
        ```python
        @strawberry.type
        class MyInput:
            title: BetweenLength[str, 5, 100]  # Length must be 5-100 chars
        ```
    """
    def __init__(self, minimum: int, maximum: int):
        self.minimum = minimum
        self.maximum = maximum

    def resolve(self, value, info, next_, path):
        if len(value) > self.maximum or len(value) < self.minimum:
            raise ValueError(f"Length must be between {self.minimum} and {self.maximum}")
        return next_(value)