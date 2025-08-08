"""Library for internal helpers on test objects."""

from http import HTTPStatus
from typing import Optional

from rime_sdk.swagger import swagger_client
from rime_sdk.swagger.swagger_client import ApiClient
from rime_sdk.swagger.swagger_client.models import TestrunresultGetBatchResultResponse
from rime_sdk.swagger.swagger_client.rest import ApiException


def get_batch_result_response(
    test_run_id: str, test_type: str, api_client: Optional[ApiClient] = None
) -> TestrunresultGetBatchResultResponse:
    """Obtain the test batch summary response."""
    api = swagger_client.ResultsReaderApi(api_client)
    try:
        res: TestrunresultGetBatchResultResponse = api.get_batch_result(
            test_run_id=test_run_id, test_type=test_type
        )
        return res
    except ApiException as e:
        if e.status == HTTPStatus.NOT_FOUND:
            raise ValueError(
                f"The test batch for {test_type} and test run "
                f"{test_run_id} was not found."
            ) from None
        raise ValueError(e.reason) from None
