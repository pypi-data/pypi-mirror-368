"""Library for converting Swagger objects to Python data types such as dataframes."""

import re
from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd

from rime_sdk.swagger.swagger_client.models import (
    RimeCategoryTestResult,
    TestrunresultTestBatchResult,
    TestrunresultTestCase,
    TestrunresultTestRunDetail,
)
from rime_sdk.swagger.swagger_client.models.detection_detection_event import (
    DetectionDetectionEvent,
)

MODEL_PERF_REGEX = r"^metrics\.model_perf.*(ref_metric|eval_metric)$"

# Map of flattened field paths to their types in the Dataframe.
TEST_RUN_COLUMN_TO_SHOW = {
    # Metadata.
    "test_run_id": "str",
    "name": "str",
    "project_id": "str",
    "model_task": "str",  # OPTIONAL
    # The canonical JSON encoding converts enums to their string representations
    # so we do not need to do manual conversions.
    "testing_type": "str",
    "upload_time": "str",
    # Metrics.
    "metrics.duration_millis": "Int64",
    "metrics.num_inputs": "Int64",
    "metrics.num_failing_inputs": "Int64",
    "metrics.summary_counts.total": "Int64",
    "metrics.summary_counts._pass": "Int64",
    "metrics.summary_counts.warning": "Int64",
    "metrics.summary_counts.fail": "Int64",
    "metrics.summary_counts.skip": "Int64",
    "metrics.severity_counts.num_none_severity": "Int64",
    "metrics.severity_counts.num_low_severity": "Int64",
    "metrics.severity_counts.num_high_severity": "Int64",
}

# List of all the columns to hide for a summary test DF.
SUMMARY_TEST_KEYS_TO_HIDE = [
    "category_metrics",
    "description",
    "duration",
    "suggestion",
]

# List of all the columns to hide for a test batch DF.
TEST_BATCH_KEYS_TO_HIDE = [
    "show_in_test_comparisons",
    "failing_rows_result",
    "display",
]

# List of all the columns to hide for a Test Case DF.
TEST_CASE_KEYS_TO_HIDE = [
    "display",
    "url_safe_feature_id",
    "test_case_id",
]

# TestBatchResult columns that need to be converted from string to int64
INT_TEST_BATCH_ATTRIBUTES = [
    "duration_in_millis",
    "summary_counts.total",
    "summary_counts.warning",
    "summary_counts._pass",
    "summary_counts.fail",
    "summary_counts.skip",
]

# Separator to use when flattening JSON into a dataframe.
# columns_to_keep definition relies on this separator.
DF_FLATTEN_SEPARATOR = "."

DATA_OPTIONS = [
    "float_value",
    "int_value",
    "str_value",
    "float_list",
    "int_list",
    "str_list",
]

EVENT_COLUMNS_TO_SHOW = [
    "project_id",
    "event_type",
    "severity",
    "event_object_name",
    "event_object_id",
    "risk_category_type",
    "test_category",
    "event_time_range.start_time",
    "event_time_range.end_time",
    "description",
    "detail.metric_degradation.rca_result.description",
]


def _flatten_uuid_field_name(field_name: str) -> str:
    """Flatten a UUID field name."""
    match = re.match(r"(.*)\.uuid$", field_name)
    if match is None:
        return field_name
    return match.groups()[0]


def parse_test_run_metadata(test_run: TestrunresultTestRunDetail) -> pd.DataFrame:
    """Parse test run metadata Swagger message into a Pandas dataframe.

    The columns are not guaranteed to be returned in sorted order.
    Some values are optional and will appear as a NaN value in the dataframe.

    """
    # Use the canonical JSON encoding for Protobuf messages.
    test_run_dict = test_run.to_dict()

    # Flatten out nested fields in the Protobuf message.
    # The DF column name will be the field path joined by the `df_flatten_separator.`
    normalized_df = pd.json_normalize(test_run_dict, sep=DF_FLATTEN_SEPARATOR)
    normalized_df = normalized_df.rename(_flatten_uuid_field_name, axis="columns")

    default_test_run_columns = list(TEST_RUN_COLUMN_TO_SHOW.keys())

    # Include the model perf columns with the set of DF columns.
    # These are metrics like "Accuracy" over the reference and eval datasets.
    model_perf_columns = [c for c in normalized_df if re.match(MODEL_PERF_REGEX, c)]
    all_test_run_columns = default_test_run_columns + model_perf_columns

    missing_columns = set(all_test_run_columns).difference(set(normalized_df.columns))
    intersect_df = normalized_df[
        normalized_df.columns.intersection(all_test_run_columns)
    ]

    # Fill in the missing columns with None values.
    kwargs: Dict[str, None] = {}
    for column in missing_columns:
        kwargs[column] = None
    # Note that this step does not preserve column order.
    full_df = intersect_df.assign(**kwargs)

    # The canonical Protobuf<>JSON encoding converts int64 values to string,
    # so we need to convert them back.
    # https://developers.google.com/protocol-buffers/docs/proto3#json
    # Note the type of all model perf metrics should be float64 so we do not have
    # to do this conversion.
    for key, value in TEST_RUN_COLUMN_TO_SHOW.items():
        if value == "Int64":
            # Some nested fields such as `metrics.severity_counts.low` will be `None`
            # because MessageToDict does not populate nested primitive fields with
            # default values.
            # Since some columns may be `None`, we must convert to `float` first.
            # https://stackoverflow.com/questions/60024262/error-converting-object-string-to-int32-typeerror-object-cannot-be-converted
            full_df[key] = full_df[key].astype("float").astype("Int64")

    # Fix an order for the index of the df.
    non_default_cols = list(
        set(all_test_run_columns).difference(set(default_test_run_columns))
    )
    ordered_index = pd.Index(default_test_run_columns + sorted(non_default_cols))
    return full_df.reindex(ordered_index, axis=1)


