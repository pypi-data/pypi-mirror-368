"""Library that defines the interface to the Registry."""

import json
import logging
from http import HTTPStatus
from typing import Dict, Iterator, List, Optional, Tuple

from deprecated import deprecated

from rime_sdk.internal.config_parser import (
    convert_model_info_to_swagger,
    convert_single_data_info_to_swagger,
    convert_single_pred_info_to_swagger,
)
from rime_sdk.internal.rest_error_handler import RESTErrorHandler
from rime_sdk.internal.swagger_utils import serialize_datetime_to_proto_timestamp
from rime_sdk.job import Job
from rime_sdk.swagger import swagger_client
from rime_sdk.swagger.swagger_client import (
    ApiClient,
    DatasetCTDatasetType,
    DatasetCTInfo,
)
from rime_sdk.swagger.swagger_client.models import (
    DatasetIdPredictionBody,
    ProjectIdUuidDatasetBody,
    ProjectIdUuidModelBody,
    RegistryMetadata,
    RegistryValidityStatus,
    RimeGetDatasetResponse,
    RimeGetModelResponse,
    RimeGetPredictionSetResponse,
    RimeListDatasetsResponse,
    RimeListModelsResponse,
    RimeListPredictionSetsResponse,
    RimeRegisterDatasetResponse,
    RimeRegisterModelResponse,
    RimeRegisterPredictionSetResponse,
    RimeUUID,
)
from rime_sdk.swagger.swagger_client.rest import ApiException

logger = logging.getLogger(__name__)


