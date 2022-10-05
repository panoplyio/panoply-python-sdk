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


def list_resources(resources: List[Resource]) -> Optional[List[Dict]]:
    if resources:
        return [
            {"name": resource["title"],
             "value": resource["id"],
             "disabled": not resource.get("available", True),
             "required": resource.get("required", False),
             "requires": resource.get("requires", [])}
            for resource in resources]
    else:
        return


def list_fields(fields: List[Field]) -> Optional[List[Dict]]:
    if fields:
        return [
            {"name": f"{field['name']} [{field['type']}]" if field.get("type") else field["name"],
             "value": field["name"],
             "type": field.get("type"),
             "is_mandatory": field.get("is_mandatory", False),
             "disabled": not field.get("is_available", True)}
            for field in fields]
    else:
        return
