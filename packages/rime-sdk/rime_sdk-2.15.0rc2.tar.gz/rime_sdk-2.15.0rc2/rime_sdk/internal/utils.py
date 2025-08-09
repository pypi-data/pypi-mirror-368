"""General Utilities."""

from html import escape
from typing import Any, Dict, List, Optional, Sequence

from google.protobuf.field_mask_pb2 import FieldMask
from google.protobuf.json_format import MessageToDict

HEADER_TMPL = "<th>{0}</th>"
DATA_TMPL = "<td>{0}</td>"
ROW_TMPL = "<tr>{0}</tr>"
TABLE_TMPL = '<table style="width:100%">{0}</table>'


def make_link(link: str, link_text: Optional[str] = None) -> str:
    """Make the HTML link."""
    if not link_text:
        link_text = "Link"
    return f'<a href="{link}" target="_blank" rel="noopener">{escape(link_text)}</a>'


def get_header_row_string(column_headers: Sequence[str]) -> str:
    """Return the table header row as a sring."""
    headers = [HEADER_TMPL.format(header) for header in column_headers]
    return ROW_TMPL.format("".join(headers))


def get_data_row_string(data_values: Sequence[str]) -> str:
    """Return a table data row as a string."""
    data = [DATA_TMPL.format(datum) for datum in data_values]
    return ROW_TMPL.format("".join(data))


def convert_dict_to_html(table_dict: Dict[str, str]) -> str:
    """Convert a dictionary to an HTML table."""
    if len(table_dict) == 0:
        return ""

    all_rows = [
        get_header_row_string(list(table_dict)),
        get_data_row_string(list(table_dict.values())),
    ]
    return TABLE_TMPL.format("".join(all_rows))


def assert_and_get_none_or_all_none(*args: Optional[Any]) -> bool:
    """Check that all arguments are None or all are not None.

    Args:
        *args: Arguments to check.

    Returns:
        True if all arguments are not None, False if all are None.

    Raises:
        ValueError
            When some arguments are None and some are not.
    """
    if all(arg is None for arg in args):
        return False
    elif all(arg is not None for arg in args):
        return True
    else:
        raise ValueError(f"All arguments {args} must be None or all must be not None.")


def _get_field_mask_paths(v: Any, path_elements: List[str]) -> List[str]:
    """Get the field mask paths for a swagger object where the values are non-null."""
    if v is None:
        return []
    if not isinstance(v, dict):
        return [".".join(path_elements)]
    mask_paths = []
    for key, val in v.items():
        mask_paths += _get_field_mask_paths(val, path_elements + [key])
    return mask_paths


def get_swagger_field_mask(swagger_object: Any) -> dict:
    """Get a field mask for a swagger object that recursively masks non-null fields."""
    mask_paths = _get_field_mask_paths(swagger_object.to_dict(), [])
    mask = FieldMask(paths=mask_paths)
    serialized_mask = MessageToDict(mask)
    return serialized_mask


def is_positive_number(v: Any) -> bool:
    """Check that the provided variable is a positive number."""
    return isinstance(v, (int, float)) and v > 0


def remove_null_values_from_dict(d: dict) -> None:
    """Remove null values from a dictionary in place."""
    # Need to convert items to list because we are mutating the dictionary during
    # iteration, and the `dict_items` actually shares memory with the underlying dict.
    for k, v in list(d.items()):
        if v is None:
            del d[k]
        if isinstance(v, dict):
            remove_null_values_from_dict(v)
        if isinstance(v, list):
            # Want to recursively apply to dicts within a list, but don't want to
            # remove None values from the list itself.
            for item in v:
                if isinstance(item, dict):
                    remove_null_values_from_dict(item)
