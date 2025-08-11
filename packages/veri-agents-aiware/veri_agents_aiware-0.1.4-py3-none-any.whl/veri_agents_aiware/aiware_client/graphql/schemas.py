from typing import Any, Type, cast
from pydantic import BaseModel

class JSONData(BaseModel):
    """
    Basic wrapper class to avoid JSONData graphql scalar to be typed as Any.

    See `[tool.ariadne-codegen.scalars.JSONData]` section in pyproject.toml.
    """
    value: Any

    def as_model[T: BaseModel](self, cls: Type[T]) -> T:
        """cast to pydantic type"""
        return cls.model_validate(cast(Any, self.value))


def parse_jsondata(value: Any) -> "JSONData":
    return JSONData(value=value)


def serialize_jsondata(jsondata: "JSONData") -> Any:
    return cast(Any, jsondata.value)
