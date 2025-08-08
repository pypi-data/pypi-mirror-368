"""Library to initiate backend RIME service requests."""

import atexit
import json
import logging
import re
from collections import Counter
from datetime import date, datetime
from http import HTTPStatus
from inspect import getmembers
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Iterator, List, Optional, Tuple, Union
from uuid import uuid4

import importlib_metadata
import pandas as pd
from urllib3.util import Retry

from rime_sdk.continuous_test import ContinuousTest
from rime_sdk.generative_model import GenerativeModel
from rime_sdk.image_builder import ImageBuilder
from rime_sdk.internal.config_parser import get_registry_ids, validate_config
from rime_sdk.internal.file_upload import FileUploadModule
from rime_sdk.internal.rest_error_handler import RESTErrorHandler
from rime_sdk.internal.throttle_queue import ThrottleQueue
from rime_sdk.job import (
    BaseJob,
    ContinuousTestJob,
    FileScanJob,
    GenerativeModelTestJob,
    ImageBuilderJob,
    Job,
)
from rime_sdk.project import Project
from rime_sdk.registry import Registry
from rime_sdk.swagger import swagger_client
from rime_sdk.swagger.swagger_client import ApiClient
from rime_sdk.swagger.swagger_client.models import (
    ConfigvalidatorConfigTypeBody,
    IntegrationIntegration,
    IntegrationIntegrationSchema,
    IntegrationIntegrationType,
    IntegrationsIntegrationIdUuidBody,
    IntegrationVariableSensitivity,
    ListImagesRequestPipLibraryFilter,
    ManagedImagePackageRequirement,
    ManagedImagePipRequirement,
    ProjectCreateProjectRequest,
    RimeActorRole,
    RimeConfigureIntegrationRequestIntegrationVariable,
    RimeCreateImageRequest,
    RimeCreateIntegrationRequest,
    RimeJobMetadata,
    RimeJobType,
    RimeLicenseLimit,
    RimeLimitStatusStatus,
    RimeListImagesRequest,
    RimeManagedImage,
    RimeManagedImagePackageType,
    RimeManagedImageStatus,
    RimeModelTask,
    RimeParentRoleSubjectRolePair,
    RimeStartFileScanRequest,
    RimeUUID,
    RoleWorkspaceBody,
    RuntimeinfoCustomImage,
    RuntimeinfoCustomImageType,
    RuntimeinfoResourceRequest,
    RuntimeinfoRunTimeInfo,
    SchemaintegrationIntegrationVariable,
    StresstestsProjectIdUuidBody,
)
from rime_sdk.swagger.swagger_client.rest import ApiException
from rime_sdk.test_run import TestRun

logger = logging.getLogger()

VALID_MODEL_TASKS = [
    model_task
    for _, model_task in getmembers(RimeModelTask)
    if isinstance(model_task, str) and "MODEL_TASK_" in model_task
]

VALID_INTEGRATION_TYPES = [
    integration_type
    for _, integration_type in getmembers(IntegrationIntegrationType)
    if isinstance(integration_type, str) and "INTEGRATION_TYPE_" in integration_type
]

VALID_VARIABLE_SENSITIVITIES = [
    variable_sensitivity
    for _, variable_sensitivity in getmembers(IntegrationVariableSensitivity)
    if isinstance(variable_sensitivity, str)
    and "VARIABLE_SENSITIVITY_" in variable_sensitivity
]

# If the api client receives one of these recoverable status codes, it will retry the request.
RETRY_HTTP_STATUS = [
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.TOO_MANY_REQUESTS,
]

SEMVER_REGEX = r"(?P<major>\d+)\.(?P<minor>\d+)(\.*)(?P<patch>\d*)(?P<extra>.*)"


# matches a string pattern 'major.minor.patch' where
# major/minor/patch are integers, e.g 2.5.10
def match_semver_regex(version_str: str) -> Optional[dict]:
    """Take a semver version string and returns a semver object or None.

    Args:
        version_str: str
            The version string to be parsed.

    Returns:
        dict:
            A map object with keys "major", "minor", "patch", and
            "extra" if the string is in the correct format.  or
            None if the string is not in the correct format.

    Example:
        .. code-block:: python

            version_str = "2.7.1rc3+15.gd719627f94"

            # Parse the string
            version = match_semver_regex(version_str)
            # version yields
            # {'major': '2', 'minor': '7', 'patch': '1', 'extra': 'rc3+15.gd719627f94'}

    """
    comparable = re.match(SEMVER_REGEX, version_str)
    if comparable:
        version = comparable.groupdict()
        for key in ["major", "minor", "patch"]:
            value = version[key]
            if value == "":
                version[key] = 0
            else:
                version[key] = int(value)

        return version
    return None


def client_ahead_of_server_message(client_version: str, server_version: str) -> str:
    """Formats the error or warning message when the SDK version is ahead of the cluster version."""
    return (  # noqa: UP032
        "Python SDK package is ahead of the server version. The Python SDK package is on version {0}, "
        "while the server is on version {1}. In order to make them be on the same version, please install "
        "the correct version of the Python SDK package with `pip install rime_sdk=={1}`"
    ).format(
        client_version,
        server_version,
    )


