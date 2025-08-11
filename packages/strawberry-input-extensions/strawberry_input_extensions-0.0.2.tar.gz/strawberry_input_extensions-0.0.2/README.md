# Strawberry GraphQL Input Extensions

A simple extension system for Strawberry GraphQL that provides declarative input validation and transformation through Python type annotations. This extension allows you to add validation rules and transformations to your GraphQL inputs while maintaining clean, readable code.


### This package should currently be considered unstable, and not used in production. Don't count on SemVer versioning being representative of non-breaking changes until a stable 1.0 release.  


## Overview

This module implements a flexible extension system for Strawberry GraphQL that enables validation and transformation of input values in GraphQL operations. It supports both synchronous and asynchronous operations, and handles nested input types, lists, and optional values.

## Key Components

- **InputExtension**: Base class for creating custom input extensions
- **InputExtensionsExtension**: Strawberry extension that integrates with GraphQL schema
- **Built-in validators**: Ready-to-use extensions for common validation scenarios
- **Exception handling**: Structured error reporting for validation failures

## Usage

### Basic Example

```python
# Use extensions in your GraphQL types as annotations
@strawberry.type
class Mutation:
    @strawberry.mutation(extensions=[InputExtensionsExtension()])
    def create_user(
        self, 
        username: MaxLength[str, 20],
        age: MinValue[int, 18]
    ) -> str:
        return f"Created user {username} ({age})"


# Or via Annotated if you prefer
@strawberry.type
class Mutation:
    @strawberry.mutation(extensions=[InputExtensionsExtension()])
    def create_user(
        self, 
        username: Annotated[str, MaxLength(20)],
        age: Annotated[int, MinValue(18)]
    ) -> str:
        return f"Created user {username} ({age})"
```

### Custom Extensions

Create your own extensions by subclassing `InputExtension`:

```python
class ToUpperCase(InputExtension):
    def resolve(self, value, info, next_, path):
        return next_(value.upper())
```

Extensions can exit early if need be:
```python
class UnsetIfNoPermission(InputExtension):
    def __init__(self, permission):
        self.permission = permission
        
    def resolve(self, value, info, next_, path):
        user = get_current_user(info)
        if not user_has_permission(user, self.permission):
            # no permission for the field, return UNSET as if it wasn't set
            return UNSET
        # remaining extensions are only for users with permissions
        return next_(value)

@strawberry.input
class BlogInput:
    title: NonNullableOptional[UnsetIfNoPermission[str, 'edit:title']] = UNSET
```


### Input types

Input fields can be used as expected, and you can also perform object level extensions using a decorator.

```python
class ValidatePasswordsMatch(InputExtension):
    def resolve(self, value, info, next_, path):
        if value.password != value.confirm_password:
            # raise the error against the password field
            raise InputExtensionFieldException("Passwords don't match", "password", info)
        return next_(value)
    
# Since they're just annotated types, they don't need to be declared in-line
PasswordField = MinLength[str, 8]

@ValidatePasswordsMatch.decorator()
@strawberry.input
class MyInput:
    password: PasswordField
    confirm_password: PasswordField
```


## Built-in Extensions

### Value Validation
- `MinValue(value)` - Ensures numeric value is at least the minimum
- `MaxValue(value)` - Ensures numeric value is at most the maximum
- `BetweenValue(min, max)` - Ensures numeric value is within range

### Length Validation
- `MinLength(length)` - Ensures string/sequence is at least the minimum length
- `MaxLength(length)` - Ensures string/sequence is at most the maximum length
- `BetweenLength(min, max)` - Ensures string/sequence length is within range

### Optional Handling
- `NonNullableOptional` - Makes an Optional field reject null values while still being optional

## Combining Extensions

Extensions can be chained to apply multiple validations/transformations:

```python
@strawberry.type
class Mutation:
    @strawberry.mutation(extensions=[InputExtensionsExtension()])
    def create_user(
        self, 
        # called outside-in, eg. BetweenLength is called first, then ToUpperCase    
        username: BetweenLength[ToUpperCase[str], 3, 20]
        
        # called in reverse order, so this is identical to the above
        username: Annotated[
            str, 
            ToUpperCase(),
            BetweenLength(3, 20)
        ]
    ) -> str:
        return f"Created user {username}"
```

## Nested Validation

Extensions work with nested input types and lists:

```python
@strawberry.input
class UserInput:
    username: MaxLength[str, 20]
    roles: MinLength[List[str], 1]
     # either UNSET or a valid string, never null
    favorite_ide: NonNullableOptional[ToUpperCase[str]] = UNSET
    

@strawberry.type
class Mutation:
    @strawberry.mutation(extensions=[InputExtensionsExtension()])
    def create_user(self, input: UserInput) -> str:
        return f"Created user {input.username}"
```

## Async Support

The extension system supports async resolvers:

```python
class AsyncExtension(InputExtension):
    async def resolve_async(self, value, info, next_, path):
        # Perform async validation/transformation
        return await next_(value)
```
By default, resolve_async calls resolve(), so this can be omitted unless you're actually doing async work in the extension
