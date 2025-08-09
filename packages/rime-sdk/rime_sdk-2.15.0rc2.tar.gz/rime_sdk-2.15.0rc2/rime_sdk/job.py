"""Library defining the interfaces for monitoring jobs in the RIME backend."""

import re
import time
from abc import ABC, abstractmethod
from datetime import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional

from rime_sdk.internal.rest_error_handler import RESTErrorHandler
from rime_sdk.swagger import swagger_client
from rime_sdk.swagger.swagger_client import ApiClient
from rime_sdk.swagger.swagger_client.models import RimeJobData, RimeJobMetadata
from rime_sdk.swagger.swagger_client.models import RimeJobStatus as StatedbJobStatus
from rime_sdk.swagger.swagger_client.models import (
    RimeJobType,
    RimeJobView,
    RimeTestRunProgress,
    RimeTestTaskStatus,
)
from rime_sdk.swagger.swagger_client.rest import ApiException
from rime_sdk.test_run import TestRun

CANCELLABLE_JOB_TYPES = [
    RimeJobType.FILE_SCAN,
    RimeJobType.FIREWALL_BATCH_TEST,
    RimeJobType.MODEL_STRESS_TEST,
]
# Format datetimes in user-readable format
DATETIME_FIELDS = ["creation_time", "start_time", "completion_time"]
# Removed if empty or overly verbose
FIELDS_TO_BE_REMOVED = ["job_data", "archived_job_logs"]


