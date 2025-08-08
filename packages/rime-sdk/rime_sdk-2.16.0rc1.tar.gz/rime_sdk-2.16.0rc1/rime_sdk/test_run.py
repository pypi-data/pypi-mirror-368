"""Library that defines the interface to a Test Run object."""

from datetime import datetime
from typing import Iterator, Tuple

import pandas as pd
from deprecated import deprecated

from rime_sdk.internal.rest_error_handler import RESTErrorHandler
from rime_sdk.internal.swagger_parser import (
    parse_category_test_results,
    parse_test_case_result,
    parse_test_run_metadata,
)
from rime_sdk.internal.test_helpers import get_batch_result_response
from rime_sdk.internal.utils import convert_dict_to_html, make_link
from rime_sdk.swagger import swagger_client
from rime_sdk.swagger.swagger_client import ApiClient
from rime_sdk.swagger.swagger_client.models import TestrunresultGetTestRunResponse
from rime_sdk.test_batch import TestBatch


class TestRun:
    """An interface for a RIME Test Run object."""

    def __init__(self, api_client: ApiClient, test_run_id: str) -> None:
        """Create a new ``TestRun`` object.

        Arguments:
            api_client: ApiClient
                The client used to query about the status of the job.
            test_run_id: str
                The ID for the successfully completed Test Run.
        """
        self._api_client = api_client
        self._test_run_id = test_run_id

    @property
    def test_run_id(self) -> str:
        """Return the Test Run ID."""
        return self._test_run_id

    def __repr__(self) -> str:
        """Return a pretty-printed string representation of the object."""
        return f"TestRun(test_run_id={self.test_run_id})"

    def _repr_html_(self) -> str:
        """Return a pretty-printed HTML representation of the object."""
        info = {
            "Test Run ID": self._test_run_id,
            "Link": make_link(
                "https://" + self.get_link(), link_text="Test Run Result Page"
            ),
        }
        return convert_dict_to_html(info)

    def get_link(self) -> str:
        """Return the web app URL for the Test Run page.

        This page contains results for all Test Runs. To jump to the view which
        shows results for this specific Test Run, click on the corresponding time
        bin in the UI.
        """
        # Fetch Test Run metadata and return a dataframe of the single row.
        with RESTErrorHandler():
            api = swagger_client.ResultsReaderApi(self._api_client)
            res: TestrunresultGetTestRunResponse = api.get_test_run(
                test_run_id=self.test_run_id
            )
        return res.test_run.web_app_url.url

    def get_result_df(self) -> pd.DataFrame:
        """Return high level summary information for a complete stress Test Run in a single-row dataframe.

        This dataframe includes information such as model metrics on the reference and\
        evaluation datasets, overall RIME results such as severity across tests,\
        and high level metadata such as the project ID and model task.

        Place these rows together to build a table of test to build a table of test
        run results for comparison. This only works for stress test jobs that
        have succeeded.

        Returns:
            pd.DataFrame:
                A `pandas.DataFrame` object containing the Test Run result.
                Use the `.columns` method on the returned dataframe to see what columns
                represent. Generally, these columns have information
                about the model and datasets as well as summary statistics such as the
                number of failing Test Cases or number of high severity Test Cases.

        Example:
            .. code-block:: python

                test_run = client.get_test_run(some_test_run_id)
                test_run_result_df = test_run.get_result_df()
        """
        api = swagger_client.ResultsReaderApi(self._api_client)
        # Fetch Test Run metadata and return a dataframe of the single row.
        with RESTErrorHandler():
            res: TestrunresultGetTestRunResponse = api.get_test_run(
                test_run_id=self._test_run_id
            )
        # Use utility function for converting Protobuf to a dataframe.
        return parse_test_run_metadata(res.test_run)

    def get_test_cases_df(self, show_test_case_metrics: bool = False) -> pd.DataFrame:
        """Return all the Test Cases for a completed stress Test Run in a dataframe.

        This enables you to perform granular queries on Test Cases.
        For example, if you only care about subset performance tests and want to see
        the results on each feature, you can fetch all the Test Cases in a dataframe,
        then query on that dataframe by test type. This only works on stress test jobs
        that have succeeded.

        Arguments:
            show_test_case_metrics: bool = False
                Whether to show Test Case specific metrics. This could result in a
                sparse dataframe that is returned, since Test Cases return different
                metrics. Defaults to False.

        Returns:
            pd.DataFrame:
                A ``pandas.DataFrame`` object containing the Test Case results.
                Here is a selected list of columns in the output:

                    1. ``test_run_id``: ID of the parent Test Run.
                    2. ``features``: List of features that the Test Case ran on.
                    3. ``test_batch_type``: Type of test that was run (e.g. Subset AUC).
                    4. ``status``: Status of the Test Case (e.g. Pass, Fail, etc.).
                    5. ``severity``: Denotes the severity of the failure of the test.

        Example:
            .. code-block:: python

                # Wait until the job has finished, since this method only works on
                # SUCCEEDED jobs.
                job.get_status(verbose=True, wait_until_finish=True)
                # Get the Test Run result.
                test_run = job.get_test_run()
                # Dump the Test Cases in dataframe ``df``.
                df = test_run.get_test_cases_df()
        """
        api = swagger_client.ResultsReaderApi(self._api_client)
        all_test_cases = []
        # Iterate through the pages of Test Cases and break at the last page.
        page_token = ""
        while True:
            with RESTErrorHandler():
                if page_token == "":
                    res = api.list_test_cases(
                        page_size=20,
                        list_test_cases_query_test_run_id=self._test_run_id,
                    )
                else:
                    res = api.list_test_cases(
                        page_size=20,
                        page_token=page_token,
                    )
            if res.test_cases:
                tc_dicts = [
                    parse_test_case_result(tc, unpack_metrics=show_test_case_metrics)
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

    def get_test_batch(self, test_type: str) -> TestBatch:
        """Return the Test Batch object for the specified test type on this Test Run.

        A ``TestBatch`` object allows a user to query the results
        for the corresponding test. For example, the ``TestBatch``
        object representing ``subset_performance:subset_accuracy`` allows a user
        to understand the results of the ``subset_performance:subset_accuracy``
        test to varying levels of granularity.

        Args:
            test_type: str
                Name of the test. Structured as ``test_type:test_name``, e.g.
                ``subset_performance:subset_accuracy``.

        Returns:
            TestBatch:
                A ``TestBatch`` representing ``test_type``.

        Example:
            .. code-block:: python

                batch = test_run.get_test_batch("unseen_categorical")
        """
        test_batch_obj = TestBatch(self._api_client, self._test_run_id, test_type)
        # check that Test Batch exists by sending a request
        get_batch_result_response(self._test_run_id, test_type, self._api_client)
        return test_batch_obj

    def get_test_batches(self) -> Iterator[TestBatch]:
        """Return all ``TestBatch`` objects for the Test Run.

        Returns:
            Iterator[TestBatch]:
                An iterator of ``TestBatch`` objects.
        """
        api = swagger_client.ResultsReaderApi(self._api_client)
        # Iterate through the pages of Test Cases and break at the last page.
        page_token = ""
        while True:
            with RESTErrorHandler():
                if page_token == "":
                    res = api.results_reader_list_batch_results(
                        page_size=20,
                        test_run_id=self._test_run_id,
                    )
                else:
                    res = api.results_reader_list_batch_results(
                        page_size=20,
                        page_token=page_token,
                    )
            if res.test_batches:
                for test_batch in res.test_batches:
                    yield TestBatch(
                        self._api_client, self._test_run_id, test_batch.test_type
                    )
            # Advance to the next page of Test Cases.
            page_token = res.next_page_token
            # we've reached the last page of Test Cases.
            if not res.has_more:
                break

    def get_category_results_df(
        self,
        show_category_results_metrics: bool = False,
    ) -> pd.DataFrame:
        """Get all category results for a completed stress Test Run in a dataframe.

        This gives you the ability to perform granular queries on category tests.
        This only works on stress test jobs that have succeeded.

        Args:
            show_category_results_metrics: bool
               Boolean flag to request metrics related to the category results.
               Defaults to False.

        Returns:
            pd.DataFrame:
                A ``pandas.DataFrame`` object containing the Test Case results.
                Here is a selected list of columns in the output:
                1. ``id``: ID of the parent Test Run.
                2. ``name``: name of the category test.
                3. ``severity``: Denotes the severity of the failure of the test.
                4. ``test_batch_types``: List of tests that this category  uses.
                5. ``failing_test_types``: List of failing tests in this category.
                6. ``num_none_severity``: Count of tests with NONE severity.
                7. ``num_low_severity``: Count of tests with LOW severity.
                9. ``num_high_severity``: Count of tests with HIGH severity.

        Example:
            .. code-block:: python

                # Wait until the job has finished, since this method only works on
                # SUCCEEDED jobs.
                job.get_status(verbose=True, wait_until_finish=True)
                # Get the Test Run result.
                test_run = job.get_test_run()
                # Dump the Test Cases in dataframe ``df``.
                df = test_run.get_category_results_df()
        """
        api = swagger_client.ResultsReaderApi(self._api_client)
        all_category_tests = []
        with RESTErrorHandler():
            res = api.get_category_results(self._test_run_id)
            if res.category_test_results:
                for category_test_result in res.category_test_results:
                    parsed_result = parse_category_test_results(
                        category_test_result,
                        unpack_metrics=show_category_results_metrics,
                    )
                    all_category_tests.append(parsed_result)
        return pd.DataFrame(all_category_tests)

    # TODO(RAT-2307): Remove this SDK
    @deprecated(
        "get_summary_tests_df has been deprecated in favor of get_category_results_df"
    )
    def get_summary_tests_df(
        self,
        show_summary_test_metrics: bool = False,
    ) -> pd.DataFrame:
        """Get summary tests for a completed stress Test Run in a dataframe.

        This gives you the ability to perform granular queries on summary tests.
        This only works on stress test jobs that have succeeded.

        Returns:
            pd.DataFrame:
                A ``pandas.DataFrame`` object containing the Test Case results.
                Here is a selected list of columns in the output:
                1. ``id``: ID of the parent Test Run.
                2. ``name``: name of the summary test.
                3. ``severity``: Denotes the severity of the failure of the test.
                4. ``test_batch_types``: List of tests that this summary tests uses.
                5. ``failing_test_types``: List of tests in this summary test that fail.
                6. ``num_none_severity``: Count of tests with NONE severity.
                7. ``num_low_severity``: Count of tests with LOW severity.
                9. ``num_high_severity``: Count of tests with HIGH severity.

        Example:
            .. code-block:: python

                # Wait until the job has finished, since this method only works on
                # SUCCEEDED jobs.
                job.get_status(verbose=True, wait_until_finish=True)
                # Get the Test Run result.
                test_run = job.get_test_run()
                # Dump the Test Cases in dataframe ``df``.
                df = test_run.get_summary_tests_df()
        """
        api = swagger_client.ResultsReaderApi(self._api_client)
        all_summary_tests = []
        # Iterate through the pages of Test Cases and break at the last page.
        page_token = ""
        while True:
            with RESTErrorHandler():
                if page_token == "":
                    res = api.list_summary_tests(
                        page_size=20,
                        query_test_run_id=self._test_run_id,
                    )
                else:
                    res = api.list_summary_tests(
                        page_size=20,
                        page_token=page_token,
                    )
            if res.summary_test_results:
                for summary_test_result in res.summary_test_results:
                    parsed_result = parse_category_test_results(
                        summary_test_result,
                        unpack_metrics=show_summary_test_metrics,
                    )
                    all_summary_tests.append(parsed_result)
            # Advance to the next page of Test Cases.
            page_token = res.next_page_token
            # we've reached the last page of Test Cases.
            if not res.has_more:
                break
        return pd.DataFrame(all_summary_tests)


class ContinuousTestRun(TestRun):
    """An interface for an individual RIME continuous Test Run."""

    def __init__(
        self,
        api_client: ApiClient,
        test_run_id: str,
        time_bin: Tuple[datetime, datetime],
    ) -> None:
        """Create a new ContinuousTestRun object.

        Arguments:
            api_client: ApiClient
                The client used to query about the status of the job.
            test_run_id: str
                The ID for the successfully completed Test Run.
            time_bin: Optional[Tuple[datetime, datetime]]
                A tuple of datetime objects indicating the start and end times.
        """
        super().__init__(api_client, test_run_id)
        self._time_bin = time_bin

    def _get_time_bin(self) -> Tuple[datetime, datetime]:
        """Return the time bin for this continuous Test Run."""
        return self._time_bin

    @property
    def start_time(self) -> datetime:
        """Return the start time."""
        return self._get_time_bin()[0]

    @property
    def end_time(self) -> datetime:
        """Return the end time."""
        return self._get_time_bin()[1]

    def get_link(self) -> str:
        """Return the web app URL which points to the Continuous Tests page.

        This page contains results for all Test Runs. To jump to the view which
        shows results for this specific Test Run, click on the corresponding time
        bin in the UI.

        Note: this is a string that should be copy-pasted into a browser.
        """
        # Fetch Test Run metadata and return a dataframe of the single row.
        with RESTErrorHandler():
            api = swagger_client.ResultsReaderApi(self._api_client)
            res: TestrunresultGetTestRunResponse = api.get_test_run(
                test_run_id=self.test_run_id
            )
        # in CT we do not have unique URLs per Test Run so this link doesn't work
        # Maybe TODO: in the BE have the url attribute correspond to this directly
        invalid_url = res.test_run.web_app_url.url
        cutoff_loc = invalid_url.find("test-runs")
        valid_url = invalid_url[:cutoff_loc] + "ai-firewall/continuous-tests"
        return valid_url
