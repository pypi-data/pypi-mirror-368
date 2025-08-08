"""Library defining the interface to Data Collector."""

import base64
import itertools
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Iterable, Iterator, List, Optional, Union

from rime_sdk.internal.rest_error_handler import RESTErrorHandler
from rime_sdk.internal.swagger_utils import serialize_datetime_to_proto_timestamp
from rime_sdk.swagger import swagger_client
from rime_sdk.swagger.swagger_client import (
    ApiClient,
    PredictionsModelIdUuidBody,
    RimeStorePredictionsRequestPrediction,
)
from rime_sdk.swagger.swagger_client.models import (
    DatacollectorDatapointRow,
    DataDataStreamIdUuidBody,
    DatastreamProjectIdUuidBody,
    RimeUUID,
)

logger = logging.getLogger(__name__)

GRPC_MAX_BYTES_SIZE = 50_000


class DatapointIterator:
    """Iterator that transforms an iterator of inputs to datapoints."""

    def __init__(self, it: Iterator):
        """Initialize iterator."""
        self.it = it

    def __iter__(self) -> Iterator:
        """Return iterator."""
        return self

    def __next__(self) -> DatacollectorDatapointRow:
        """Take next datapoint and convert to proto datapoint."""
        input_data, label, timestamp, query_id = self.it.__next__()
        return convert_input_to_datapoint(input_data, timestamp, label, query_id)


def convert_input_to_datapoint(
    input_data: Dict,
    timestamp: Optional[datetime] = None,
    label: Optional[Union[Dict, int, float]] = None,
    query_id: Optional[Union[str, float, int]] = None,
) -> DatacollectorDatapointRow:
    """Convert input data to a datapoint."""
    datapoint = DatacollectorDatapointRow(
        input_data=json_serialize(input_data),
    )
    if label is not None:
        datapoint.label = json_serialize(label)
    if query_id is not None:
        datapoint.query_id = json_serialize(query_id)
    if timestamp is not None:
        datapoint.timestamp = serialize_datetime_to_proto_timestamp(timestamp)
    return datapoint


def json_serialize(serialize_object: Any) -> str:
    """Encode using UTF-8 or return as None."""
    return base64.b64encode(json.dumps(serialize_object).encode("utf-8")).decode(
        "utf-8"
    )


def validate_log_datapoints(
    inputs: List[Dict], lists_to_validate: List[Optional[List]], list_names: List[str]
) -> None:
    """Create string message with everything wrong with inputs to log datapoints.

    Returns None if no errors.
    """
    input_len = len(inputs)

    for index, elements in enumerate(lists_to_validate):
        if elements is not None and len(elements) != input_len:
            error_str = (
                "Size Mismatch in {}: {} data points, {} {}".format(  # noqa: UP032
                    list_names[index], input_len, len(elements), list_names[index]
                )
            )
            raise ValueError(error_str)