class BaseJob(ABC):
    """Abstract class for RIME Jobs.

    This object provides an interface for monitoring the status of a
    job in the RIME backend.
    """

    _job_type: str

    def __init__(self, api_client: ApiClient, job_id: str) -> None:
        """Create a new RIME Job.

        Args:
            api_client: ApiClient
                The client used to query the RIME cluster.
            job_id: str
                The ID of the RIME Job object.
        """
        self._api_client = api_client
        self._job_id = job_id

    def __repr__(self) -> str:
        """Return a string representation of this object."""
        return str(self)

    @property
    def job_id(self) -> str:
        """Return the ID of the Job."""
        return self._job_id

    @property
    def job_type(self) -> str:
        """Return the type of the Job.

        The valid Job types are:
        MODEL_STRESS_TEST, FIREWALL_BATCH_TEST, IMAGE_BUILDER, FILE_SCAN
        """
        return self._job_type

    @property
    def error_msg(self) -> str:
        """The error message, if this job failed."""
        status = self.get_status(verbose=False)
        return f"{status.get('error_msg')}"

    def __str__(self) -> str:
        """Pretty-print the object."""
        # Ping the backend for the full representation of the job and detailed
        # info only for succeeded jobs.
        job = self.get_status(verbose=False)
        ret = {
            "job_id": self._job_id,
            "job_type": self._job_type,
            "status": job.get("status"),
        }
        if job.get("status") == StatedbJobStatus.SUCCEEDED:
            ret.update(self._get_test_run_dict())
        elif job.get("status") == StatedbJobStatus.FAILED:
            ret["error_msg"] = job.get("error_msg")
        job_class = self.__class__.__name__
        return f"{job_class} {ret}"

    def __eq__(self, obj: Any) -> bool:  # noqa: PYI032
        """Check if this job is equivalent to 'obj'."""
        return isinstance(obj, BaseJob) and self._job_id == obj._job_id

    @staticmethod
    def _get_test_run_progress(test_run: RimeTestRunProgress) -> Optional[str]:
        test_batches = test_run.test_batches
        if len(test_batches) == 0:
            return None
        n = sum(batch.status == RimeTestTaskStatus.COMPLETED for batch in test_batches)
        return f"{n:<2} / {len(test_batches):>2} tests completed"

    @abstractmethod
    def _get_progress(self, job: RimeJobMetadata) -> Optional[str]:
        """Pretty print the progress of the test run."""

    # TODO(VAL-2282): refactor this function to have fewer branches and be more readable
    def get_status(  # noqa: PLR0912 (too-many-branches)
        self,
        verbose: bool = True,
        wait_until_finish: bool = False,
        poll_rate_sec: float = 5.0,
    ) -> Dict:
        """Return the current status of the Job.

        Includes flags for blocking until the job is complete and printing
        information to ``stdout``. This method displays the progress and
        running time of jobs.

        If the job has failed, the logs of the testing engine will be dumped
        to ``stdout`` for debugging.

        Arguments:
            verbose: bool
                Specifies whether to print diagnostic information such as progress.
            wait_until_finish: bool
                Specifies whether to block until the job has succeeded or failed.
                If `verbose` is enabled too, information about the job including
                running time and progress will be printed to ``stdout`` every
                ``poll_rate_sec``.
            poll_rate_sec: float
                The frequency in seconds with which to poll the job's status.

        Returns:
            Dict:
                A dictionary representing the job's state.

                .. code-block:: python

                    {
                    "id": str
                    "type": str
                    "status": str
                    "start_time_secs": int64
                    "running_time_secs": double
                    }

        Example:
            .. code-block:: python

                # Block until this job is finished and dump monitoring info to stdout.
                job_status = job.get_status(verbose=True, wait_until_finish=True)
        """
        printed_cancellation_req = False
        printed_poll_string = False
        # Create backend client stubs to use for the remainder of this session.
        api = swagger_client.JobReaderApi(self._api_client)
        with RESTErrorHandler():
            job: RimeJobMetadata = api.get_job(
                job_id=self._job_id, view=RimeJobView.FULL
            ).job
        if verbose:
            print(
                "Job '{}' started at {}".format(  # noqa: UP032
                    job.job_id,
                    datetime.fromtimestamp(job.creation_time.timestamp()),
                )
            )

        # Do not repeat if the job is finished or blocking is disabled.
        while wait_until_finish and job.status not in (
            StatedbJobStatus.SUCCEEDED,
            StatedbJobStatus.FAILED,
            StatedbJobStatus.CANCELLED,
        ):
            time.sleep(poll_rate_sec)
            with RESTErrorHandler():
                job = api.get_job(job_id=self._job_id, view=RimeJobView.FULL).job
                progress = self._get_progress(job)
            if verbose:
                if (
                    not printed_cancellation_req
                    and verbose
                    and job.cancellation_requested
                ):
                    print("Cancellation Requested")
                    # Only print "Cancellation Requested" once.
                    printed_cancellation_req = True

                minute, second = divmod(job.running_time_secs, 60)
                hour, minute = divmod(minute, 60)
                progress_str = f" ({progress})" if progress else ""
                print(
                    "\rStatus: {}, Running Time: {:02}:{:02}:{:05.2f}{}".format(  # noqa: UP032
                        job.status, int(hour), int(minute), second, progress_str
                    ),
                    end="",
                )
                printed_poll_string = True

        # Add a new line if we printed the poll string, because it has `end=""`.
        # This ensures future print statements start on the next line.
        if verbose and printed_poll_string:
            print()

        # Only get the logs if the job has failed, as the
        # primary purpose is debuggability during development.
        model_testing_api = swagger_client.ModelTestingApi(self._api_client)
        if job.status == StatedbJobStatus.FAILED:
            if job.error_msg is not None:
                print(f"Error message from failed job: {job.error_msg}")

            try:
                response = model_testing_api.get_latest_logs(job_id=self._job_id)
                if response.result.chunk:
                    print(
                        "\nLogs from failed job:\n"
                        + self._format_logs(response.result.chunk)
                    )
                else:
                    print("No logs found.")
            except ApiException as e:
                # if logs cannot be found do not raise an error.
                # For most deployments logs cannot be read via this api.
                if e.status != HTTPStatus.NOT_FOUND:
                    raise ValueError(e.reason) from None
            # check for debug logs in the job
            print(f"Debug Logs: {self._get_debug_logs(job)}")

        job_dict = job.to_dict()
        # Hide job data and archived logs in the return value because it can get ugly.
        for field in FIELDS_TO_BE_REMOVED:
            if field in job_dict:
                del job_dict[field]

        for field in DATETIME_FIELDS:
            if field in job_dict and job_dict[field]:
                job_dict[field] = job_dict[field].strftime("%H:%M %B %d, %Y")

        return job_dict

    @staticmethod
    def _format_logs(logs_string: str) -> str:
        # Required to remove any warnings which contain endpoint information from logs.
        logs_without_warning = re.sub(r"^WARNING(.*?)recommended!\n$", "", logs_string)
        return logs_without_warning

    def _get_test_run_dict(self) -> dict:
        """Return a dictionary that is used to help pretty-print this object."""
        return {}

    def cancel(self) -> None:
        """Request to cancel the Job.

        The RIME cluster will mark the Job with "Cancellation Requested" and then clean
        up the Job.
        """
        if self.job_type not in CANCELLABLE_JOB_TYPES:
            raise ValueError(
                "Cancelling jobs is only supported for job types "
                f"{CANCELLABLE_JOB_TYPES}"
            )
        api = swagger_client.JobReaderApi(self._api_client)
        with RESTErrorHandler():
            api.cancel_job(job_id=self.job_id)

    def get_agent_id(self) -> str:
        """Return the Agent ID running the Job."""
        api = swagger_client.JobReaderApi(self._api_client)
        with RESTErrorHandler():
            job = api.get_job(job_id=self._job_id).job
        return job.agent_id.uuid

    def _get_job(self) -> RimeJobData:
        """Return the Job object.

        Get the Test Run ID corresponding to a successful Job.

        Raises:
            ValueError
                This error is generated when the job does not have state 'SUCCEEDED'
                or when the request to the Job Reader service fails.
        """
        # This first step only prevents a rare case where the RIME engine has
        # signaled the test suite has completed but before the upload has completed.
        api = swagger_client.JobReaderApi(self._api_client)
        with RESTErrorHandler():
            job: RimeJobMetadata = api.get_job(job_id=self._job_id).job
        if job.status != StatedbJobStatus.SUCCEEDED:
            raise ValueError(
                f"Job has status {job.status}; "
                "it must have status {StatedbJobStatus.SUCCEEDED} to get results"
            )
        return job.job_data

    def get_job_debug_logs_link(self) -> str:
        """Return a link to the archived logs for a failed Job."""
        api = swagger_client.JobReaderApi(self._api_client)
        with RESTErrorHandler():
            job: RimeJobMetadata = api.get_job(
                job_id=self._job_id, view=RimeJobView.FULL
            ).job
            return self._get_debug_logs(job)

    def _get_debug_logs(self, job: RimeJobMetadata) -> str:
        """Pretty print the archived logs for a failed Job."""
        if job.status != StatedbJobStatus.FAILED:
            return (
                f"Debug logs are not available for this job."
                f"They are only available for failed jobs, "
                f"this job has status {job.status}"
            )
        else:
            try:
                expiration_time = datetime.fromtimestamp(
                    job.archived_job_logs.expiration_time.timestamp()
                )
                if datetime.now() < expiration_time:
                    return (
                        f"Debug logs for the job can found in your blob "
                        f"storage for your job {job.job_id},"
                        f" at the following url {job.archived_job_logs.url}"
                    )
                else:
                    return (
                        f"Debug logs for the job {job.job_id} maybe "
                        f"available in your blob storage. RI platform only"
                        f" has access to a presigned url which has "
                        f"expired. However, the logs themselves might not "
                        f"have expired. Please check your configured blob"
                        f" storage. The logs maybe available in the "
                        f"bucket configured under the following directory:"
                        f" /logs/{job.job_id}. The expired url:"
                        f"{job.archived_job_logs.url}"
                    )
            except AttributeError:
                return "Debug logs are not available for this job"