def parse_test_batch_result(
    raw_result: TestrunresultTestBatchResult,
    unpack_metrics: bool = False,
) -> pd.Series:
    """Parse test batch result into a series."""
    result_dict = raw_result.to_dict()
    del result_dict["metrics"]
    if unpack_metrics:
        _add_metric_cols(result_dict, raw_result)

    # Note: some keys may be missing for nested singular messages, so we do
    # a safe delete here.
    for key in TEST_BATCH_KEYS_TO_HIDE:
        result_dict.pop(key, None)

    df = pd.json_normalize(result_dict, sep=DF_FLATTEN_SEPARATOR)

    for key in INT_TEST_BATCH_ATTRIBUTES:
        # Some nested fields such as `metrics.severity_counts.low` will be `None`
        # because MessageToDict does not populate nested primitive fields with
        # default values.
        # Since some columns may be `None`, we must convert to `float` first.
        # https://stackoverflow.com/questions/60024262/error-converting-object-string-to-int32-typeerror-object-cannot-be-converted
        df[key] = df[key].astype("float").astype("Int64")

    return df.squeeze(axis=0)


def parse_test_case_result(
    raw_result: TestrunresultTestCase, unpack_metrics: bool = False
) -> dict:
    """Parse swagger Test Case result to pythonic form."""
    result_dict = raw_result.to_dict()
    del result_dict["metrics"]
    if unpack_metrics:
        _add_metric_cols(result_dict, raw_result)

    # Drop the keys to hide if they are specified.
    # Note: some keys may be missing for nested singular messages, so we do
    # a safe delete here.
    for key in TEST_CASE_KEYS_TO_HIDE:
        result_dict.pop(key, None)

    return result_dict


def _add_metric_cols(
    result_dict: dict,
    raw_result: Union[TestrunresultTestCase, TestrunresultTestBatchResult],
) -> None:
    """Unpack test metrics into separate fields."""
    if raw_result.metrics:
        for metric in raw_result.metrics:
            category_string = metric.category
            if category_string:
                prefix = "TEST_METRIC_CATEGORY_"
                category_string = category_string[len(prefix) :]
                metric_value: Any = np.nan
                if metric.empty:
                    pass
                else:
                    for data_option in DATA_OPTIONS:
                        getter = getattr(metric, data_option)
                        if getter is not None:
                            metric_value = getter
                            break
                result_dict[f"{category_string}:{metric.metric}"] = metric_value


def parse_category_test_results(
    raw_result: RimeCategoryTestResult,
    unpack_metrics: bool = False,
) -> dict:
    """Parse swagger summary test result to pythonic form."""
    raw_dict = raw_result.to_dict()
    for key in SUMMARY_TEST_KEYS_TO_HIDE:
        raw_dict.pop(key, None)
    if unpack_metrics:
        for metric in raw_result.category_metrics:
            raw_dict[metric.name] = metric.value
    severity_count_dict = raw_dict.pop("severity_counts")
    for key in severity_count_dict:
        raw_dict[key] = int(severity_count_dict[key])
    return raw_dict


def parse_events_to_df(
    events: List[DetectionDetectionEvent],
) -> pd.DataFrame:
    """Parse a list of Detection Events to a pandas DateFrame."""
    event_dicts = [event.to_dict() for event in events]
    df = pd.json_normalize(event_dicts, sep=DF_FLATTEN_SEPARATOR)
    df = df.rename(_flatten_uuid_field_name, axis="columns")

    intersect_df = df[df.columns.intersection(EVENT_COLUMNS_TO_SHOW)]
    intersect_df = intersect_df.rename({"event_object_id": "monitor_id"}, axis=1)

    return intersect_df
