from typing import Optional, List, TypedDict


class Field(TypedDict):
    name: str
    type: Optional[str]
    is_mandatory: Optional[bool]
    is_available: Optional[bool]


class Resource(TypedDict):
    id: str
    title: str
    fields: Optional[List[Field]]
    required: Optional[bool]
    requires: Optional[List[str]]
