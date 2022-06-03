from datetime import datetime
from typing import TypedDict, Dict, List

from .errors.exceptions import WrongTypeOrValueError


class PanoplyMetadata(TypedDict):
    resource_id: str
    timestamp: str


class PanoplyRecord(TypedDict):
    data: Dict
    metadata: PanoplyMetadata


class PanoplyRecordGroup(TypedDict):
    data: List[Dict]
    metadata: PanoplyMetadata


def to_record(resource, data) -> PanoplyRecordGroup:
    """ Converts data and resource to RecordGroup object """
    validate_resource(resource)
    data = validate_and_transform_data_type(data)
    timestamp = get_iso_string()
    record_group = PanoplyRecordGroup(
        data=data,
        metadata={
            'resource_id': resource,
            'timestamp': timestamp,
        }
    )
    return record_group


def validate_resource(resource):
    if not isinstance(resource, str) or len(resource.strip()) == 0:
        raise WrongTypeOrValueError("`resource` must be a non empty string")


def validate_and_transform_data_type(data):
    if isinstance(data, list):
        if data and not isinstance(data[0], dict):
            raise WrongTypeOrValueError("Objects inside returned list should be of type dict.")
        return data
    elif isinstance(data, dict):
        return [data]
    else:
        raise WrongTypeOrValueError("The data returned should be of the type list or dict.")


def get_iso_string() -> str:
    now = datetime.now()
    return f"{now.isoformat(timespec='milliseconds')}Z"
