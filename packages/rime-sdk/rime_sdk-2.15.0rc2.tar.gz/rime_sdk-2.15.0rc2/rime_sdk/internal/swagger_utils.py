"""Utility functions for converting between SDK args and proto objects."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, TypeVar

from google.protobuf.json_format import MessageToDict
from google.protobuf.timestamp_pb2 import Timestamp

from rime_sdk.swagger.swagger_client import RimeUUID


def swagger_is_empty(swagger_val: Any) -> bool:
    """Check if a swagger object is empty."""
    return not bool(swagger_val)


TYPE_KEY = "enum_type"
PROTO_FIELD_KEY = "proto_field"
PROTO_TYPE_KEY = "proto_type"

BASE_TYPES = ["str", "float", "int", "bool"]

T = TypeVar("T")


def parse_dict_to_swagger(obj_dict: Optional[Dict], new_obj: T) -> T:
    """Parse non-nested dicts into a new object."""
    if obj_dict:
        for key, value in obj_dict.items():
            setattr(new_obj, key, value)
    return new_obj


def parse_str_to_uuid(uuid_str: Optional[str]) -> Optional[RimeUUID]:
    """Parse a string into a RimeUUID."""
    if uuid_str:
        return RimeUUID(uuid_str)
    return None


def serialize_datetime_to_proto_timestamp(date: datetime) -> Dict:
    """Convert datetime to swagger compatible grpc timestamp."""
    timestamp = Timestamp()
    timestamp.FromDatetime(date)
    # Swagger serialize datetime to iso8601 format, convert to
    # protobuf compatible serialization
    return MessageToDict(timestamp)


def rest_to_timedelta(delta: str) -> timedelta:
    """Convert a REST API compatible string to a time delta."""
    # REST API returns a string in seconds; e.g. one day is represented as "86400s"
    return timedelta(seconds=int(delta[:-1]))


def timedelta_to_rest(delta: timedelta) -> str:
    """Convert a time delta to a REST API compatible string."""
    return f"{int(delta.total_seconds())}s"


def select_oneof(oneof_map: Dict[str, Any], key_list: List[str]) -> Any:
    """Select one of the keys in the map.

    Args:
        oneof_map: The map to select from.
        key_list: The list of keys to select from.

    Returns:
        The key that was selected.

    Raises:
        ValueError
            When more than one of the keys are provided in the map.
    """
    selected_key = None
    for key in key_list:
        if key in oneof_map:
            if selected_key is not None:
                raise ValueError(
                    f"More than one of the keys {key_list} were provided in the map."
                )
            selected_key = key
    if selected_key is None:
        raise ValueError(f"None of the keys {key_list} were provided in the map.")
    return selected_key