class Client:
    """A Client object provides an interface to Robust Intelligence's services.

    To initialize the Client, provide the address of your RI instance and your API key.
    The Client can be used for creating Projects, starting Stress Test Jobs, and querying
    the backend for current Stress Test Jobs.

    Args:
        domain: str
            The base domain/address of the RIME service.
        api_key: str
            The API key used to authenticate to RIME services.
        channel_timeout: Optional[float]
            The amount of time in seconds to wait for responses from the cluster.
        disable_tls: Optional[bool]
            A Boolean that enables TLS when set to FALSE. By default, this
            value is set to FALSE.
        ssl_ca_cert: Optional[Union[Path, str]]
            Specifies the path to the certificate file used to verify the peer.
        cert_file: Optional[Union[Path, str]]
            Path to the Client certificate file.
        key_file: Optional[Union[Path, str]]
            Path to the Client key file.
        assert_hostname: Optional[bool]
            Enable/disable SSL hostname verification.

    Raises:
        ValueError
            This error is generated when a connection to the RIME cluster cannot be
            established before the interval specified in `timeout` expires.

    Example:
        .. code-block:: python

            rime_client = Client("my_vpc.rime.com", "api-key")
    """

    # A throttler that limits the number of model tests to roughly 20 every 5 minutes.
    # This is a static variable for Client.
    _throttler = ThrottleQueue(desired_events_per_epoch=20, epoch_duration_sec=300)

    def __init__(
        self,
        domain: str,
        api_key: str = "",
        channel_timeout: float = 180.0,
        disable_tls: bool = False,
        ssl_ca_cert: Optional[Union[Path, str]] = None,
        cert_file: Optional[Union[Path, str]] = None,
        key_file: Optional[Union[Path, str]] = None,
        assert_hostname: Optional[bool] = None,
    ) -> None:
        """Create a new Client connected to the services available at `domain`."""
        self._domain = domain
        if disable_tls:
            print(
                "WARNING: disabling tls is not recommended."
                " Please ensure you are on a secure connection to your servers."
            )
        self._channel_timeout = channel_timeout
        configuration = swagger_client.Configuration()
        configuration.api_key["rime-api-key"] = api_key
        if domain.endswith("/"):
            domain = domain[:-1]
        configuration.host = domain
        configuration.verify_ssl = not disable_tls
        # Set this to customize the certificate file to verify the peer.
        configuration.ssl_ca_cert = ssl_ca_cert
        # client certificate file
        configuration.cert_file = cert_file
        # client key file
        configuration.key_file = key_file
        # Set this to True/False to enable/disable SSL hostname verification.
        configuration.assert_hostname = assert_hostname
        self._api_client = ApiClient(configuration)
        # Prevent race condition in pool.close() triggered by swagger generated code
        atexit.register(self._api_client.pool.close)
        # Sets the timeout and hardcoded retries parameter for the api client.
        self._api_client.rest_client.pool_manager.connection_pool_kw[
            "timeout"
        ] = channel_timeout
        self._api_client.rest_client.pool_manager.connection_pool_kw["retries"] = Retry(
            total=3, status_forcelist=RETRY_HTTP_STATUS
        )
        self.customer_name = self._check_version()
        self._check_expiration()
        self.generative_model = GenerativeModel(self._api_client)

    def __repr__(self) -> str:
        """Return the string representation of the Client."""
        return f"Client(domain={self._domain})"

    def _check_expiration(self) -> None:
        """Check RIME Expiration Date."""
        api = swagger_client.FeatureFlagApi(self._api_client)
        with RESTErrorHandler():
            feature_flag_response = api.get_limit_status(
                customer_name=self.customer_name, limit=RimeLicenseLimit.EXPIRATION
            )

        # Get Expiration Date
        rime_info_api = swagger_client.RIMEInfoApi(self._api_client)
        with RESTErrorHandler():
            rime_info_response = rime_info_api.get_rime_info()
        expiration_date = datetime.fromtimestamp(
            rime_info_response.expiration_time.timestamp()
        ).date()

        limit_status = feature_flag_response.limit_status.limit_status
        if limit_status == RimeLimitStatusStatus.WARN:
            print(
                f"Your license expires on {expiration_date}."
                f" Contact the Robust Intelligence team to"
                f" upgrade your license."
            )
        elif limit_status == RimeLimitStatusStatus.ERROR:
            message = (
                "Your license has expired. Contact the Robust "
                "Intelligence team to upgrade your license."
            )
            grace_period_end = datetime.fromtimestamp(
                rime_info_response.grace_period_end_time.timestamp()
            ).date()
            if date.today() > grace_period_end:
                # if grace period has ended throw an error
                raise ValueError(message)
            else:
                print(f"{message} You have until {grace_period_end} to upgrade.")
        elif limit_status == RimeLimitStatusStatus.OK:
            pass
        else:
            raise ValueError(f"Unexpected status value: '{limit_status}'")

    def _check_version(self) -> str:
        """Check current RIME version and return client name."""
        api = swagger_client.RIMEInfoApi(self._api_client)
        with RESTErrorHandler():
            rime_info_response = api.get_rime_info()
        server_version_str = rime_info_response.cluster_info_version
        client_version_str = importlib_metadata.version("rime_sdk")
        try:
            server_version = match_semver_regex(server_version_str)
            client_version = match_semver_regex(client_version_str)
            if server_version is not None and client_version is not None:
                server_is_dev_version = server_version["extra"] != ""
                client_ahead_of_server = (
                    client_version["major"] > server_version["major"]
                ) or (
                    client_version["major"] == server_version["major"]
                    and client_version["minor"] > server_version["minor"]
                )
                if client_ahead_of_server:
                    if server_is_dev_version:
                        logger.warning(
                            client_ahead_of_server_message(
                                client_version_str, server_version_str
                            )
                        )
                    else:
                        raise ValueError(
                            client_ahead_of_server_message(
                                client_version_str, server_version_str
                            )
                        )
                elif client_version["major"] != server_version["major"] or (
                    client_version["minor"] != server_version["minor"]
                ):  # client is behind server
                    logger.warning(
                        "Python SDK package is behind the server version. "
                        "The Python SDK package is on version %s, "
                        "while the server is on version %s. "
                        "In order to make them be on the same version, please "
                        "install the correct version of the Python SDK package with "
                        "`pip install rime_sdk==%s`",
                        client_version_str,
                        server_version_str,
                        server_version_str,
                    )
        except (AttributeError, re.error):
            pass

        return rime_info_response.customer_name

    def __str__(self) -> str:
        """Pretty-print the object."""
        return f"RIME Client [{self._domain}]"

    def _project_exists(self, project_id: str) -> bool:
        """Check if `project_id` exists.

        Args:
            project_id: the id of the Project to be checked.

        Returns:
            bool:
                Whether project_id is a valid Project.

        Raises:
            ValueError
                This error is generated when the request to the Project service
                fails.
        """
        api = swagger_client.ProjectServiceApi(self._api_client)
        try:
            api.get_project(project_id)
            return True
        except ApiException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                return False
            raise ValueError(e.reason)

    def create_project(
        self,
        name: str,
        description: str,
        model_task: str,
        use_case: Optional[str] = None,
        ethical_consideration: Optional[str] = None,
        profiling_config: Optional[dict] = None,
        general_access_role: Optional[str] = "ACTOR_ROLE_NONE",
        run_time_info: Optional[dict] = None,
    ) -> Project:
        """Create a new RIME Project.

        Projects enable you to organize Stress Test runs.
        A natural way to organize Stress Test runs is to create a Project for each
        specific ML task, such as predicting whether a transaction is fraudulent.

        Args:
            name: str
                Name of the new Project.
            description: str
                Description of the new Project.
            model_task: str
                Machine Learning task associated with the Project. Must be one of
                "MODEL_TASK_REGRESSION", "MODEL_TASK_BINARY_CLASSIFICATION",
                "MODEL_TASK_MULTICLASS_CLASSIFICATION",
                "MODEL_TASK_NAMED_ENTITY_RECOGNITION", "MODEL_TASK_RANKING",
                "MODEL_TASK_OBJECT_DETECTION", "MODEL_TASK_NATURAL_LANGUAGE_INFERENCE",
                "MODEL_TASK_FILL_MASK".
            use_case: Optional[str]
                Description of the use case of the Project.
            ethical_consideration: Optional[str]
                Description of ethical considerations for this Project.
            profiling_config: Optional[dict]
                Configuration for the data and model profiling across all test
                runs.
            general_access_role: Optional[str],
                Project roles assigned to the workspace members.
                Allowed Values: ACTOR_ROLE_USER, ACTOR_ROLE_VIEWER, ACTOR_ROLE_NONE.
            run_time_info: Optional[dict]
                Default runtime information for all test runs in the project.

        Returns:
            Project:

        Raises:
            ValueError
                This error is generated when the request to the Project service fails.

        Example:
            .. code-block:: python

               project = rime_client.create_project(
                   name="foo", description="bar", model_task="Binary Classification"
               )
        """
        api = swagger_client.ProjectServiceApi(self._api_client)

        valid_general_access_roles = [
            "ACTOR_ROLE_USER",
            "ACTOR_ROLE_VIEWER",
            "ACTOR_ROLE_NONE",
        ]
        if general_access_role not in valid_general_access_roles:
            raise ValueError(
                f"Invalid general access role: '{general_access_role}'. "
                f"Expected one of: {valid_general_access_roles}"
            )
        if model_task not in VALID_MODEL_TASKS:
            raise ValueError(
                f"Invalid model task: '{model_task}'. "
                f"Expected one of: {VALID_MODEL_TASKS}"
            )
        with RESTErrorHandler():
            if profiling_config:
                with RESTErrorHandler():
                    cv_api = swagger_client.ConfigValidatorApi(self._api_client)
                    validate_body = ConfigvalidatorConfigTypeBody(
                        config_json=json.dumps(profiling_config),
                    )
                    cv_api.config_validator_validate_test_config(
                        config_type="CONFIG_TYPE_PROFILING", body=validate_body
                    )
            body = ProjectCreateProjectRequest(
                name=name,
                description=description,
                model_task=model_task,
                use_case=use_case,
                ethical_consideration=ethical_consideration,
                profiling_config=profiling_config,
                run_time_info=run_time_info,
            )
            response = api.create_project(body=body)

            if general_access_role != "ACTOR_ROLE_NONE":
                role_pairs = [
                    RimeParentRoleSubjectRolePair(
                        parent_role=RimeActorRole.ADMIN,
                        subject_role=general_access_role,
                    ),
                    RimeParentRoleSubjectRolePair(
                        parent_role=RimeActorRole.VP,
                        subject_role=general_access_role,
                    ),
                    RimeParentRoleSubjectRolePair(
                        parent_role=RimeActorRole.USER,
                        subject_role=general_access_role,
                    ),
                    # Workspace viewers can receive only a viewer role through
                    # general access as per the RBAC spec.
                    RimeParentRoleSubjectRolePair(
                        parent_role=RimeActorRole.VIEWER,
                        subject_role=RimeActorRole.VIEWER,
                    ),
                ]
                workspace_role_body = RoleWorkspaceBody(role_pairs=role_pairs)
                api.update_workspace_roles_for_project(
                    project_id_uuid=response.project.id.uuid,
                    body=workspace_role_body,
                )
            return Project(self._api_client, response.project.id.uuid)

    def get_project(self, project_id: str) -> Project:
        """Get Project by ID.

        Args:
            project_id: str
                ID of the Project to return.

        Returns:
            Project:

        Example:
            .. code-block:: python

               project = rime_client.get_project("123-456-789")
        """
        api = swagger_client.ProjectServiceApi(self._api_client)
        try:
            response = api.get_project(project_id)
            return Project(self._api_client, response.project.project.id.uuid)
        except ApiException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                raise ValueError(f"Project with this id {project_id} does not exist")
            raise ValueError(e.reason)

    def delete_project(self, project_id: str, force: Optional[bool] = False) -> None:
        """Delete a Project by ID.

        Args:
            project_id: str
                ID of the Project to delete.
            force: Optional[bool] = False
                When set to True, the Project will be deleted immediately. By default,
                a confirmation is required.

        Example:
            .. code-block:: python

               project = rime_client.delete_project("123-456-789", True)
        """
        project = self.get_project(project_id)
        project.delete(force=force)

    def create_managed_image(
        self,
        name: str,
        requirements: List[ManagedImagePipRequirement],
        package_requirements: Optional[List[ManagedImagePackageRequirement]] = None,
        python_version: Optional[str] = None,
    ) -> ImageBuilder:
        """Create a new managed Docker image with the desired custom requirements to run RIME on.

        These managed Docker images are managed by the RIME cluster and
        automatically upgrade when the installed version of RIME upgrades.
        Note: Images take a few minutes to be built.

        This method returns an object that can be used to track the progress of the
        image building job. The new custom image is only available for use in a stress
        test once it has status ``READY``.

        **Managed images are not currently supported in a Cloud deployment.
        Please reach out to Robust Intelligence for support if this functionality is required
        for your deployment.**

        Args:
            name: str
                The name of the new Managed Image. This name serves as the unique
                identifier of the Managed Image. The call fails when an image with
                the specified name already exists.
            requirements: List[ManagedImagePipRequirement]
                List of additional pip requirements to be installed on the managed
                image. A ``ManagedImagePipRequirement`` can be created with the helper
                method ``Client.pip_requirement``.
                The first argument is the name of the library (e.g. ``tensorflow`` or
                ``xgboost``) and the second argument is a valid pip
                `version specifier <https://www.python.org/dev/peps/pep-0440/#version-specifiers>`
                (e.g. ``>=0.1.2`` or ``==1.0.2``) or an exact
                `version<https://peps.python.org/pep-0440/>`, such as ``1.1.2``,
                for the library.
            package_requirements: Optional[List[ManagedImagePackageRequirement]]
                [BETA] An optional List of additional operating system package
                requirements to install on the Managed Image. Currently only
                `Rocky Linux` package requirements are supported.
                Create a ``ManagedImagePackageRequirement`` parameter with
                the ``Client.os_requirement`` helper method.
                The first argument is the name of the package (e.g. ``texlive`` or
                ``vim``) and the second optional argument is a valid yum
                `version specifier` (e.g. ``0.1.2``) for the package.
            python_version: Optional[str]
                An optional version string specifying only the major and minor version
                for the python interpreter used. The string should be of the format
                X.Y and be present in the set of supported versions.

        Returns:
            ImageBuilder:
                A ``ImageBuilder`` object that provides an interface for monitoring
                the job in the backend.

        Raises:
            ValueError
                This error is generated when the request to the ImageRegistry
                service fails.

        Example:
            .. code-block:: python

               reqs = [
                    # Fix the version of `xgboost` to `1.0.2`.
                    rime_client.pip_requirement("xgboost", "==1.0.2"),
                    # We do not care about the installed version of `tensorflow`.
                    rime_client.pip_requirement("tensorflow")
                ]

               # Start a new image building job
               builder_job = rime_client.create_managed_image("xgboost102_tf", reqs)

               # Wait until the job has finished and print out status information.
               # Once this prints out the `READY` status, your image is available for
               # use in Stress Tests.
               builder_job.get_status(verbose=True, wait_until_finish=True)
        """

        if isinstance(package_requirements, ManagedImagePackageRequirement):
            package_requirements = list(package_requirements)

        req = RimeCreateImageRequest(
            name=name,
            pip_requirements=requirements,
            package_requirements=package_requirements,
        )

        if python_version is not None:
            req.python_version = python_version

        api = swagger_client.ImageRegistryApi(self._api_client)
        with RESTErrorHandler():
            image: RimeManagedImage = api.create_image(body=req).image
        return ImageBuilder(
            self._api_client,
            image.name,
            requirements,
            package_requirements,
            python_version,
        )

    def has_managed_image(self, name: str, check_status: bool = False) -> bool:
        """Check whether a Managed Image with the specified name exists.

        Args:
            name: str
                The unique name of the Managed Image to check. The call returns
                False when no image with the specified name exists.
            check_status: bool
                Flag that determines whether to check the image status. When
                this flag is set to True, the call returns True if and only if the image
                with the specified name exists AND the image is ready to be used.

        Returns:
            bool:
                Specifies whether a Managed Image with this name exists.

        Example:
            .. code-block:: python

               if rime_client.has_managed_image("xgboost102_tensorflow"):
                    print("Image exists.")
        """
        api = swagger_client.ImageRegistryApi(self._api_client)
        try:
            res = api.get_image(name=name)
        except ApiException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                return False
            else:
                raise ValueError(e.reason) from None
        if check_status:
            return res.image.status == RimeManagedImageStatus.READY
        return True

    def get_managed_image(self, name: str) -> Dict:
        """Get Managed Image by name.

        Args:
            name: str
                The unique name of the new Managed Image. The call raises
                an error when no image exists with this name.

        Returns:
            Dict:
                A dictionary with information about the Managed Image.

        Example:
            .. code-block:: python

               image = rime_client.get_managed_image("xgboost102_tensorflow")
        """
        api = swagger_client.ImageRegistryApi(self._api_client)
        with RESTErrorHandler():
            res = api.get_image(name=name)
        return res.image.to_dict()

    def delete_managed_image(self, name: str) -> None:
        """Delete a managed Docker image.

        Args:
            name: str
                The unique name of the Managed Image.

        Example:
            .. code-block:: python

               image = rime_client.delete_managed_image("xgboost102_tensorflow")
        """
        api = swagger_client.ImageRegistryApi(self._api_client)
        try:
            api.delete_image(name=name)
            print(f"Managed Image {name} successfully deleted")
        except ApiException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                raise ValueError(f"Docker image with name {name} does not exist.")
            raise ValueError(e.reason) from None

    @staticmethod
    def pip_requirement(
        name: str,
        version_specifier: Optional[str] = None,
    ) -> ManagedImagePipRequirement:
        """Construct a PipRequirement object for use in ``create_managed_image()``."""
        if not isinstance(name, str) or (
            version_specifier is not None and not isinstance(version_specifier, str)
        ):
            raise ValueError(
                "Proper specification of a pip requirement has the name"
                "of the library as the first argument and the version specifier"
                "string as the second argument"
                '(e.g. `pip_requirement("tensorflow", "==0.15.0")` or'
                '`pip_requirement("xgboost")`)'
            )
        res = ManagedImagePipRequirement(name=name)
        if version_specifier is not None:
            res.version_specifier = version_specifier
        return res

    @staticmethod
    def os_requirement(
        name: str,
        version_specifier: Optional[str] = None,
    ) -> ManagedImagePackageRequirement:
        """Construct a PackageRequirement object for ``create_managed_image()``."""
        if (
            not isinstance(name, str)
            or (
                version_specifier is not None and not isinstance(version_specifier, str)
            )
            or (
                version_specifier is not None and not re.match(r"\d", version_specifier)
            )
        ):
            raise ValueError(
                "Proper specification of a package requirement has the name"
                "of the library as the first argument and optionally the version"
                "specifier string as the second argument"
                '(e.g. `os_requirement("texlive", "20200406")` or'
                '`os_requirement("texlive")`)'
            )
        res = ManagedImagePackageRequirement(
            name=name, package_type=RimeManagedImagePackageType.ROCKYLINUX
        )
        if version_specifier is not None:
            res.version_specifier = version_specifier
        return res

    @staticmethod
    def pip_library_filter(
        name: str,
        fixed_version: Optional[str] = None,
    ) -> ListImagesRequestPipLibraryFilter:
        """Construct a PipLibraryFilter object for use in ``list_managed_images()``."""
        if not isinstance(name, str) or (
            fixed_version is not None and not isinstance(fixed_version, str)
        ):
            raise ValueError(
                "Proper specification of a pip library filter has the name"
                "of the library as the first argument and the semantic version"
                "string as the second argument"
                '(e.g. `pip_library_filter("tensorflow", "1.15.0")` or'
                '`pip_library_filter("xgboost")`)'
            )
        res = ListImagesRequestPipLibraryFilter(name=name)
        if fixed_version is not None:
            res.version = fixed_version
        return res

    def list_managed_images(
        self,
        pip_library_filters: Optional[List[ListImagesRequestPipLibraryFilter]] = None,
    ) -> Iterator[Dict]:
        """List all managed Docker images.

        Enables searching for images with specific pip libraries installed so that users
        can reuse Managed Images for Stress Tests.

        Args:
            pip_library_filters: Optional[List[ListImagesRequestPipLibraryFilter]]
                Optional list of pip libraries to filter by.
                Construct each ListImagesRequest.PipLibraryFilter object with the
                ``pip_library_filter`` convenience method.

        Returns:
            Iterator[Dict]:
                An iterator of dictionaries, each dictionary represents
                a single Managed Image.

        Raises:
            ValueError
                This error is generated when the request to the ImageRegistry
                service fails or the list of pip library filters is improperly
                specified.

        Example:
            .. code-block:: python

                # Filter for an image with catboost1.0.3 and tensorflow installed.
                filters = [
                    rime_client.pip_library_filter("catboost", "1.0.3"),
                    rime_client.pip_library_filter("tensorflow"),
                ]

                # Query for the images.
                images = rime_client.list_managed_images(
                    pip_library_filters=filters)

                # To get the names of the returned images.
                [image["name"] for image in images]
        """
        if pip_library_filters is None:
            pip_library_filters = []

        if pip_library_filters is not None:
            for pip_library_filter in pip_library_filters:
                if not isinstance(
                    pip_library_filter, ListImagesRequestPipLibraryFilter
                ):
                    raise ValueError(
                        f"pip library filter `{pip_library_filter}` is not of the "
                        f"correct type, should be of type "
                        f"ListImagesRequest.PipLibraryFilter. Please use "
                        f"rime_client.pip_library_filter to create these filters."
                    )

        # Iterate through the pages of images and break at the last page.
        api = swagger_client.ImageRegistryApi(self._api_client)
        page_token = ""
        while True:
            if page_token == "":
                body = RimeListImagesRequest(
                    pip_libraries=pip_library_filters,
                    page_size=20,
                )
            else:
                body = RimeListImagesRequest(page_token=page_token, page_size=20)
            with RESTErrorHandler():
                # This function hits the additional REST binding on the RPC endpoint.
                # The method sends a POST request instead of a GET since it is
                # the only way to encode multiple custom messages (pip_libraries).
                res = api.image_registry_list_images2(body=body)
                for image in res.images:
                    yield image.to_dict()

            # If we've reached the last page token
            if page_token == res.next_page_token:
                break

            # Move to the next page
            page_token = res.next_page_token

    def list_agents(
        self,
    ) -> Iterator[Dict]:
        """List all Agents available to the user.

        Returns:
            Iterator[Dict]:
                An iterator of dictionaries, each dictionary represents a single Agent.

        Raises:
            ValueError
                This error is generated when the request to the AgentManager
                service fails.

        Example:
            .. code-block:: python

                # Query for the images.
                agents = rime_client.list_agents()

                # To get the names of the returned Agents.
                [agent["name"] for agent in agents]
        """
        # Iterate through the pages of images and break at the last page.
        page_token = None
        api = swagger_client.AgentManagerApi(self._api_client)
        while True:
            with RESTErrorHandler():
                if page_token is None:
                    res = api.list_agents(
                        first_page_query_agent_status_types=[],
                        first_page_query_agent_ids=[],
                        page_size=100,
                    )
                else:
                    res = api.list_agents(page_token=page_token, page_size=100)
            for agent in res.agents:
                yield agent.to_dict()

            # If we've reached the last page token
            if not res.has_more:
                break

            # Move to the next page
            page_token = res.next_page_token

    def list_projects(
        self,
    ) -> Iterator[Project]:
        """List all Projects.

        Returns:
            Iterator[Project]:
                An iterator of Projects.

        Raises:
            ValueError
                This error is generated when the request to the Project service fails.

        Example:
            .. code-block:: python

                # Query for projects.
                projects = rime_client.list_projects()

        """
        # Iterate through the pages of Test Cases and break at the last page.
        page_token = ""
        api = swagger_client.ProjectServiceApi(self._api_client)
        while True:
            with RESTErrorHandler():
                res = api.list_projects(page_token=page_token)
            for project in res.projects:
                yield Project(self._api_client, project.project.id.uuid)
            # we've reached the last page of Test Cases.
            if not res.has_more:
                break
            # Advance to the next page of Test Cases.
            page_token = res.next_page_token

    def start_stress_test(
        self,
        test_run_config: dict,
        project_id: str,
        agent_id: Optional[str] = None,
        **exp_fields: Dict[str, object],
    ) -> Job:
        """Start a Stress Testing run.

        Args:
            test_run_config: dict
                Configuration for the test to be run, which specifies unique ids to
                locate the model and datasets to be used for the test.
            project_id: str
                Identifier for the Project where the resulting test run will be stored.
                When not specified, stores the results in the default Project.
            agent_id: Optional[str]
                ID for the Agent where the Stress Test will be run.
                Uses the default Agent for the workspace when not specified.
            exp_fields: Dict[str, object]
                [BETA] Fields for experimental features.

        Returns:
            Job:
                A Job that provides information about the model Stress Test job.

        Raises:
            ValueError
                This error is generated when the request to the ModelTesting
                service fails.

        Example:
            This example assumes that reference and evaluation datasets are registered
            with identifiers "foo" and "bar" respectively, and that a model with the
            unique identifier `model_uuid` is registered.

        .. code-block:: python

            config = {
                "data_info": {"ref_dataset_id": "foo", "eval_dataset_id": "bar"},
                "model_id": model_uuid,
                "run_name": "My Stress Test Run",
            }

        Run the job using the specified configuration and the default Docker image in
        the RIME backend. Store the results in the RIME Project associated with this
        object.

        .. code-block:: python

           job = rime_client.start_stress_test_job(
              test_run_config=config, project_id="123-456-789"
           )
        """
        validate_config(test_run_config)
        ref_dataset_id, eval_dataset_id, model_id = get_registry_ids(test_run_config)
        registry = Registry(self._api_client)
        if ref_dataset_id is not None:
            resp = registry.get_dataset(dataset_id=ref_dataset_id)
            registry.log_registry_validation(resp, "ref dataset", ref_dataset_id)
        if eval_dataset_id is not None:
            resp = registry.get_dataset(dataset_id=eval_dataset_id)
            registry.log_registry_validation(resp, "eval dataset", eval_dataset_id)
        if model_id is not None:
            resp = registry.get_model(model_id=model_id)
            registry.log_registry_validation(resp, "model", model_id)

        if not self._project_exists(project_id):
            raise ValueError(f"Project id {project_id} does not exist")
        cv_api = swagger_client.ConfigValidatorApi(self._api_client)
        with RESTErrorHandler():
            validate_body = ConfigvalidatorConfigTypeBody(
                config_json=json.dumps(test_run_config),
            )
            cv_api.config_validator_validate_test_config(
                config_type="CONFIG_TYPE_TEST_RUN", body=validate_body
            )
            req = StresstestsProjectIdUuidBody(
                test_run_config=test_run_config,
                experimental_fields=exp_fields if exp_fields else None,
                agent_id=RimeUUID(agent_id) if agent_id else None,
            )
            Client._throttler.throttle(
                throttling_msg="Your request is throttled to limit # of model tests."
            )
            api = swagger_client.ModelTestingApi(self._api_client)
            job: RimeJobMetadata = api.start_stress_test(
                body=req,
                project_id_uuid=project_id,
            ).job
        return Job(self._api_client, job.job_id)

    def get_test_run(self, test_run_id: str) -> TestRun:
        """Get a TestRun object with the specified test_run_id.

        Checks to see if the test_run_id exists, then returns TestRun object.

        Args:
            test_run_id: str
                ID of the test run to query for

        Returns:
            TestRun:
                A TestRun object corresponding to the test_run_id
        """
        try:
            api = swagger_client.ResultsReaderApi(self._api_client)
            api.get_test_run(test_run_id=test_run_id)
            return TestRun(self._api_client, test_run_id)
        except ApiException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                raise ValueError(f"test run id {test_run_id} does not exist")
            raise ValueError(e.reason) from None

    def get_ct_for_project(self, project_id: str) -> ContinuousTest:
        """Get the active ct for a Project if it exists.

        Query the backend for an active `ContinuousTest` in a specified Project
        which can be used to perform continuous testing operations. If there is
        no active ContinuousTest for the Project, this call will error.

        Args:
            project_id: ID of the Project which contains a ContinuousTest.

        Returns:
            ContinuousTest:
                A ``ContinuousTest`` object.

        Raises:
            ValueError
                This error is generated when the ContinuousTest does not exist
                or when the request to the Project service fails.

        Example:
            .. code-block:: python

                # Get CT in foo-project if it exists.
                ct = rime_client.get_ct_for_project("foo-project")
        """
        project = self.get_project(project_id)
        return project.get_ct()

    def upload_file(
        self, file_path: Union[Path, str], upload_path: Optional[str] = None
    ) -> str:
        """Upload a file to make it accessible to the RIME cluster.

        The uploaded file is stored in the RIME cluster in a blob store
        using its file name.

        **File uploading is not currently supported in a Cloud deployment.
        Please use an external data source instead.**

        Args:
            file_path: Union[Path, str]
                Path to the file to be uploaded to RIME's blob store.
            upload_path: Optional[str] = None
                Name of the directory in the blob store file system. If omitted,
                a unique random string will be the directory.

        Returns:
            str:
                A reference to the uploaded file's location in the blob store. This
                reference can be used to refer to that object when writing RIME configs.
                Please store this reference for future access to the file.

        Raises:
            FileNotFoundError
                When the path ``file_path`` does not exist.
            IOError
                When ``file_path`` is not a file.
            ValueError
                When the specified upload_path is an empty string or there was an
                error in obtaining a blobstore location from the
                RIME backend or in uploading ``file_path`` to RIME's blob store.
                When the file upload fails, the incomplete file is
                NOT automatically deleted.

        Example:
             .. code-block:: python

                # Upload the file at location data_path.
                client.upload_file(data_path)
        """
        if upload_path is not None and upload_path == "":
            raise ValueError("specified upload_path must not be an empty string")
        if isinstance(file_path, str):
            file_path = Path(file_path)
        with RESTErrorHandler():
            fum = FileUploadModule(self._api_client)
            return fum.upload_dataset_file(file_path, upload_path)

    def upload_local_image_dataset_file(
        self,
        file_path: Union[Path, str],
        image_features: List[str],
        upload_path: Optional[str] = None,
    ) -> Tuple[List[Dict], str]:
        """Upload an image dataset file where image files are stored locally.

        The image dataset file is expected to be a list of JSON dictionaries,
        with an image_features that reference an image (either an absolute path
        or a relative path to an image file stored locally).
        Every image within the file is also uploaded to blob store,
        and the final file is also uploaded.
        If your image paths already reference an external blob storage,
        then use `upload_file` instead to upload the dataset file.

        **File uploading is not currently supported in a Cloud deployment.
        Please use an external data source instead.**

        Args:
            file_path: Union[Path, str]
                Path to the file to be uploaded to RIME's blob store.
            image_features: List[str]
                Keys to image file paths.
            upload_path: Optional[str]
                Name of the directory in the blob store file system. If omitted,
                a unique random string will be the directory.

        Returns:
            Tuple[List[Dict], str]:
                The list of dicts contains the updated
                dataset file with image paths replaced by s3 paths. The string contains
                a reference to the uploaded file's location in the blob store. This
                reference can be used to refer to that object when writing RIME configs.
                Please store this reference for future access to the file.

        Raises:
            FileNotFoundError
                When the path ``file_path`` does not exist.
            IOError
                When ``file_path`` is not a file.
            ValueError
                When there was an error in obtaining a blobstore location from the
                RIME backend or in uploading ``file_path`` to RIME's blob store.
                In the scenario the file fails to upload, the incomplete file will
                NOT automatically be deleted.
        """
        if upload_path is not None and upload_path == "":
            raise ValueError("specified upload_path must not be an empty string")
        if isinstance(file_path, str):
            file_path = Path(file_path)
        with open(file_path, "r") as fp:
            data_dicts = json.load(fp)
            is_list = isinstance(data_dicts, list)
            is_all_dict = all(isinstance(d, dict) for d in data_dicts)
            if not is_list or not is_all_dict:
                raise ValueError(
                    "Loaded image dataset file must be a list of dictionaries."
                )
        null_counter: Counter = Counter()
        # first check if image path exists
        for data_dict in data_dicts:
            for key in image_features:
                if data_dict.get(key) is None:
                    null_counter[key] += 1
                    continue
                image_path = Path(data_dict[key])
                if not image_path.is_absolute():
                    image_path = file_path.parent / image_path
                if not image_path.exists():
                    raise ValueError(f"Image path does not exist: {image_path}")
                data_dict[key] = image_path

        for key, num_nulls in null_counter.items():
            logger.warning("Found %d null paths for feature %s.", num_nulls, key)

        # then upload paths, replace dict
        for data_dict in data_dicts:
            for key in image_features:
                if data_dict.get(key) is None:
                    continue
                uploaded_image_path = self.upload_file(
                    data_dict[key], upload_path=upload_path
                )
                data_dict[key] = uploaded_image_path

        # save dictionary with s3 paths to a new temporary file, upload file to S3
        with TemporaryDirectory() as temp_dir:
            # save file to a temporary directory
            temp_path = Path(temp_dir) / file_path.name
            with open(temp_path, "w") as fp:
                json.dump(data_dicts, fp)
            return (
                data_dicts,
                self.upload_file(temp_path, upload_path=upload_path),
            )

    def upload_data_frame(
        self,
        data_frame: pd.DataFrame,
        name: Optional[str] = None,
        upload_path: Optional[str] = None,
    ) -> str:
        """Upload a pandas DataFrame to make it accessible to the RIME cluster.

        The uploaded file is stored in the RIME cluster in a blob store
        using its file name.

        **File uploading is not currently supported in a Cloud deployment.
        Please use an external data source instead.**

        Args:
            data_frame: pd.DataFrame
                Path to the file to be uploaded to RIME's blob store.
            name: Optional[str] = None
                Name of the file in the blob store file system. If omitted,
                a unique random string will be assigned as the file name.
            upload_path: Optional[str] = None
                Name of the directory in the blob store file system. If omitted,
                a unique random string will be the directory.

        Returns:
            str:
                A reference to the uploaded file's location in the blob store. This
                reference can be used to refer to that object when writing RIME configs.
                Please store this reference for future access to the file.

        Raises:
            ValueError
                When the specified upload_path is an empty string or there was an
                error in obtaining a blobstore location from the
                RIME backend or in uploading ``file_path`` to RIME's blob store.
                When the file upload fails, the incomplete file is
                NOT automatically deleted.

        Example:
             .. code-block:: python

                # Upload pandas data frame.
                client.upload_data_frame(df)
        """
        with TemporaryDirectory() as temp_dir:
            name = name or f"{uuid4()}-data"
            temp_path = Path(temp_dir) / f"{name}.parquet"
            data_frame.to_parquet(temp_path, index=False)
            return self.upload_file(temp_path, upload_path=upload_path)

    def upload_directory(
        self,
        dir_path: Union[Path, str],
        upload_hidden: bool = False,
        upload_path: Optional[str] = None,
    ) -> str:
        """Upload a model directory to make it accessible to the RIME cluster.

        The uploaded directory is stored in the RIME cluster in a blob store.
        All files contained within ``dir_path`` and its subdirectories are uploaded
        according to their relative paths within ``dir_path``. When
        `upload_hidden` is set to False, all hidden files and subdirectories
        that begin with a '.' are not uploaded.

        **File uploading is not currently supported in a Cloud deployment.
        Please use an external data source instead.**

        Args:
            dir_path: Union[Path, str]
                Path to the directory to be uploaded to RIME's blob store.
            upload_hidden: bool = False
                Whether to upload hidden files or subdirectories
                (i.e. those beginning with a '.').
            upload_path: Optional[str] = None
                Name of the directory in the blob store file system. If omitted,
                a unique random string will be the directory.

        Returns:
            str:
                A reference to the uploaded directory's location in the blob store. This
                reference can be used to refer to that object when writing RIME configs.
                Please store this reference for future access to the directory.

        Raises:
            FileNotFoundError
                When the directory ``dir_path`` does not exist.
            IOError
                When ``dir_path`` is not a directory or contains no files.
            ValueError
                When the specified upload_path is an empty string or
                there was an error in obtaining a blobstore location from the
                RIME backend or in uploading ``dir_path`` to RIME's blob store.
                In the scenario the directory fails to upload, files will NOT
                automatically be deleted.
        """
        if upload_path is not None and upload_path == "":
            raise ValueError("specified upload_path must not be an empty string")
        if isinstance(dir_path, str):
            dir_path = Path(dir_path)
        with RESTErrorHandler():
            fum = FileUploadModule(self._api_client)
            return fum.upload_model_directory(
                dir_path,
                upload_hidden=upload_hidden,
                upload_path=upload_path,
            )

    def list_uploaded_file_urls(self) -> Iterator[str]:
        """Return an iterator of file paths that have been uploaded using ``client.upload_file``.

        Returns:
            Iterator[str]:
                An iterator of file path strings.

        Example:
            .. code-block:: python

                # List all file URLs
                urls = rime_client.list_uploaded_file_urls()
        """
        with RESTErrorHandler():
            fum = FileUploadModule(self._api_client)
            return fum.list_uploaded_files_urls()

    def delete_uploaded_file_url(self, upload_url: str) -> None:
        """Delete the file at the specified upload url in the RIME blob store.

        Args:
            upload_url: str
                Url to the file to be deleted in the RIME blob store.

        Returns:
            None

        Example:
            .. code-block:: python

                # Delete a file URL returned by list_uploaded_file_urls
                urls = rime_client.list_uploaded_file_urls()
                first_url = next(urls)
                rime_client.delete_uploaded_file_url(first_url)
        """
        with RESTErrorHandler():
            fum = FileUploadModule(self._api_client)
            return fum.delete_uploaded_file_url(upload_url)

    def get_job(self, job_id: str) -> BaseJob:
        """Get job by ID.

        Args:
            job_id: ID of the Job to return.

        Returns:
            Job:
                A ``Job`` object.

        Raises:
            ValueError
                This error is generated when no Job with the specified ID exists.

        Example:
            .. code-block:: python

                # Get Job with ID if it exists.
                job = rime_client.get_job("123-456-789")
        """
        api = swagger_client.JobReaderApi(self._api_client)
        try:
            job_response = api.get_job(job_id=job_id)
        except ApiException as e:
            if e.status == HTTPStatus.BAD_REQUEST:
                raise ValueError(f"job id `{job_id}` is not a valid job id.")
            elif e.status == HTTPStatus.NOT_FOUND:
                raise ValueError(f"Did not find job id `{job_id}`.")
            else:
                raise ValueError(e.reason) from None
        if job_response.job.job_type == RimeJobType.MODEL_STRESS_TEST:
            return Job(self._api_client, job_id)
        elif job_response.job.job_type == RimeJobType.FIREWALL_BATCH_TEST:
            return ContinuousTestJob(self._api_client, job_id)
        elif job_response.job.job_type == RimeJobType.IMAGE_BUILDER:
            return ImageBuilderJob(self._api_client, job_id)
        elif job_response.job.job_type == RimeJobType.FILE_SCAN:
            return FileScanJob(self._api_client, job_id)
        elif job_response.job.job_type == RimeJobType.GENERATIVE_MODEL_TEST:
            return GenerativeModelTestJob(self._api_client, job_id)
        else:
            raise ValueError(f"Invalid job type {job_response.job.job_type}.")

    def start_file_scan(
        self,
        model_id: str,
        project_id: str,
        custom_image: Optional[RuntimeinfoCustomImage] = None,
        rime_managed_image: Optional[str] = None,
        ram_request_megabytes: Optional[int] = None,
        cpu_request_millicores: Optional[int] = None,
        agent_id: Optional[str] = None,
    ) -> FileScanJob:
        """Start a File Scan job.

        Args:
            model_id: str
                The model ID of the model to be scanned. Only registered models can be
                scanned.
            project_id: str
                The project to which the file scan result will be saved. Must be the
                project whose registry contains the model to be scanned.
            custom_image: Optional[RuntimeinfoCustomImage]
                Specification of a customized container image to use running the model
                test. The image must have all dependencies required by your model.
                The image must specify a name for the image and optionally a pull secret
                (of type RuntimeinfoCustomImagePullSecret) with the name of the
                kubernetes pull secret used to access the given image.
            rime_managed_image: Optional[str]
                Name of a Managed Image to use when running the model test.
                The image must have all dependencies required by your model. To create
                new Managed Images with your desired dependencies, use the client's
                `create_managed_image()` method.
            ram_request_megabytes: Optional[int]
                Megabytes of RAM requested for the Stress Test Job.
                The limit is equal to megabytes requested.
            cpu_request_millicores: Optional[int]
                Millicores of CPU requested for the Stress Test Job.
                The limit is equal to millicores requested.
            agent_id: Optional[str]
                ID of the Agent that runs the File Scan job.
                When unspecified, the workspace's default Agent is used.

        Returns:
            FileScanJob:
                An ML File Scan Job object.

        Raises:
            ValueError
                This error is generated when the request to the FileScanning
                service fails.

        Example:
            This example shows how to scan a Huggingface model file.

        .. code-block:: python

           job = rime_client.start_file_scan(model_id="123-456-789")
        """
        if not self._project_exists(project_id):
            raise ValueError(f"Project ID {project_id} does not exist")
        if not isinstance(model_id, str):
            raise ValueError(f"Model ID {model_id} must be a string")
        if ram_request_megabytes is not None and ram_request_megabytes <= 0:
            raise ValueError(
                "The requested number of megabytes of RAM must be positive"
            )

        if cpu_request_millicores is not None and cpu_request_millicores <= 0:
            raise ValueError(
                "The requested number of millicores of CPU must be positive"
            )
        req = RimeStartFileScanRequest(
            model_id=RimeUUID(model_id),
            project_id=RimeUUID(project_id),
            agent_id=RimeUUID(agent_id) if agent_id else None,
        )

        req.run_time_info = RuntimeinfoRunTimeInfo(
            resource_request=RuntimeinfoResourceRequest()
        )
        if cpu_request_millicores:
            req.run_time_info.resource_request.cpu_request_millicores = (
                cpu_request_millicores
            )
        if ram_request_megabytes:
            req.run_time_info.resource_request.ram_request_megabytes = (
                ram_request_megabytes
            )
        if custom_image:
            req.run_time_info.custom_image = RuntimeinfoCustomImageType(
                custom_image=custom_image
            )
        if rime_managed_image:
            req.run_time_info.custom_image = RuntimeinfoCustomImageType(
                managed_image_name=rime_managed_image
            )

        Client._throttler.throttle(
            throttling_msg="Your request is throttled to limit # of file scans."
        )
        api = swagger_client.ModelTestingApi(self._api_client)
        with RESTErrorHandler():
            response = api.model_testing_start_file_scan(body=req)
            job: RimeJobMetadata = response.job
            return FileScanJob(self._api_client, job.job_id)

    def get_file_scan_result(
        self,
        file_scan_id: str,
    ) -> dict:
        """Get a file scan result with the specified file_scan_id.

        Args:
            file_scan_id: str
                ID of the file scan result to query for

        Returns:
            Dict:
                A dictionary representation of the file scan result.
        """
        api = swagger_client.FileScanningApi(self._api_client)
        try:
            response = api.file_scanning_get_file_scan_result(
                file_scan_id_uuid=file_scan_id,
            )
            return response.file_scan_result.to_dict()
        except ApiException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                raise ValueError(f"file scan id {file_scan_id} does not exist")
            raise ValueError(e.reason) from None

    def list_file_scan_results(
        self,
        project_id: str,
        model_id: Optional[str] = "",
    ) -> Iterator[dict]:
        """List all file scan results within a project.

        Optionally filters for all scan results of a specific model.

        Args:
            project_id: str
                The project ID of the project whose file scan results are to be
                returned.
            model_id: Optional[str]
                The model ID of file scan results to be returned.

        File scan results contain the security reports for the scanned files
        or repositories.

        Returns:
            Iterator[dict]:
                An iterator of dictionaries, each dictionary represents a single ML
                File Scan result.

        Raises:
            ValueError
                This error is generated when the request to the FileScanning
                service fails.

        Example:
            .. code-block:: python

                # List all ML file scan results.
                results = rime_client.list_file_scan_results(project_id="123-456-789")
        """
        if not self._project_exists(project_id):
            raise ValueError(f"Project ID {project_id} does not exist")
        # Iterate through the pages of file scan results and break at the last page.
        page_token = ""
        api = swagger_client.FileScanningApi(self._api_client)
        while True:
            with RESTErrorHandler():
                if page_token == "":
                    params = {
                        "first_page_query_project_id_uuid": project_id,
                        "page_size": 20,
                    }
                    if model_id != "":
                        params["first_page_query_model_id_uuid"] = model_id
                    res = api.file_scanning_list_file_scan_results(
                        **params,
                    )
                else:
                    res = api.file_scanning_list_file_scan_results(
                        page_token=page_token,
                        page_size=20,
                    )
            for file_scan_result in res.results:
                yield file_scan_result.to_dict()

            # If we've reached the last page token
            if not res.has_more:
                break

            # Move to the next page
            page_token = res.next_page_token

    def delete_file_scan_result(
        self,
        file_scan_id: str,
    ) -> None:
        """Deletes a file scan result with the specified file_scan_id.

        Args:
            file_scan_id: str
                ID of the file scan result to delete

        Returns:
            None
        """
        api = swagger_client.FileScanningApi(self._api_client)
        try:
            api.file_scanning_delete_file_scan_result(file_scan_id_uuid=file_scan_id)
            print(f"File scan with ID {file_scan_id} successfully deleted")
        except ApiException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                raise ValueError(f"File Scan with ID {file_scan_id} does not exist")
            raise ValueError(e.reason) from None

    def create_integration(
        self,
        workspace_id: str,
        name: str,
        integration_type: str,
        integration_schema: List[Dict],
    ) -> str:
        """Create an integration and return its UUID.

        Args:
            workspace_id: str
                ID of the workspace for which to create the integration.
            name: str
                Name that will be given to the integration.
            integration_type: str
                The type of integration. Must be one of
                "INTEGRATION_TYPE_CUSTOM", "INTEGRATION_TYPE_DATABRICKS",
                "INTEGRATION_TYPE_AWS_ACCESS_KEY",
                "INTEGRATION_TYPE_AWS_ROLE_ARN",
                "INTEGRATION_TYPE_HUGGINGFACE", "INTEGRATION_TYPE_GCS",
                "INTEGRATION_TYPE_AZURE_CLIENT_SECRET",
                "INTEGRATION_TYPE_AZURE_WORKLOAD_IDENTITY".
            integration_schema: List[Dict]
                List of Python dicts where each dict represents a variable and
                has the following keys:

                "name": str (required)
                "sensitivity": str (required). Must be one of
                "VARIABLE_SENSITIVITY_PUBLIC",
                "VARIABLE_SENSITIVITY_WORKSPACE_SECRET",
                "VARIABLE_SENSITIVITY_USER_SECRET".
                value: str (optional)

        Returns:
            str:
                The integration id of the newly created integration.

        Raises:
            ValueError
                This error is generated when the user provides an invalid
                integration_type or integration_schema is missing required information.
        """
        api = swagger_client.IntegrationServiceApi(self._api_client)

        if integration_type not in VALID_INTEGRATION_TYPES:
            raise ValueError(
                f"Invalid integration type: '{integration_type}'. "
                f"Expected one of: {VALID_INTEGRATION_TYPES}"
            )

        validated_integration_variables = self._validate_and_convert_integration_schema(
            integration_schema
        )
        create_req = RimeCreateIntegrationRequest(
            integration=IntegrationIntegration(
                workspace_id=RimeUUID(workspace_id),
                name=name,
                type=integration_type,
                schema=validated_integration_variables,
            )
        )
        with RESTErrorHandler():
            resp = api.create_integration(body=create_req)

        integration_id = resp.integration_info.integration.id
        integration_variables = self._prepare_schema_for_configuring_integration(
            integration_schema
        )
        configure_req = IntegrationsIntegrationIdUuidBody(
            integration_id=integration_id,
            variables=integration_variables,
        )
        with RESTErrorHandler():
            api.configure_integration(
                body=configure_req,
                integration_id_uuid=integration_id.uuid,
            )
        return integration_id.uuid

    @staticmethod
    def _validate_and_convert_integration_schema(
        integration_schema: List[Dict],
    ) -> IntegrationIntegrationSchema:
        """Validate user provided schema and return its swagger representation.

        Args:
            integration_schema: List[Dict]
                List of Python dicts where each dict represents a variable and
                has the following keys:
                    "name": str (required)
                    "sensitivity": str (required). Must be one of
                        "VARIABLE_SENSITIVITY_PUBLIC",
                        "VARIABLE_SENSITIVITY_WORKSPACE_SECRET",
                        "VARIABLE_SENSITIVITY_USER_SECRET".
                    value: str (optional)

        Returns:
            IntegrationIntegrationSchema:
                Swagger object containing representation of each dict provided.

        Raises:
            ValueError
                This error is generated when the user provided dictionaries do
                not contain the required information.
        """
        variables = []

        for variable in integration_schema:
            if "name" not in variable:
                raise ValueError(
                    'Missing key "name" in integration_schema\'s variable dict.'
                )
            if "sensitivity" not in variable:
                raise ValueError(
                    'Missing key "sensitivity" in integration_schema\'s variable dict.'
                )
            name = variable["name"]
            sensitivity = variable["sensitivity"]

            if sensitivity not in VALID_VARIABLE_SENSITIVITIES:
                raise ValueError(
                    f"Invalid variable sensitivity: '{sensitivity}'. "
                    f"Expected one of: {VALID_VARIABLE_SENSITIVITIES}"
                )

            value = None
            if "value" in variable:
                value = variable["value"]

            variables.append(
                SchemaintegrationIntegrationVariable(
                    name=name,
                    sensitivity=sensitivity,
                    value=value,
                )
            )

        return IntegrationIntegrationSchema(variables=variables)

    @staticmethod
    def _prepare_schema_for_configuring_integration(
        integration_schema: List[Dict],
    ) -> List[RimeConfigureIntegrationRequestIntegrationVariable]:
        """Validate user provided schema and return its swagger representation.

        Args:
            integration_schema: List[Dict]
                List of Python dicts where each dict represents a variable and
                has the following keys:
                    "name": str (required)
                    "value": str (optional)

        Returns:
            List[RimeConfigureIntegrationRequestIntegrationVariable]:
                List of swagger objects containing representation of each
                dict provided.

        Raises:
            ValueError
                This error is generated when the user provided dictionaries do
                not contain the required information.
        """
        variables = []

        for variable in integration_schema:
            if "name" not in variable:
                raise ValueError(
                    'Missing key "name" in integration_schema\'s variable dict.'
                )
            name = variable["name"]

            value = None
            if "value" in variable:
                value = variable["value"]

            variables.append(
                RimeConfigureIntegrationRequestIntegrationVariable(
                    name=name,
                    value=value,
                )
            )

        return variables

    def get_model_security_report(
        self,
        repo_id: str,
    ) -> dict:
        """Gets the supply chain risk report for a Hugging Face model.

        Args:
            repo_id: str
                ID of the Hugging Face model.
            repo_type: enum
                Currently only Hugging Face is supported.

        Returns:
            Dict:
                A dictionary representation of the model scan result.

        """
        api = swagger_client.SecurityDBApi(self._api_client)

        with RESTErrorHandler():
            resp = api.get_model_security_report(
                repo_id=repo_id,
            )
        return resp.to_dict()
