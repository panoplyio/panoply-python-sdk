from typing import Optional, List, TypedDict, Dict


class Field(TypedDict):
    name: str
    type: Optional[str]
    is_mandatory: Optional[bool]
    is_available: Optional[bool]


class Resource(TypedDict):
    id: str
    title: str
    fields: Optional[List[Field]]
    available: Optional[bool]
    required: Optional[bool]
    requires: Optional[List[str]]


def convert_to_ui_format(items, create_name, create_value,
                         is_disabled=lambda item: False, requires=lambda item: []):
    if items:
        return [
            {"name": create_name(item),
             "value": create_value(item),
             "disabled": is_disabled(item),
             "requires": requires(item)
             }
            for item in items]
    else:
        return
