from typing import Any

from pydantic import BaseModel, Field, create_model
from typing_extensions import Literal


def _python_type(openapi_type: str, enum_values: list[Any] | None) -> Any:
    """
    Convert an OpenAPI type string to a corresponding Python type.
    If there is an enum, return a Literal[...] instead.
    """
    if enum_values:
        # Use Literal if there's an enum
        return Literal[tuple(enum_values)]

    # Fallback by schema type
    if openapi_type == "string":
        return str
    elif openapi_type == "boolean":
        return bool
    elif openapi_type == "integer":
        return int
    elif openapi_type == "number":
        return float
    # default to str if no recognized type
    return str


def generate_pydantic_model(model_name: str, parameters: list[dict]) -> BaseModel:
    """
    Dynamically generate a Pydantic model class with fields derived from
    OpenAPI/Swagger-style parameter definitions.
    """
    fields = {}

    for param in parameters:
        field_name = param["name"]
        required = param.get("required", False)
        description = param.get("description", "")

        # Extract type info and enums
        schema = param.get("schema", {})
        openapi_type = schema.get("type", "string")
        enum_values = schema.get("enum")

        # Convert to Python type (Literal if enum is present)
        py_type = _python_type(openapi_type, enum_values)

        # If a param is required, use Ellipsis (...) as the default;
        # otherwise default to None.
        default = ... if required else None

        # You might also want to process `schema.get("example")`
        # or the top-level `param.get("examples")`.
        example = schema.get("example")

        # For multiple examples, you can store them as extra metadata:
        examples = param.get("examples", {})

        # Field(...) helps specify details like description, example, etc.
        field_obj = Field(
            default,
            description=description,
            example=example,  # single example
            examples=examples or None,  # multiple examples if present
        )  # type: ignore

        # Add a (type, Field) tuple to 'fields'
        fields[field_name] = (py_type, field_obj)

    # create_model returns a new Model subclass named `model_name`
    return create_model(model_name, **fields)  # type: ignore
