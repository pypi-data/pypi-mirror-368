from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, RootModel, field_validator, model_validator


class JsonPatchOperation(str, Enum):
    REPLACE = "replace"
    ADD = "add"
    REMOVE = "remove"
    MOVE = "move"
    COPY = "copy"
    TEST = "test"


class JsonPatchObject(BaseModel):
    op: JsonPatchOperation
    from_: Optional[str] = Field(alias="from", default=None)
    path: str
    value: Optional[Any] = None

    @field_validator("path")
    def path_must_start_with_slash(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError("path must start with a slash")
        return v

    @model_validator(mode="before")
    def operation_validation(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        operation: JsonPatchOperation = values.get("op")  # type: ignore
        if operation not in JsonPatchOperation.__members__.values():
            return values
        validation_map = {
            JsonPatchOperation.REPLACE: cls.add_replace_test_validation,
            JsonPatchOperation.ADD: cls.add_replace_test_validation,
            JsonPatchOperation.REMOVE: cls.remove_validation,
            JsonPatchOperation.MOVE: cls.move_copy_validation,
            JsonPatchOperation.COPY: cls.move_copy_validation,
            JsonPatchOperation.TEST: cls.add_replace_test_validation,
        }
        validation_map.get(operation)(values)
        return values

    @staticmethod
    def add_replace_test_validation(values: Dict[str, Any]) -> None:
        if values.get("value") is None:
            raise ValueError(f"value must be present for {values.get('op')} operations")
        if values.get("from") is not None:
            raise ValueError(
                f"from must not be present for {values.get('op')} operations"
            )

    @staticmethod
    def remove_validation(values: Dict[str, Any]) -> None:
        if values.get("value") is not None:
            raise ValueError("value must not be present for remove operations")
        if values.get("from") is not None:
            raise ValueError("from must not be present for remove operations")

    @staticmethod
    def move_copy_validation(values: Dict[str, Any]) -> None:
        if values.get("value") is not None:
            raise ValueError(
                f"value must not be present for {values.get('op')} operations"
            )
        if values.get("from") is None:
            raise ValueError(f"from must be present for {values.get('op')} operations")


class JsonPatchModel(RootModel):
    root: List[JsonPatchObject]

    def dump(self) -> List[Dict[str, Any]]:
        return [
            patch.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)
            for patch in self.root
        ]


class MetaModel(BaseModel):
    total: Optional[int] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