class Job(BaseJob):
    """This object provides an interface for monitoring a Stress Test Job in the RIME backend."""

    _job_type = RimeJobType.MODEL_STRESS_TEST

    def _get_progress(self, job: RimeJobMetadata) -> Optional[str]:
        """Pretty print the progress of the test run."""
        if job.job_data.stress.progress is None:
            return None
        else:
            return self._get_test_run_progress(job.job_data.stress.progress.test_run)

    def get_test_run_id(self) -> str:
        """Get the Test Run ID corresponding to a successful Job.

        Raises:
            ValueError
                This error is generated when the job does not have state 'SUCCEEDED'
                or when the request to the Job Reader service fails.
        """
        job_data = self._get_job()
        return job_data.stress.test_run_id

    def get_test_run(self) -> TestRun:
        """Get the Test Run object corresponding to a successful Job.

        Raises:
            ValueError
                This error is generated when the job does not have state 'SUCCEEDED'
                or if the request to the Job Reader service fails.
        """
        test_run_id = self.get_test_run_id()
        return TestRun(self._api_client, test_run_id)

    def _get_test_run_dict(self) -> dict:
        """Return a dictionary that is used to help pretty-print this object."""
        ret = {}
        test_run_obj = self.get_test_run()
        test_run_res = test_run_obj.get_result_df()
        for k, v in test_run_res.iloc[0].to_dict().items():
            # Omit metrics from the output dictionary.
            if not str(k).startswith("metrics"):
                ret[k] = v
        return ret


