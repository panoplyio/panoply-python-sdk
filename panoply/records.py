from datetime import datetime
from typing import TypedDict, Dict, List


class Metadata(TypedDict):
    resource_id: str
    timestamp: str


class Record(TypedDict):
    data: Dict
    metadata: Metadata


class RecordGroup(TypedDict):
    data: List[Dict]
    metadata: Metadata


def to_record(resource, data) -> RecordGroup:
    """ Converts data and resource to RecordGroup object """
    validate_resource(resource)
    data = normalize_data(data)
    timestamp = get_iso_string()
    record_group = RecordGroup(
        data=data,
        metadata={
            'resource_id': resource,
            'timestamp': timestamp,
        }
    )
    return record_group


def validate_resource(resource):
    if not isinstance(resource, str):
        raise TypeError("`resource` must be of a type string")
    if len(resource.strip()) == 0:
        raise ValueError("`resource` must be a non empty string")


def normalize_data(data):
    if isinstance(data, list):
        if data and not isinstance(data[0], dict):
            raise TypeError("Objects inside returned list should be of type dict.")
        return data
    elif isinstance(data, dict):
        return [data]
    else:
        raise TypeError("The data returned should be of the type list or dict.")


def get_iso_string() -> str:
    now = datetime.utcnow()
    return f"{now.isoformat(timespec='milliseconds')}Z"
