# Docstring Style Guide

This guide describes the docstring style used in sts-libs.
We loosely follow Google-style docstrings with some specific conventions for examples.

## Code Formatting

ruff formatter also formats code in docstrings:

```bash
hatch run format
```

or directly with ruff:

```bash
ruff format
```

This will ensure consistent formatting across the codebase and docstrings.
With pre-commit hook installed, it will be automatically run on commit.

## Single Example

```python
def my_function():
    """Function description.

    Detailed description of what the function does.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value

    Example:
        ```python
        result = my_function(1, 2)
        ```
    """
```

## Multiple Examples

```python
def my_function():
    """Function description.

    Detailed description of what the function does.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value

    Examples:
        Basic usage:
        ```python
        result = my_function(1, 2)
        ```

        With optional parameters:
        ```python
        result = my_function(1, 2, optional=True)
        ```

        Error handling:
        ```python
        try:
            result = my_function(-1, 2)
        except ValueError:
            print("Invalid input")
        ```
    """
```

## Key Points

1. Use descriptive text before each example
2. Use "Example:" for single examples, "Examples:" for multiple
3. Keep examples concise and focused
4. Include expected output in comments where relevant
5. Use markdown code blocks for proper rendering in mkdocs

## Common Patterns

### Class Examples

```python
class MyClass:
    """Class description.

    Examples:
        Create with default settings:
        ```python
        obj = MyClass()
        ```

        Create with custom settings:
        ```python
        obj = MyClass(setting=True)
        ```
    """
```

### Method Examples

```python
def method(self):
    """Method description.

    Example:
        ```python
        obj = MyClass()
        result = obj.method()  # Returns expected value
        ```
    """
```

### Function Examples

```python
def function():
    """Function description.

    Examples:
        Basic usage:
        ```python
        function()
        ```

        With error handling:
        ```python
        try:
            function()
        except Error:
            handle_error()
        ```
    """
```

## Previewing Documentation

To see how your docstrings are rendered in mkdocs:

1. Run the documentation server locally:

   ```bash
   hatch run docs:serve
   ```

2. Open your browser to <http://127.0.0.1:8000>

This allows you to verify that your examples are properly rendered in the documentation.

## Tips for Writing Good Examples

1. **Be Concise**: Examples should demonstrate one specific use case clearly
2. **Show Real Usage**: Use realistic variable names and values
3. **Include Context**: Add brief descriptions before examples
4. **Show Outputs**: Use comments to indicate expected return values or outputs
5. **Error Cases**: Include examples of handling common errors when relevant