class DataCollector:
    """An interface to a Data Collector.

    A Data Collector allows users to log datapoints to be used in RIME
    at either a datapoint or batch level in a continuous stream.
    """

    def __init__(self, api_client: ApiClient, project_id: str) -> None:
        """Create a new Data Collector wrapper object.

        Arguments:
            api_client: ApiClient
                The client used to query the RIME cluster.
            project_id: str
                The Project ID associated with the Data Collector.
        """
        self._api_client = api_client
        self._project_id = project_id

    def register_data_stream(self) -> str:
        """Register a data stream with the Data Collector.

        A data stream is a location to which data can be uploaded.

        Returns:
            str:
                The ID of the registered data stream.
        """
        req = DatastreamProjectIdUuidBody(project_id=RimeUUID(self._project_id))
        with RESTErrorHandler():
            api = swagger_client.DataCollectorApi(self._api_client)
            res = api.register_data_stream(
                body=req,
                project_id_uuid=self._project_id,
            )
        return res.data_stream_id.uuid

    def _upload_datapoints_with_buffer(
        self, data_stream_id: str, datapoints: Iterator[DatacollectorDatapointRow]
    ) -> List[str]:
        """Upload a list of Data Collector datapoints, buffering message size."""
        datapoint_list: List[DatacollectorDatapointRow] = []
        datapoint_ids: List[RimeUUID] = []

        bytes_counter = 0

        # Parse through datapoints, uploading the max amount that GRPC supports
        # each time
        with RESTErrorHandler():
            api = swagger_client.DataCollectorApi(self._api_client)
            for datapoint in datapoints:
                # Request will error if a single datapoint is too large
                # This is OK because if it does, it means that the user
                # is using the product in a way we don't currently want to support
                # 4MB GRPC Message limit is large enough
                if bytes_counter + sys.getsizeof(datapoint) > GRPC_MAX_BYTES_SIZE:
                    req = DataDataStreamIdUuidBody(
                        data_stream_id=RimeUUID(data_stream_id),
                        datapoints=datapoint_list,
                    )
                    with RESTErrorHandler():
                        resp = api.store_datapoints(
                            data_stream_id_uuid=data_stream_id,
                            body=req,
                        )
                        datapoint_ids.extend(resp.datapoint_ids)
                    datapoint_list = []
                    bytes_counter = 0

                datapoint_list.append(datapoint)
                bytes_counter += sys.getsizeof(datapoint)
            # Upload remaining datapoints
            if len(datapoint_list) > 0:
                req = DataDataStreamIdUuidBody(
                    data_stream_id=RimeUUID(data_stream_id),
                    datapoints=datapoint_list,
                )
                with RESTErrorHandler():
                    resp = api.store_datapoints(
                        data_stream_id_uuid=data_stream_id, body=req
                    )
                    datapoint_ids.extend(resp.datapoint_ids)
        return [datapoint_id.uuid for datapoint_id in datapoint_ids]

    def log_datapoints(
        self,
        data_stream_id: str,
        inputs: List[Dict],
        timestamps: Optional[List[datetime]] = None,
        labels: Optional[List[Union[Dict, int, float]]] = None,
        query_ids: Optional[List[Union[str, float, int]]] = None,
    ) -> List[str]:
        """Log datapoints in batches.

        Args:
            data_stream_id: str
                The ID of the data stream to log the datapoints.
            inputs: List[Dict]
                List of inputs to log to the Data Collector. Provide each input
                should as a dictionary. Feature names are dictionary keys, with
                their corresponding values.
            timestamps: Optional[List[datetime]]
                List of optional timestamps associated with each input. The default
                value is the timestamp when the log_datapoints method is called.
            labels: Optional[List[Union[Dict, int, float]]]
                List of optional labels associated with each input.
            query_ids: Optional[List[Union[str, float, int]]]
                List of optional query IDs associated with each input. This parameter
                is only relevant for ranking use cases.

        Returns:
            List[str]:
                List of the logged datapoint IDs.

        Raises:
            ValueError
                This error is generated when the length of the inputs, timestamps,
                labels, or query_ids lists are not equal.

        Example:
        This example registers a data stream and logs two datapoints to the
        registered data stream.

        .. code-block:: python

            data_stream_id = data_collector.register_data_stream()
            datapoint_ids = data_collector.log_datapoints(
            data_stream_id=data_stream_id,
                inputs=[
                    {"feature_1": 1, "feature_2": 2},
                    {"feature_1": 3, "feature_2": 4},
                ],
                timestamps=[
                    datetime(2020, 1, 1, 0, 0, 0),
                    datetime(2020, 1, 1, 0, 0, 1),
                ],
                labels=[{"label": "label_1"}, {"label": "label_2"}],
            )
        """
        # Validate Datapoint List
        validate_log_datapoints(
            inputs,
            [labels, timestamps, query_ids],
            ["labels", "timestamps", "query_ids"],
        )
        print("Logging datapoints...")

        # Easier for looping through options
        it_timestamps: Iterable[Any] = timestamps or itertools.repeat(None)
        it_labels: Iterable[Any] = labels or itertools.repeat(None)
        it_queries: Iterable[Any] = query_ids or itertools.repeat(None)

        data_vals = zip(
            inputs,
            it_labels,
            it_timestamps,
            it_queries,
        )
        datapoint_iterator = DatapointIterator(iter(data_vals))
        return self._upload_datapoints_with_buffer(data_stream_id, datapoint_iterator)

    def log_predictions(
        self, model_id: str, datapoint_ids: List[str], predictions: List[Dict]
    ) -> None:
        """Log predictions to the Data Collector.

        Args:
            model_id: str
                The ID of the model to log the predictions.
            datapoint_ids: List[str]
                List of datapoint IDs associated with each prediction.
            predictions: List[Dict]
                List of predictions to log to the Data Collector. Provide each
                prediction as a dictionary. Feature names are dictionary keys,
                with their corresponding values.

        Raises:
            ValueError
                This error is generated when the length of the datapoint_ids and
                predictions lists are not equal.

        Example:
        This example logs two predictions to the Data Collector.

        .. code-block:: python

            data_collector.log_predictions(
                model_id="model_id",
                datapoint_ids=["datapoint_id_1", "datapoint_id_2"],
                predictions=[
                    {"prediction": "prediction_1"}, {"prediction": "prediction_2"}
                ],
            )
        """
        if len(datapoint_ids) != len(predictions):
            raise ValueError(
                f"The length of the datapoint_ids and predictions lists must be equal."
                f"Received {len(datapoint_ids)} datapoint_ids and "
                f"{len(predictions)} predictions."
            )
        print("Logging predictions...")
        api = swagger_client.DataCollectorApi(self._api_client)
        preds_list: List[RimeStorePredictionsRequestPrediction] = []
        bytes_counter = 0
        for datapoint_id, prediction in zip(datapoint_ids, predictions):
            pred = RimeStorePredictionsRequestPrediction(
                datapoint_id=RimeUUID(datapoint_id),
                prediction=json_serialize(prediction),
            )
            preds_list.append(pred)
            bytes_counter += sys.getsizeof(pred)
            if bytes_counter + sys.getsizeof(pred) > GRPC_MAX_BYTES_SIZE:
                with RESTErrorHandler():
                    req = PredictionsModelIdUuidBody(
                        model_id=RimeUUID(model_id),
                        predictions=preds_list,
                    )
                    api.store_predictions(
                        body=req,
                        model_id_uuid=model_id,
                    )

                preds_list = []
                bytes_counter = 0
        if len(preds_list) > 0:
            with RESTErrorHandler():
                req = PredictionsModelIdUuidBody(
                    model_id=RimeUUID(model_id),
                    predictions=preds_list,
                )
                api.store_predictions(
                    body=req,
                    model_id_uuid=model_id,
                )