class Registry:
    """An interface to a RIME Registry."""

    def __init__(self, api_client: ApiClient) -> None:
        """Create a new Registry object.

        Arguments:
            api_client: ApiClient
                The client used to query the RIME cluster.
        """
        self._api_client = api_client

    @deprecated(
        "register_dataset is replaced by register_and_validate_dataset and will be removed in a future release."
        + "Note: the new method returns a tuple."
    )
    def register_dataset(
        self,
        project_id: str,
        name: str,
        data_config: dict,
        integration_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        ct_info: Optional[dict] = None,
        skip_validation: Optional[bool] = False,  # noqa: ARG002
        agent_id: Optional[str] = None,
    ) -> str:
        """Register and validate a new dataset in a Project.

        Args:
            project_id: str
                The ID of the Project in which to register the dataset.
            name: str
                The chosen name of the dataset.
            data_config: dict
                A dictionary that contains the data configuration.
                The data configuration must match the API specification
                of the `data_info` field in the `RegisterDataset` request.
            integration_id: Optional[str] = None,
                Provide the integration ID for datasets that require an integration.
            tags: Optional[List[str]] = None,
                An optional list of tags to associate with the dataset.
            metadata: Optional[dict] = None,
                An optional dictionary of metadata to associate with the dataset.
            ct_info: Optional[dict] = None,
                An optional dictionary that contains the CT info.
                The CT info must match the API specification of the `ct_info`
                field in the `RegisterDataset` request.
            skip_validation: Optional[bool] = False,
                The param is deprecated, validate is always performed.
            agent_id: Optional[str] = None,
                Agent for running validation. If omitted the workspace's default
                agent will be used.

        Returns:
            str:
                The ID of the newly registered dataset.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.

        Example:
            .. code-block:: python

                dataset_id = registry.register_dataset(
                    name=DATASET_NAME,
                    data_config={
                        "connection_info": {"data_file": {"path": FILE_PATH}},
                        "data_params": {"label_col": LABEL_COL},
                    },
                    integration_id=INTEGRATION_ID,
                )
        """
        dataset_id, _ = self.register_and_validate_dataset(
            project_id=project_id,
            name=name,
            data_config=data_config,
            integration_id=integration_id,
            tags=tags,
            metadata=metadata,
            ct_info=ct_info,
            agent_id=agent_id,
        )
        return dataset_id

    def register_and_validate_dataset(
        self,
        project_id: str,
        name: str,
        data_config: dict,
        integration_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        ct_info: Optional[dict] = None,
        agent_id: Optional[str] = None,
    ) -> Tuple[str, Optional[Job]]:
        """Register and validate a new dataset in a Project.

        Args:
            project_id: str
                The ID of the Project in which to register the dataset.
            name: str
                The chosen name of the dataset.
            data_config: dict
                A dictionary that contains the data configuration.
                The data configuration must match the API specification
                of the `data_info` field in the `RegisterDataset` request.
            integration_id: Optional[str] = None,
                Provide the integration ID for datasets that require an integration.
            tags: Optional[List[str]] = None,
                An optional list of tags to associate with the dataset.
            metadata: Optional[dict] = None,
                An optional dictionary of metadata to associate with the dataset.
            ct_info: Optional[dict] = None,
                An optional dictionary that contains the CT info.
                The CT info must match the API specification of the `ct_info`
                field in the `RegisterDataset` request.
            agent_id: Optional[str] = None,
                Agent for running validation. If omitted the workspace's default
                agent will be used.

        Returns:
            Tuple[str, Optional[Job]]:
                The returned Tuple contains the ID of the newly registered
                dataset and the Job object that represents the validation job.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.

        Example:
            .. code-block:: python

                dataset_id = registry.register_dataset(
                    name=DATASET_NAME,
                    data_config={
                        "connection_info": {"data_file": {"path": FILE_PATH}},
                        "data_params": {"label_col": LABEL_COL},
                    },
                    integration_id=INTEGRATION_ID,
                )
        """
        data_info_swagger = convert_single_data_info_to_swagger(data_config)
        req = ProjectIdUuidDatasetBody(
            project_id=RimeUUID(uuid=project_id),
            name=name,
            data_info=data_info_swagger,
            agent_id=RimeUUID(agent_id) if agent_id else None,
        )

        metadata_str: Optional[str] = None
        if metadata is not None:
            metadata_str = json.dumps(metadata)
        if tags is not None or metadata_str is not None:
            req.metadata = RegistryMetadata(tags=tags, extra_info=metadata_str)

        if integration_id is not None:
            req.integration_id = RimeUUID(uuid=integration_id)

        if ct_info is not None:
            req.ct_info = DatasetCTInfo(
                firewall_id=RimeUUID(uuid=ct_info["firewall_id"]),
                start_time=serialize_datetime_to_proto_timestamp(ct_info["start_time"]),
                end_time=serialize_datetime_to_proto_timestamp(ct_info["end_time"]),
                ct_dataset_type=DatasetCTDatasetType.USER_SPECIFIED,
            )

        with RESTErrorHandler():
            api = swagger_client.RegistryServiceApi(self._api_client)
            res: RimeRegisterDatasetResponse = api.register_dataset(
                body=req,
                project_id_uuid=project_id,
            )

        return (
            res.dataset_id,
            (
                Job(self._api_client, res.registry_validation_job_id.uuid)
                if res.registry_validation_job_id
                else None
            ),
        )

    @deprecated(
        "register_model is replaced by register_and_validate_model and will be removed in a future release.  "
        "Note: the new method returns a tuple."
    )
    def register_model(
        self,
        project_id: str,
        name: str,
        model_config: Optional[dict] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        external_id: Optional[str] = None,
        integration_id: Optional[str] = None,
        model_endpoint_integration_id: Optional[str] = None,
        skip_validation: Optional[bool] = False,  # noqa: ARG002
        agent_id: Optional[str] = None,
    ) -> str:
        """Register and validate a new model in a Project.

        Args:
            project_id: str
                The ID of the Project in which to register the model.
            name: str
                The chosen name of the model.
            model_config: Optional[dict] = None,
                A dictionary that contains the model configuration.
                Any model configuration that is provided must match the API
                specification for the `model_info` field of the `RegisterModel`
                request.
            tags: Optional[List[str]] = None,
                An optional list of tags to associate with the model.
            metadata: Optional[dict] = None,
                An optional dictionary of metadata to associate with the model.
            external_id: Optional[str] = None,
                An optional external ID that can be used to identify the model.
            integration_id: Optional[str] = None,
                Provide the integration ID for models that require an
                integration for access.
            model_endpoint_integration_id: Optional[str] = None,
                Provide the integration ID for models that require an
                integration when running the model.
            skip_validation: Optional[bool] = False,
                The param is deprecated, validate is always performed.
            agent_id: Optional[str] = None,
                Agent for running validation. If omitted the workspace's default
                agent will be used.

        Returns:
            str:
                The ID of the newly registered model.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.

        Example:
            .. code-block:: python

                model_id = registry.register_model(
                    name=MODEL_NAME,
                    model_config={
                        "hugging_face": {
                            "model_uri": URI,
                            "kwargs": {
                                "tokenizer_uri": TOKENIZER_URI,
                                "class_map": MAP,
                                "ignore_class_names": True,
                            },
                        }
                    },
                    tags=[MODEL_TAG],
                    metadata={KEY: VALUE},
                    external_id=EXTERNAL_ID,
                    agent_id=AGENT_ID,
                )
        """
        model_id, _ = self.register_and_validate_model(
            project_id=project_id,
            name=name,
            model_config=model_config,
            tags=tags,
            metadata=metadata,
            external_id=external_id,
            integration_id=integration_id,
            model_endpoint_integration_id=model_endpoint_integration_id,
            agent_id=agent_id,
        )
        return model_id

    def register_and_validate_model(
        self,
        project_id: str,
        name: str,
        model_config: Optional[dict] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        external_id: Optional[str] = None,
        integration_id: Optional[str] = None,
        model_endpoint_integration_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> Tuple[str, Optional[Job]]:
        """Register and validate a new model in a Project.

        Args:
            project_id: str
                The ID of the Project in which to register the model.
            name: str
                The chosen name of the model.
            model_config: Optional[dict] = None,
                A dictionary that contains the model configuration.
                Any model configuration that is provided must match the API
                specification for the `model_info` field of the `RegisterModel`
                request.
            tags: Optional[List[str]] = None,
                An optional list of tags to associate with the model.
            metadata: Optional[dict] = None,
                An optional dictionary of metadata to associate with the model.
            external_id: Optional[str] = None,
                An optional external ID that can be used to identify the model.
            integration_id: Optional[str] = None,
                Provide the integration ID for models that require an
                integration for access.
            model_endpoint_integration_id: Optional[str] = None,
                Provide the integration ID for models that require an
                integration when running the model.
            agent_id: Optional[str] = None,
                Agent for running validation. If omitted the workspace's default
                agent will be used.

        Returns:
            Tuple[str, Optional[Job]]:
                The returned Tuple contains the ID of the newly registered
                dataset and the Job object that represents the validation job.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.

        Example:
            .. code-block:: python

                model_id = registry.register_model(
                    name=MODEL_NAME,
                    model_config={
                        "hugging_face": {
                            "model_uri": URI,
                            "kwargs": {
                                "tokenizer_uri": TOKENIZER_URI,
                                "class_map": MAP,
                                "ignore_class_names": True,
                            },
                        }
                    },
                    tags=[MODEL_TAG],
                    metadata={KEY: VALUE},
                    external_id=EXTERNAL_ID,
                    agent_id=AGENT_ID,
                )
        """
        req = ProjectIdUuidModelBody(
            project_id=RimeUUID(uuid=project_id),
            name=name,
            agent_id=RimeUUID(agent_id) if agent_id else None,
        )

        if model_config is not None:
            # When the `model_path` key is provided to the dictionary, the value
            # must be a dictionary whose `path` value points to a python
            # file that holds a `predict_dict` or `predict_df` function.
            # When the `model_loading` key is provided to the dictionary, the value
            # must be a dictionary whose `path` value points to a python
            # file that holds a `get_predict_df` or `get_predict_dict` function and
            # whose value for the `params` key is a dictionary of parameters to
            # pass to the function.
            # When the `hugging_face` key is provided to the dictionary, the value must
            # be a dictionary whose `model_uri` value points to a
            # hugging face model and whose value for the `params` key is a dictionary
            # of parameters that hugging face model requires.
            model_info = convert_model_info_to_swagger(model_config)
            req.model_info = model_info

        metadata_str: Optional[str] = None
        if metadata:
            metadata_str = json.dumps(metadata)
        if tags or metadata_str:
            req.metadata = RegistryMetadata(tags=tags, extra_info=metadata_str)
        if external_id:
            req.external_id = external_id
        if integration_id is not None:
            req.integration_id = RimeUUID(uuid=integration_id)
        if model_endpoint_integration_id is not None:
            req.model_endpoint_integration_id = RimeUUID(
                uuid=model_endpoint_integration_id
            )

        with RESTErrorHandler():
            api = swagger_client.RegistryServiceApi(self._api_client)
            res: RimeRegisterModelResponse = api.register_model(
                body=req,
                project_id_uuid=project_id,
            )

        return (
            res.model_id.uuid,
            (
                Job(self._api_client, res.registry_validation_job_id.uuid)
                if res.registry_validation_job_id
                else None
            ),
        )

    @deprecated(
        "register_predictions is replaced by register_and_validate_prediction and will be removed in a future "
        + "release. Note: the new method returns a tuple."
    )
    def register_predictions(
        self,
        project_id: str,
        dataset_id: str,
        model_id: str,
        pred_config: dict,
        integration_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        skip_validation: Optional[bool] = False,  # noqa: ARG002
        agent_id: Optional[str] = None,
    ) -> None:
        """Register and validate a new set of predictions for a model and a dataset.

        Args:
            project_id: str
                The ID of the Project to which the models belong.
            dataset_id: str,
                The ID of the dataset used to generate the predictions.
            model_id: str,
                The ID of the model used to generate the predictions.
            pred_config: dict,
                A dictionary that contains the prediction configuration.
                The prediction configuration must match the API specification
                for the `pred_info` field of the `RegisterPredictions` request.
            integration_id: Optional[str] = None,
                Provide the integration ID for predictions that require an
                integration to use.
            tags: Optional[List[str]] = None,
                An optional list of tags to associate with the predictions.
            metadata: Optional[dict] = None,
                An optional dictionary of metadata to associate with the predictions.
            skip_validation: Optional[bool] = False,
                The param is deprecated, validate is always performed.
            agent_id: Optional[str] = None,
                Agent for running validation. If omitted the workspace's default
                agent will be used.

        Returns:
            None

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.

        Example:
            .. code-block:: python

                registry.register_predictions(
                    dataset_id=DATASET_ID,
                    model_id=MODEL_ID,
                    pred_config={
                        "connection_info": {
                            "databricks": {
                                # Unix timestamp equivalent to 02/08/2023
                                "start_time": 1675922943,
                                # Unix timestamp equivalent to 03/08/2023
                                "end_time": 1678342145,
                                "table_name": TABLE_NAME,
                                "time_col": TIME_COL,
                            },
                        },
                        "pred_params": {"pred_col": PREDS},
                    },
                    tags=[TAG],
                    metadata={KEY: VALUE},
                )
        """
        self.register_and_validate_predictions(
            project_id=project_id,
            dataset_id=dataset_id,
            model_id=model_id,
            pred_config=pred_config,
            integration_id=integration_id,
            tags=tags,
            metadata=metadata,
            agent_id=agent_id,
        )

    def register_and_validate_predictions(
        self,
        project_id: str,
        dataset_id: str,
        model_id: str,
        pred_config: dict,
        integration_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        agent_id: Optional[str] = None,
    ) -> Optional[Job]:
        """Register and validate a new set of predictions for a model and a dataset.

        Args:
            project_id: str
                The ID of the Project to which the models belong.
            dataset_id: str,
                The ID of the dataset used to generate the predictions.
            model_id: str,
                The ID of the model used to generate the predictions.
            pred_config: dict,
                A dictionary that contains the prediction configuration.
                The prediction configuration must match the API specification
                for the `pred_info` field of the `RegisterPredictions` request.
            integration_id: Optional[str] = None,
                Provide the integration ID for predictions that require an
                integration to use.
            tags: Optional[List[str]] = None,
                An optional list of tags to associate with the predictions.
            metadata: Optional[dict] = None,
                An optional dictionary of metadata to associate with the predictions.
            agent_id: Optional[str] = None,
                Agent for running validation. If omitted the workspace's default
                agent will be used.

        Returns:
            job:
                The job object that represents the validation job.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.

        Example:
            .. code-block:: python

                registry.register_predictions(
                    dataset_id=DATASET_ID,
                    model_id=MODEL_ID,
                    pred_config={
                        "connection_info": {
                            "databricks": {
                                # Unix timestamp equivalent to 02/08/2023
                                "start_time": 1675922943,
                                # Unix timestamp equivalent to 03/08/2023
                                "end_time": 1678342145,
                                "table_name": TABLE_NAME,
                                "time_col": TIME_COL,
                            },
                        },
                        "pred_params": {"pred_col": PREDS},
                    },
                    tags=[TAG],
                    metadata={KEY: VALUE},
                )
        """
        pred_info_swagger = convert_single_pred_info_to_swagger(pred_config)

        req = DatasetIdPredictionBody(
            project_id=RimeUUID(uuid=project_id),
            model_id=RimeUUID(uuid=model_id),
            pred_info=pred_info_swagger,
            agent_id=RimeUUID(agent_id) if agent_id else None,
        )

        metadata_str: Optional[str] = None
        if metadata is not None:
            metadata_str = json.dumps(metadata)
        if tags is not None or metadata_str is not None:
            req.metadata = RegistryMetadata(tags=tags, extra_info=metadata_str)

        if integration_id is not None:
            req.integration_id = RimeUUID(uuid=integration_id)

        with RESTErrorHandler():
            api = swagger_client.RegistryServiceApi(self._api_client)
            res: RimeRegisterPredictionSetResponse = api.register_prediction_set(
                body=req,
                project_id_uuid=project_id,
                model_id_uuid=model_id,
                dataset_id=dataset_id,
            )
        return (
            Job(self._api_client, res.registry_validation_job_id.uuid)
            if res.registry_validation_job_id
            else None
        )

    def list_datasets(self, project_id: str) -> Iterator[Dict]:
        """Return a list of datasets.

        Args:
            project_id: str
                The ID of the Project to which the datasets belong.

        Returns:
            Iterator[Dict]:
                Iterator of dictionaries: each dictionary represents a
                dataset.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.
        """
        api = swagger_client.RegistryServiceApi(self._api_client)
        # Iterate through the pages of datasets and break at the last page.
        page_token = ""
        with RESTErrorHandler():
            while True:
                if page_token == "":
                    res: RimeListDatasetsResponse = api.list_datasets(
                        project_id_uuid=project_id
                    )
                else:
                    res = api.list_datasets(
                        project_id_uuid=project_id, page_token=page_token
                    )
                if res.datasets is not None:
                    for dataset in res.datasets:
                        yield dataset.to_dict()
                # Advance to the next page of datasets.
                page_token = res.next_page_token
                # we've reached the last page of datasets.
                if not res.has_more:
                    break

    def list_models(self, project_id: str) -> Iterator[Dict]:
        """Return a list of models.

        Args:
            project_id: str
                The ID of the Project to which the models belong.

        Returns:
            Iterator[Dict]:
                Iterator of dictionaries: each dictionary represents a
                model.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.
        """
        api = swagger_client.RegistryServiceApi(self._api_client)
        # Iterate through the pages of datasets and break at the last page.
        page_token = ""
        with RESTErrorHandler():
            while True:
                if page_token == "":
                    res: RimeListModelsResponse = api.list_models(
                        project_id_uuid=project_id
                    )
                else:
                    res = api.list_models(
                        project_id_uuid=project_id, page_token=page_token
                    )
                if res.models is not None:
                    for model in res.models:
                        yield model.model.to_dict()
                # Advance to the next page of models.
                page_token = res.next_page_token
                # we've reached the last page of models.
                if not res.has_more:
                    break

    def list_predictions(
        self,
        project_id: str,
        model_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
    ) -> Iterator[Dict]:
        """Return a list of prediction sets.

        Args:
            project_id: str
                The ID of the Project to which the models belong.
            model_id: Optional[str] = None
                The ID of the model to which the prediction sets belong.
            dataset_id: Optional[str] = None
                The ID of the dataset to which the prediction sets belong.

        Returns:
            Iterator[Dict]:
                Iterator of dictionaries: each dictionary represents a
                prediction set.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.
        """
        if model_id is not None and dataset_id is not None:
            raise ValueError("Only one of model_id or dataset_id can be set.")
        if model_id is None and dataset_id is None:
            raise ValueError("Must specify either a model_id or dataset_id.")
        else:
            pass
        api = swagger_client.RegistryServiceApi(self._api_client)
        # Iterate through the pages of datasets and break at the last page.
        page_token = ""
        with RESTErrorHandler():
            while True:
                if page_token == "":
                    if model_id is not None:
                        res: RimeListPredictionSetsResponse = api.list_prediction_sets(
                            project_id_uuid=project_id,
                            first_page_req_model_id=model_id,
                        )
                    else:
                        res = api.list_prediction_sets(
                            project_id_uuid=project_id,
                            first_page_req_dataset_id=dataset_id,
                        )
                else:
                    res = api.list_prediction_sets(
                        project_id_uuid=project_id,
                        page_token=page_token,
                    )
                if res.predictions is not None:
                    for prediction in res.predictions:
                        yield prediction.to_dict()
                # Advance to the next page of predictions.
                page_token = res.next_page_token
                # we've reached the last page of predictions.
                if not res.has_more:
                    break

    def get_dataset(
        self, dataset_id: Optional[str] = None, dataset_name: Optional[str] = None
    ) -> Dict:
        """Return a dataset.

        Args:
            dataset_id: str
                The ID of the dataset to retrieve.
            dataset_name: str
                The name of the dataset to retrieve.

        Returns:
            Dict:
                A dictionary representing the dataset.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.
        """
        if dataset_id is not None and dataset_name is not None:
            raise ValueError(
                "Arguments dataset_id and dataset_name"
                " are mutually exclusive.\n"
                f"Received dataset_id={dataset_id}"
                f" and dataset_name={dataset_name}."
            )
        elif dataset_name is None and dataset_id is None:
            raise ValueError("Must provide either dataset_id or dataset_name")
        api = swagger_client.RegistryServiceApi(self._api_client)
        with RESTErrorHandler():
            if dataset_id:
                res: RimeGetDatasetResponse = api.get_dataset(dataset_id=dataset_id)
            else:
                res = api.get_dataset(dataset_name=dataset_name)
        return res.dataset.to_dict()

    def has_dataset(
        self, dataset_id: Optional[str] = None, dataset_name: Optional[str] = None
    ) -> bool:
        """Return a boolean on whether the dataset is present.

        Args:
            dataset_id: Optional[str] = None
                The ID of the dataset to check for.
            dataset_name: Optional[str] = None
                The name of the dataset to check for.

        Returns:
            bool:
                A boolean on whether the dataset is present.

        Raises:
            ValueError
                This error is generated any error other than HTTPStatus.NOT_FOUND
                is returned from the Registry service.
        """
        if dataset_id is not None and dataset_name is not None:
            raise ValueError(
                "Arguments dataset_id and dataset_name"
                " are mutually exclusive.\n"
                f"Received dataset_id={dataset_id}"
                f" and dataset_name={dataset_name}."
            )
        elif dataset_name is None and dataset_id is None:
            raise ValueError("Must provide either dataset_id or dataset_name")
        api = swagger_client.RegistryServiceApi(self._api_client)
        with RESTErrorHandler():
            try:
                if dataset_id:
                    api.get_dataset(dataset_id=dataset_id)
                else:
                    api.get_dataset(dataset_name=dataset_name)
            except ApiException as e:
                if e.status == HTTPStatus.NOT_FOUND:
                    return False
                else:
                    raise e
        return True

    def get_model(
        self, model_id: Optional[str] = None, model_name: Optional[str] = None
    ) -> Dict:
        """Return a model.

        Args:
            model_id: str
                The ID of the model to retrieve.
            model_name: str
                The name of the model to retrieve.

        Returns:
            Dict:
                A dictionary representing the model.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.
        """
        api = swagger_client.RegistryServiceApi(self._api_client)
        with RESTErrorHandler():
            if model_id is not None:
                if model_name is not None:
                    raise ValueError(
                        "Arguments model_id and model_name are mutually exclusive.\n"
                        f"Received model_id={model_id} and model_name={model_name}."
                    )
                res: RimeGetModelResponse = api.get_model(model_id_uuid=model_id)
            elif model_name is not None:
                res = api.get_model(model_name=model_name)
            else:
                raise ValueError("Must provide either model_id or model_name")
            return res.model.model.to_dict()

    def get_predictions(self, model_id: str, dataset_id: str) -> Dict:
        """Get a prediction set.

        Args:
            model_id: str
                The ID of the model used to generate the predictions.
            dataset_id: str
                The ID of the dataset used to generate the predictions.

        Returns:
            Dict:
                A dictionary that contains the prediction set.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.
        """
        api = swagger_client.RegistryServiceApi(self._api_client)
        with RESTErrorHandler():
            res: RimeGetPredictionSetResponse = api.get_prediction_set(
                dataset_id=dataset_id, model_id_uuid=model_id
            )
            return res.prediction.to_dict()

    def delete_dataset(self, dataset_id: str) -> None:
        """Delete a dataset.

        Args:
            dataset_id: str
                The ID of the dataset to delete.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.
        """
        api = swagger_client.RegistryServiceApi(self._api_client)
        with RESTErrorHandler():
            api.delete_dataset(dataset_id=dataset_id)

    def delete_model(self, model_id: str) -> None:
        """Delete a model.

        Args:
            model_id: str
                The ID of the model to delete.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.
        """
        api = swagger_client.RegistryServiceApi(self._api_client)
        with RESTErrorHandler():
            api.delete_model(model_id_uuid=model_id)

    def delete_predictions(self, model_id: str, dataset_id: str) -> None:
        """Delete a prediction set.

        Args:
            model_id: str
                The ID of the model used to generate the predictions.
            dataset_id: str
                The ID of the dataset used to generate the predictions.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.
        """
        api = swagger_client.RegistryServiceApi(self._api_client)
        with RESTErrorHandler():
            api.delete_prediction_set(dataset_id=dataset_id, model_id_uuid=model_id)

    @staticmethod
    def log_registry_validation(
        registry_resp: dict, registry_type: str, registry_id: str
    ) -> None:
        """Log the validation status of a registry."""
        status = registry_resp.get(
            "validity_status", RegistryValidityStatus.UNSPECIFIED
        )
        if status != RegistryValidityStatus.VALID:
            print(
                f"Warning: the validation status of the {registry_type} {registry_id} is {status}. "
                f"Your test run may fail due to this {registry_type}.",
            )
            if registry_resp["validity_status_message"]:
                print(
                    f"The validation error message of the {registry_type} "
                    f"is {registry_resp['validity_status_message']}"
                )
