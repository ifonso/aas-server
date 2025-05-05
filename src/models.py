from __future__ import annotations

from typing import List, Union, Optional, Dict, Type
from enum import Enum
from pydantic import BaseModel, model_validator


class ValueType(str, Enum):
    STRING = "string"
    FLOAT = "float"
    INT = "int"


class DataElementCategory(str, Enum):
    CONSTANT = "CONSTANT"
    PARAMETER = "PARAMETER"
    VARIABLE = "VARIABLE"


VALUE_TYPE_TO_PYTHON: Dict[ValueType, Type] = {
    ValueType.STRING: str,
    ValueType.FLOAT: float,
    ValueType.INT: int,
}


class BaseElement(BaseModel):
    id_short: str
    category: Optional[DataElementCategory] = None
    description: Optional[str] = None


class Property(BaseElement):
    value: Union[str, float, int]
    value_type: ValueType

    @model_validator(mode="after")
    def validate_value_type(self) -> Property:
        expected_type = VALUE_TYPE_TO_PYTHON[self.value_type]
        if not isinstance(self.value, expected_type):
            raise TypeError(
                f"value must be of type {expected_type.__name__} for value_type '{self.value_type}'"
            )
        return self


class SubmodelElementCollection(BaseElement):
    value: List[Union[Property, SubmodelElementCollection]]


class Submodel(BaseElement):
    id: str
    submodel_elements: List[Union[Property, SubmodelElementCollection]]


class AssetAdministrationShell(BaseModel):
    id: str
    id_short: str
    data_elements: List[Submodel]
