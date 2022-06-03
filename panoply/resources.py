from typing import Optional, List, TypedDict


class PanoplyField(TypedDict):
    name: str
    type: Optional[str]
    is_mandatory: Optional[bool]
    is_available: Optional[bool]


class PanoplyResource(TypedDict):
    id: str
    title: str
    fields: Optional[List[PanoplyField]]
    required: Optional[bool]
    requires: Optional[List[str]]
