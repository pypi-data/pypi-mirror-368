"""Library defining the interface to a Test Batch object."""

import pandas as pd

from rime_sdk.internal.rest_error_handler import RESTErrorHandler
from rime_sdk.internal.swagger_parser import (
    parse_test_batch_result,
    parse_test_case_result,
)
from rime_sdk.internal.test_helpers import get_batch_result_response
from rime_sdk.swagger import swagger_client
from rime_sdk.swagger.swagger_client import ApiClient


class TestBatch:
    """An interface for a Test Batch object in a RIME Test Run."""

    def __init__(self, api_client: ApiClient, test_run_id: str, test_type: str) -> None:
        """Contains information about a ``TestBatch`` object.

        Args:
            api_client: ApiClient
                The client used to query about the status of the job.
            test_run_id: str
                The ID for the Test Run this Test Batch belong to.
            test_type: str
                The test type of this Test Batch e.g. unseen_categorical.
        """
        self._api_client = api_client
        self._test_run_id = test_run_id
        self._test_type = test_type

    def __repr__(self) -> str:
        """Return a string representation of the Test Batch."""
        return (
            f"TestBatch(test_run_id={self._test_run_id}, test_type={self._test_type})"
        )

    @property
    def test_run_id(self) -> str:
        """Return the Test Run ID of the Test Batch."""
        return self._test_run_id

    @property
    def test_type(self) -> str:
        """Return the type of the Test Batch."""
        return self._test_type

    def summary(self, show_batch_metrics: bool = False) -> pd.Series:
        """Return the Test Batch summary as a Pandas Series.

        The summary contains high level information about a Test Batch.
        For example, the name of the Test Batch, the category, and the
        severity of the Test Batch as a whole.

        Returns:
            pd.Series:
                A Pandas Series with the following columns (and optional additional
                columns for batch-level metrics):

                    1. test_run_id
                    2. test_type
                    3. test_name
                    4. category
                    5. duration_in_millis
                    6. severity
                    7. failing_features
                    8. description
                    9. summary_counts.total
                    10. summary_counts.pass
                    11. summary_counts.fail
                    12. summary_counts.warning
                    13. summary_counts.skip
        """
        res = get_batch_result_response(
            self._test_run_id,
            self._test_type,
            self._api_client,
        )
        return parse_test_batch_result(
            res.test_batch, unpack_metrics=show_batch_metrics
        )

    def get_test_cases_df(self) -> pd.DataFrame:
        """Return all Test Cases in the Test Batch as a Pandas DataFrame.

        Different tests will have different columns/information.
        For example, some tests may have a column representing
        the number of failing rows.

        Returns:
            pd.DataFrame:
                A Pandas Dataframe where each row represents a Test Case.

        Example:
            .. code-block:: python

                # Wait until the job has finished, since this method only works on
                # SUCCEEDED jobs.
                job.get_status(verbose=True, wait_until_finish=True)
                # Get the Test Run result.
                test_run = job.get_test_run()
                # Get the "subset accuracy" Test Batch from this Test Run.
                test_batch = test_run.get_test_batch("subset_performance:subset_recall")
                # Return the Test Cases from this Test Batch in a dataframe ``df``.
                df = test_batch.get_test_cases_df()
        """
        # don't forget to exhaust pages if necessary
        api = swagger_client.ResultsReaderApi(self._api_client)
        all_test_cases = []
        # Iterate through the pages of Test Cases and break at the last page.
        page_token = ""
        while True:
            with RESTErrorHandler():
                if page_token == "":
                    res = api.list_test_cases(
                        list_test_cases_query_test_run_id=self._test_run_id,
                        list_test_cases_query_test_types=[self._test_type],
                        page_size=20,
                    )
                else:
                    res = api.list_test_cases(
                        page_token=page_token,
                        page_size=20,
                    )
            if res.test_cases:
                tc_dicts = [
                    parse_test_case_result(tc, unpack_metrics=True)
                    for tc in res.test_cases
                ]
                # Concatenate the list of Test Case dictionaries.
                all_test_cases += tc_dicts
            # Advance to the next page of Test Cases.
            page_token = res.next_page_token

            # we've reached the last page of Test Cases.
            if not res.has_more:
                break

        return pd.DataFrame(all_test_cases)
