"""Exception definitions."""

from pydantic.errors import (
    PydanticUserError,
    PydanticImportError,
    PydanticUndefinedAnnotation,
    PydanticSchemaGenerationError,
    PydanticInvalidForJsonSchema,
)
from pydantic_core import (
    PydanticCustomError,
    PydanticKnownError,
    PydanticSerializationError,
    SchemaError,
    ValidationError,
)

PYDANTIC_ERRORS = (
    PydanticCustomError,
    PydanticKnownError,
    PydanticSerializationError,
    SchemaError,
    ValidationError,
    PydanticUserError,
    PydanticImportError,
    PydanticUndefinedAnnotation,
    PydanticSchemaGenerationError,
    PydanticInvalidForJsonSchema,
)


class AigarthITUError(Exception):
    """Generic Aigarth IT Unit error."""

    pass


class AigarthITUInputDataError(Exception):
    """AIgarth IT Unit input data error."""

    pass
