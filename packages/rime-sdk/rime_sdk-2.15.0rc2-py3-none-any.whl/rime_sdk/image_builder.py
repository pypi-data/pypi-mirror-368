"""Library defining the interface to Image Builder jobs."""

import time
from typing import Any, Dict, List, Optional

from rime_sdk.internal.rest_error_handler import RESTErrorHandler
from rime_sdk.swagger.swagger_client import ApiClient, ImageRegistryApi
from rime_sdk.swagger.swagger_client.models import (
    ManagedImagePackageRequirement,
    ManagedImagePipRequirement,
    RimeManagedImage,
    RimeManagedImageStatus,
)


class ImageBuilder:
    """An interface to an Image Builder object."""

    def __init__(
        self,
        api_client: ApiClient,
        name: str,
        requirements: Optional[List[ManagedImagePipRequirement]] = None,
        package_requirements: Optional[List[ManagedImagePackageRequirement]] = None,
        python_version: Optional[str] = None,
    ) -> None:
        """Create a new Image Builder.

        Args:
            api_client: ApiClient
                The client used to query about the status of the Job.
            name: str
                The name of the Managed Image that this object monitors.
            requirements: Optional[List[ManagedImage.PipRequirement]] = None
                Optional list of pip requirements to be installed on this Image.
            package_requirements: Optional[List[ManagedImage.PackageRequirement]] = None
                Optional list of system package requirements to be installed on
                this Image.
            python_version: Optional[str]
                An optional version string specifying only the major and minor version
                for the python interpreter used. The string should be of the format
                X.Y and be present in the set of supported versions.
        """

        self._api_client = api_client
        self._name = name
        self._requirements = requirements
        self._package_requirements = package_requirements
        self._python_version = python_version

    def __eq__(self, obj: Any) -> bool:  # noqa: PYI032
        """Check if this builder is equivalent to 'obj'."""
        return isinstance(obj, ImageBuilder) and self._name == obj._name

    def __str__(self) -> str:
        """Pretty-print the object."""
        ret = {"name": self._name}
        if self._requirements:
            ret["requirements"] = str(
                [f"{req.name}{req.version_specifier}" for req in self._requirements]
            )
        if self._package_requirements:
            ret["package_requirements"] = str(
                [
                    f"{req.name}{req.version_specifier}"
                    for req in self._package_requirements
                ]
            )
        if self._python_version:
            ret["python_version"] = self._python_version
        return f"ImageBuilder {ret}"

    def get_status(
        self,
        verbose: bool = True,
        wait_until_finish: bool = False,
        poll_rate_sec: float = 5.0,
    ) -> Dict:
        """Return the status of the Image Build Job.

        This method includes a toggle to wait until the Image Build job
        finishes.

        Arguments:
            verbose: bool
                Specifies whether to print diagnostic information such as logs.
                By default, this value is set to True.
            wait_until_finish: bool
                Specifies whether to block until the Image is READY or FAILED.
                By default, this value is set to False.
            poll_rate_sec: float
                The frequency with which to poll the Image's build status.
                By default, this value is set to 5 seconds.

        Returns:
            Dict:
                A dictionary representing the Image's state.
        """
        # Create backend client stubs to use for the remainder of this session.
        image = RimeManagedImage(status=RimeManagedImageStatus.UNSPECIFIED)
        if verbose:
            print(f"Querying for Managed Image '{self._name}':")
        # Do not repeat if the job is finished or blocking is disabled.
        repeat = True
        poll_count = 0
        api = ImageRegistryApi(self._api_client)
        while repeat and image.status not in (
            RimeManagedImageStatus.FAILED,
            RimeManagedImageStatus.OUTDATED,
            RimeManagedImageStatus.READY,
        ):
            with RESTErrorHandler():
                image = api.get_image(name=self._name).image
            if verbose:
                status_name = image.status
                print(
                    f"\rStatus: {status_name}, Poll Count: {poll_count}",
                    end="",
                )
            if wait_until_finish:
                time.sleep(poll_rate_sec)
            else:
                repeat = False
            poll_count += 1

            # TODO(VAL-2433): Add ability to get and print logging information from a
            # failed build.

        return image.to_dict()