class ContinuousTestJob(BaseJob):
    """This object provides an interface for monitoring a Continuous Test Job in the RIME backend."""

    _job_type = RimeJobType.FIREWALL_BATCH_TEST

    def _get_progress(self, job: RimeJobMetadata) -> Optional[str]:
        """Pretty print the progress of the test run."""
        if job.job_data.continuous_inc.progress is None:
            return None
        test_runs = job.job_data.continuous_inc.progress.test_runs
        total_ct_runs = len(job.job_data.continuous_inc.ct_test_run_ids)
        if total_ct_runs == 0:
            return None
        finished_test_runs = len(
            [
                test_run
                for test_run in test_runs
                if test_run.test_run.status == RimeTestTaskStatus.COMPLETED
            ]
        )
        run_progress = "{:<2} / {:>2} time bins completed".format(  # noqa: UP032
            finished_test_runs, total_ct_runs
        )
        for test_run in test_runs:
            if test_run.test_run.status != RimeTestTaskStatus.COMPLETED:
                batch_progress = self._get_test_run_progress(test_run.test_run)
                if batch_progress is not None:
                    return f"{run_progress}, {batch_progress}"
        return run_progress

    def get_test_run_ids(self) -> str:
        """Get the set of Test Run IDs corresponding to a successful Continuous Test Job.

        Raises:
            ValueError
                This error is generated when the job does not have state 'SUCCEEDED'
                or when the request to the Job Reader service fails.
        """
        job_data = self._get_job()
        return job_data.continuous_inc.ct_test_run_ids

    def get_test_runs(self) -> List[TestRun]:
        """Get the list of Test Run objects corresponding to a successful Continuous Test Job.

        Raises:
            ValueError
                This error is generated when the job does not have state 'SUCCEEDED'
                or if the request to the Job Reader service fails.
        """
        test_run_ids = self.get_test_run_ids()
        return [TestRun(self._api_client, test_run_id) for test_run_id in test_run_ids]

    def _get_test_run_dict(self) -> dict:
        """Return a dictionary that is used to help pretty-print this object."""
        return {}


class ImageBuilderJob(BaseJob):
    """This object provides an interface for monitoring a Image Builder Job in the RIME backend."""

    _job_type = RimeJobType.IMAGE_BUILDER

    def _get_progress(
        self, job: RimeJobMetadata  # noqa: ARG002 (unused-method-argument)
    ) -> Optional[str]:
        """Pretty print the progress of the test run."""
        # TODO: find a good way to pretty print the progress of a ImageBuilderJob
        return None


class FileScanJob(BaseJob):
    """This object provides an interface for monitoring a File Scan Job in the RIME backend."""

    _job_type = RimeJobType.FILE_SCAN

    def _get_progress(
        self, job: RimeJobMetadata  # noqa: ARG002 (unused-method-argument)
    ) -> Optional[str]:
        """Pretty print the progress of the test run."""
        # TODO: find a good way to pretty print the progress of a FileScanJob
        return None


class GenerativeModelTestJob(BaseJob):
    """This object provides an interface for monitoring a Generative Model Test Job in the RIME backend."""

    _job_type = RimeJobType.GENERATIVE_MODEL_TEST

    def _get_progress(
        self, job: RimeJobMetadata  # noqa: ARG002 (unused-method-argument)
    ) -> Optional[str]:
        """Pretty print the progress of the test run."""
        return None
