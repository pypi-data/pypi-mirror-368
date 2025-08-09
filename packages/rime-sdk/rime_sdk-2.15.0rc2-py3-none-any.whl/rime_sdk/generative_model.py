"""Library defining the interface to work with generative models."""

from typing import Iterator, Optional

from typing_extensions import deprecated

from rime_sdk.internal.rest_error_handler import RESTErrorHandler
from rime_sdk.job import GenerativeModelTestJob
from rime_sdk.swagger.swagger_client import ApiClient
from rime_sdk.swagger.swagger_client import (
    GenerativeValidationApi as GenerativeModelTestingApi,
)
from rime_sdk.swagger.swagger_client import (
    GenerativevalidationGenerativeValidationResult,
    GenerativevalidationGetResultsResponse,
    GenerativevalidationStartTestRequest,
    GenerativevalidationStartTestResponse,
    RimeUUID,
)


class GenerativeModel:
    """The interface to the Generative Model Testing API."""

    def __init__(self, api_client: ApiClient):
        """Initialize the Generative Model interface.

        Args:
            api_client: The API client to use.
        """
        self._api_client = api_client

    @deprecated(
        "This method has been deprecated in favor of the new SDK and will be removed in a future version.  Find new "
        "SDK in the package `robustintelligence`."
    )
    def start_test(
        self,
        url: str,
        endpoint_payload_template: str,
        response_json_path: str,
        http_headers: Optional[dict] = None,
        name: Optional[str] = None,
        http_auth_integration_id: Optional[str] = None,
        mutual_tls_integration_id: Optional[str] = None,
    ) -> GenerativeModelTestJob:
        """Start a Generative Model Test.

        Args:
            url: The URL to test.
            http_headers: The HTTP headers to use.
            endpoint_payload_template: The endpoint payload template to use.
            response_json_path: The response JSON path to use.
            name: A name to identify your generative test run.
            http_auth_integration_id: The HTTP Auth Integration ID.
            mutual_tls_integration_id: The Mutual TLS Integration ID.

        Returns:
            GenerativeModelTestJob: The Generative Model Test Job.
        """
        http_auth_uuid = (
            RimeUUID(http_auth_integration_id)
            if http_auth_integration_id is not None
            else None
        )
        mtls_uuid = (
            RimeUUID(mutual_tls_integration_id)
            if mutual_tls_integration_id is not None
            else None
        )

        request = GenerativevalidationStartTestRequest(
            url=url,
            http_headers=http_headers,
            endpoint_payload_template=endpoint_payload_template,
            response_json_path=response_json_path,
            name=name,
            http_auth_integration_id=http_auth_uuid,
            mutual_tls_integration_id=mtls_uuid,
        )
        with RESTErrorHandler():
            res: GenerativevalidationStartTestResponse = GenerativeModelTestingApi(
                self._api_client
            ).start_generative_test(body=request)
            if res.job_id is None:
                raise ValueError(
                    "Job ID is missing from the response, please try making the request again."
                )

            return GenerativeModelTestJob(self._api_client, res.job_id.uuid)

    @deprecated(
        "This method has been deprecated in favor of the new SDK and will be removed in a future version.  Find new "
        "SDK in the package `robustintelligence`."
    )
    def get_results(
        self,
        job_id_uuid: str,
        page_size: Optional[int] = 10,
    ) -> Iterator[GenerativevalidationGenerativeValidationResult]:
        """Get the results of a Generative Model Test.

        Args:
            job_id_uuid: The job ID UUID.
            page_size: The number of results per request.  Defaults to 10.

        Returns:
            An iterator of Generative Model Test Results.
        """
        page_token = ""
        with RESTErrorHandler():
            while True:
                res: GenerativevalidationGetResultsResponse = GenerativeModelTestingApi(
                    self._api_client
                ).results(
                    job_id_uuid=job_id_uuid,
                    page_token=page_token,
                    page_size=page_size,
                )

                yield from res.results

                if not res.has_more:
                    break

                page_token = res.next_page_token
