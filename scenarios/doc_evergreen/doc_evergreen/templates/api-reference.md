# API Reference Template

## Instructions for AI

You are generating an API reference document for a software project.

**Tone**: Technical, precise, comprehensive
**Audience**: Developers integrating with or using the API
**Structure**: Follow the example structure below

## Required Sections

1. **Overview**: Brief description of the API's purpose
2. **Modules/Classes**: Organized by functionality
3. **Functions/Methods**: Clear signatures, parameters, return values
4. **Examples**: Practical usage examples
5. **Error Handling**: Common errors and how to handle them

## Example Output

---

# API Reference

Overview of what this API provides and its main use cases.

## Core Module

### ClassName

Brief description of what this class does.

#### `__init__(param1: Type, param2: Type)`

Initialize the class.

**Parameters:**
- `param1` (Type): Description of parameter
- `param2` (Type): Description of parameter

**Example:**
```python
obj = ClassName(param1="value", param2=123)
```

#### `method_name(arg: Type) -> ReturnType`

Description of what this method does.

**Parameters:**
- `arg` (Type): Description of argument

**Returns:**
- `ReturnType`: Description of return value

**Raises:**
- `ValueError`: When invalid input
- `RuntimeError`: When operation fails

**Example:**
```python
result = obj.method_name("input")
```

## Utility Functions

### `function_name(param: Type) -> ReturnType`

Description of standalone function.

**Parameters:**
- `param` (Type): Description

**Returns:**
- `ReturnType`: Description

**Example:**
```python
output = function_name(input_value)
```

## Error Handling

Common errors and how to handle them:

- **ErrorType**: Cause and resolution
- **AnotherError**: Cause and resolution

---

## Source Content

The following files have been provided as source material. Extract API information from docstrings, type hints, and code structure:

{{SOURCE_FILES}}

## Generation Rules

1. Extract all public classes and functions (not starting with _)
2. Use type hints for parameter and return types
3. Extract docstrings for descriptions
4. Generate practical examples based on actual usage patterns
5. Group related functionality together
6. Include error information from code and docstrings
7. Keep examples concise but complete
