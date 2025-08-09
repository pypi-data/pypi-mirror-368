"""Library defining the interface to a Project."""

import json
import os
from datetime import timedelta
from http import HTTPStatus
from pathlib import Path
from typing import Any, Dict, Iterator, List, NamedTuple, Optional, Tuple, Union

from deprecated import deprecated
from google.protobuf.field_mask_pb2 import FieldMask
from google.protobuf.json_format import MessageToDict

from rime_sdk.continuous_test import ContinuousTest
from rime_sdk.data_collector import DataCollector
from rime_sdk.internal.config_parser import (
    _get_individual_tests_config_swagger,
    convert_single_data_info_to_swagger,
    convert_single_pred_info_to_swagger,
    validate_config,
)
from rime_sdk.internal.decorators import prompt_confirmation
from rime_sdk.internal.file_upload import FileUploadModule
from rime_sdk.internal.rest_error_handler import RESTErrorHandler
from rime_sdk.internal.swagger_utils import parse_str_to_uuid, timedelta_to_rest
from rime_sdk.internal.utils import (
    convert_dict_to_html,
    get_swagger_field_mask,
    make_link,
)
from rime_sdk.job import ContinuousTestJob, Job
from rime_sdk.registry import Registry
from rime_sdk.schedule import Schedule
from rime_sdk.swagger import swagger_client
from rime_sdk.swagger.swagger_client import (
    ApiClient,
    CreateFirewallRequestScheduledCTParameters,
    ProjectActivateScheduleForProjectResponse,
    ProjectScheduleInfo,
    RimeCreateFirewallRequest,
    RimeCreateScheduleRequest,
    RimeCreateScheduleResponse,
    RimeUUID,
    ScheduleSchedule,
)
from rime_sdk.swagger.swagger_client.models import (
    ConfigvalidatorConfigTypeBody,
    DigestConfigDigestFrequency,
    NotificationDigestConfig,
    NotificationJobActionConfig,
    NotificationMonitoringConfig,
    NotificationNotificationType,
    NotificationObjectType,
    NotificationWebhookConfig,
    ProjectProject,
    ProjectsProjectIdUuidBody,
    RimeActorRole,
    RimeCreateNotificationRequest,
)
from rime_sdk.swagger.swagger_client.models import RimeJobStatus as StatedbJobStatus
from rime_sdk.swagger.swagger_client.models import (
    RimeJobType,
    RimeListNotificationsResponse,
    RimeTestType,
    ScheduleIdUuidActivateBody,
    ScheduleIdUuidDeactivateBody,
    SchemanotificationConfig,
)
from rime_sdk.swagger.swagger_client.models.testrun_profiling_config import (
    TestrunProfilingConfig,
)
from rime_sdk.swagger.swagger_client.rest import ApiException
from rime_sdk.test_run import TestRun

NOTIFICATION_TYPE_JOB_ACTION_STR: str = "Job_Action"
NOTIFICATION_TYPE_MONITORING_STR: str = "Monitoring"
NOTIFICATION_TYPE_DIGEST_STR: str = "Daily_Digest"
NOTIFICATION_TYPE_UNSPECIFIED_STR: str = "Unspecified"
NOTIFICATION_TYPES_STR_LIST: List[str] = [
    NOTIFICATION_TYPE_JOB_ACTION_STR,
    NOTIFICATION_TYPE_MONITORING_STR,
    NOTIFICATION_TYPE_DIGEST_STR,
]


def get_job_status_enum(job_status: str) -> str:
    """Get job status enum value from string."""
    if job_status == "pending":
        return StatedbJobStatus.PENDING
    elif job_status == "running":
        return StatedbJobStatus.RUNNING
    elif job_status == "failed":
        return StatedbJobStatus.FAILED
    elif job_status == "succeeded":
        return StatedbJobStatus.SUCCEEDED
    else:
        raise ValueError(
            f"Got unknown job status ({job_status}), "
            f"should be one of: `pending`, `running`, `failed`, `succeeded`"
        )


class ProjectInfo(NamedTuple):
    """ProjectInfo contains static information that describes a Project."""

    project_id: str
    """The unique ID of the Project."""
    name: str
    """Name of the Project."""
    description: str
    """Description of the Project."""
    use_case: Optional[str] = None
    """Description of the use case of the Project."""
    ethical_consideration: Optional[str] = None
    """Description of ethical considerations for this Project."""
    run_time_info: Optional[dict] = None
    """Default runtime information object that specifies how this Project will be run.

       If no runtime information is provided when the test is created or started,
       then this runtime information is used.
    """
    continuous_test_categories: Optional[list] = None
    stress_test_categories: Optional[list] = None
    profiling_config: Optional[dict] = None
    project_test_suite_config: Optional[dict] = None
    active_schedule: Optional[dict] = None
    """Information about the current active schedule for this Project."""


class Project:
    """An interface to a Project object.

    The Project object is used for editing, updating, and deleting Projects.
    """

    def __init__(self, api_client: ApiClient, project_id: str) -> None:
        """Create a Project.

        Args:
            api_client: ApiClient
                The client used to query the status of the job.
            project_id: str
                The unique ID of the Project.
        """
        self._api_client = api_client
        self._project_id = project_id
        self._registry = Registry(self._api_client)
        self._data_collector = DataCollector(self._api_client, self._project_id)

    def __repr__(self) -> str:
        """Return a string representation of the Project object."""
        return f"Project({self._project_id})"

    def _repr_html_(self) -> str:
        """Return HTML representation of the object."""
        info = {
            "Project ID": self._project_id,
            "Link": make_link("https://" + self.get_link(), link_text="Project Page"),
        }
        return convert_dict_to_html(info)

    @property
    def project_id(self) -> str:
        """Return the ID of this Project."""
        return self._project_id

    def _get_project(self) -> ProjectProject:
        """Return a Project from the backend.

        Returns:
            Project:
                A ``Project`` object.
        """
        api = swagger_client.ProjectServiceApi(self._api_client)
        with RESTErrorHandler():
            response = api.get_project(self._project_id)
            return response.project.project

    @property
    def info(self) -> ProjectInfo:
        """Return description, use case and ethical consideration of the Project."""
        project = self._get_project()
        active_schedule = project.active_schedule and project.active_schedule.to_dict()
        return ProjectInfo(
            project_id=self._project_id,
            name=project.name,
            description=project.description,
            use_case=project.use_case,
            ethical_consideration=project.ethical_consideration,
            run_time_info=project.run_time_info,
            active_schedule=active_schedule,
            stress_test_categories=project.stress_test_categories,
            continuous_test_categories=project.continuous_test_categories,
            profiling_config=project.profiling_config,
            project_test_suite_config=project.project_test_suite_config,
        )

    def get_link(self) -> str:
        """Return the web app URL to the Project.

        This link directs to your organization's deployment of RIME.
        You can view more detailed information in the web app, including
        information on your Test Runs, comparisons of those results,
        and monitored models.
        """
        api = swagger_client.ProjectServiceApi(self._api_client)
        with RESTErrorHandler():
            resp = api.get_project_url(project_id_uuid=self._project_id)
        return resp.url.url

    @property
    def name(self) -> str:
        """Return the name of this Project."""
        return self.info.name

    @property
    def description(self) -> str:
        """Return the description of this Project."""
        return self.info.description

    def list_stress_testing_jobs(
        self,
        status_filters: Optional[List[str]] = None,
    ) -> Iterator[Job]:
        """Get list of Stress Testing Jobs for the Project filtered by status.

        Note that this only returns jobs from the last two weeks, because the
        time-to-live of job objects in the cluster is set at two weeks.

        Args:
            status_filters: Optional[List[str]] = None
                Filter for selecting jobs by a union of statuses.
                The following list enumerates all acceptable values.
                ['pending', 'running', 'failed', 'succeeded']
                If omitted, jobs will not be filtered by status.

        Returns:
            Iterator[Job]:
                An iterator of ``Job`` objects.
                These are not guaranteed to be in any sorted order.

        Raises:
            ValueError
                This error is generated when the request to the JobReader
                service fails or when the provided status_filters array has
                invalid values.

        Example:
            .. code-block:: python

                # Get all running and succeeded jobs for a Project.
                jobs = project.list_stress_testing_jobs(
                    status_filters=['pending', 'succeeded'],
                )
                # To get the names of all jobs.
                [job["name"] for job in jobs]
        """
        with RESTErrorHandler():
            # Filter only for Stress Testing jobs.
            selected_types = [RimeJobType.MODEL_STRESS_TEST]
            selected_statuses = []
            if status_filters:
                # This throws a ValueError if status is invalid.
                selected_statuses = [
                    get_job_status_enum(status) for status in status_filters
                ]
            page_token = None
            while True:
                api = swagger_client.JobReaderApi(self._api_client)
                kwargs: Dict[str, Any] = {}
                if page_token is None:
                    kwargs["first_page_query_selected_statuses"] = selected_statuses
                    kwargs["first_page_query_selected_types"] = selected_types
                else:
                    kwargs["page_token"] = page_token
                res = api.list_jobs_for_project(
                    project_id_uuid=self.project_id,
                    page_size=20,
                    **kwargs,
                )
                for job in res.jobs:
                    yield Job(self._api_client, job.job_id)
                if not res.has_more:
                    break
                page_token = res.next_page_token

    def list_scheduled_ct_jobs(
        self,
    ) -> Iterator[ContinuousTestJob]:
        """Get list of Scheduled CT Jobs for the Project.

        Note that this only returns jobs from the last two weeks, because the
        time-to-live of job objects in the cluster is set at two weeks.

        Returns:
            Iterator[ContinuousTestJob]:
                An iterator of ``ContinuousTestJob`` objects.
                These are not guaranteed to be in any sorted order.

        Raises:
            ValueError
                This error is generated when the request to the JobReader
                service fails.

        Example:
            .. code-block:: python

                # Get all Scheduled CT jobs for a Project.
                ct_jobs = project.list_scheduled_ct_jobs()

                # To get the names of all jobs.
                [ct_job["name"] for ct_job in ct_jobs]
        """
        with RESTErrorHandler():
            # Filter only for CT jobs.
            selected_types = [RimeJobType.FIREWALL_BATCH_TEST]
            page_token = None
            while True:
                api = swagger_client.JobReaderApi(self._api_client)
                kwargs: Dict[str, Any] = {}
                if page_token is None:
                    kwargs["first_page_query_selected_types"] = selected_types
                    kwargs["first_page_query_internal_created"] = True
                else:
                    kwargs["page_token"] = page_token
                res = api.list_jobs_for_project(
                    project_id_uuid=self.project_id,
                    page_size=20,
                    **kwargs,
                )
                for job in res.jobs:
                    yield ContinuousTestJob(self._api_client, job.job_id)
                if not res.has_more:
                    break
                page_token = res.next_page_token

    def list_test_runs(
        self,
        test_type: Optional[RimeTestType] = None,
    ) -> Iterator[TestRun]:
        """List the Test Runs associated with this Project.

        Args:
            test_type: Optional[RimeTestType] = None.
                Filter for selecting test runs by RimeTestType.
                If omitted, stress test runs are returned, excluding continuous test runs.

        Returns:
            Iterator[TestRun]:
                An iterator of ``TestRun`` objects.

        Raises:
            ValueError
                This error is generated when the request to the
                ResultsReader Service fails.

        Example:
            .. code-block:: python

                # List all stress test runs in the Project.
                test_runs = project.list_test_runs()
                # Get the IDs of the test runs.
                [test_run.test_run_id for test_run in test_runs]


                # List all continuous test runs in the Project.
                test_runs = project.list_test_runs(RimeTestType.CONTINUOUS_TESTING)
        """
        api = swagger_client.ResultsReaderApi(self._api_client)
        # Iterate through the pages of projects and break at the last page.
        page_token = ""
        while True:
            if page_token == "":
                res = api.list_test_runs(
                    first_page_query_project_id_uuid=self._project_id,
                    first_page_query_testing_type=(
                        test_type
                        if test_type is not None
                        else RimeTestType.STRESS_TESTING_UNSPECIFIED
                    ),
                )
            else:
                res = api.list_test_runs(page_token=page_token)
            if res.test_runs is not None:
                for test_run in res.test_runs:
                    yield TestRun(self._api_client, test_run.test_run_id)
            # Advance to the next page of Test Cases.
            page_token = res.next_page_token
            # we've reached the last page of Test Cases.
            if not res.has_more:
                break

    def create_ct(
        self,
        model_id: str,
        ref_data_id: str,
        bin_size: timedelta,
        scheduled_ct_eval_data_integration_id: Optional[str] = None,
        scheduled_ct_eval_data_info: Optional[dict] = None,
        scheduled_ct_eval_pred_integration_id: Optional[str] = None,
        scheduled_ct_eval_pred_info: Optional[dict] = None,
    ) -> ContinuousTest:
        """Create a ContinuousTest in the current Project.

        Args:
            model_id: str
                The model ID that this ContinuousTest is testing. Model IDs are created
                by the Registry.
            ref_data_id: str
                The ID of the reference dataset that this ContinuousTest compares
                against during testing. Dataset IDs are created by the Registry.
            bin_size: timedelta
                The length of each time bin to test over as a `timedelta` object.
                Must have a minimum value of 1 hour.
            scheduled_ct_eval_data_integration_id: Optional[str]
                The integration ID will be used to fetch eval data.
            scheduled_ct_eval_data_info: Optional[dict]
                The data info needed to fetch eval data.
            scheduled_ct_eval_pred_integration_id: Optional[str]
                The integration ID will be used to fetch eval predictions.
            scheduled_ct_eval_pred_info: Optional[dict]
                The predcition info needed to fetch eval predictions.

        Returns:
            ContinuousTest:
                A ``ContinuousTest`` object that is used to monitor the model.

        Raises:
            ValueError
                This error is generated when the request to the
                ContinuousTest Service fails.

        Example:
            .. code-block:: python

                from datetime import timedelta
                # Create ContinuousTest using previously registered model and dataset IDs.
                ct = project.create_ct(model_id, ref_data_id, timedelta(days=2))
        """
        api = swagger_client.FirewallServiceApi(self._api_client)
        req = RimeCreateFirewallRequest(
            project_id=RimeUUID(uuid=self._project_id),
            model_id=RimeUUID(uuid=model_id),
            ref_data_id=ref_data_id,
            bin_size=timedelta_to_rest(bin_size),
        )
        if scheduled_ct_eval_data_info is not None:
            eval_pred_info = (
                convert_single_pred_info_to_swagger(scheduled_ct_eval_pred_info)
                if scheduled_ct_eval_pred_info is not None
                else None
            )
            req.scheduled_ct_parameters = CreateFirewallRequestScheduledCTParameters(
                eval_data_integration_id=parse_str_to_uuid(
                    scheduled_ct_eval_data_integration_id
                ),
                eval_data_info=convert_single_data_info_to_swagger(
                    scheduled_ct_eval_data_info,
                ),
                eval_pred_integration_id=parse_str_to_uuid(
                    scheduled_ct_eval_pred_integration_id
                ),
                eval_pred_info=eval_pred_info,
            )

        with RESTErrorHandler():
            resp = api.firewall_service_create_firewall(body=req)
        return ContinuousTest(self._api_client, resp.firewall_id.uuid)

    def _get_ct_ids(self) -> List[str]:
        api = swagger_client.ProjectServiceApi(self._api_client)
        with RESTErrorHandler():
            response = api.get_project(project_id_uuid=self._project_id)
            return [dict_id.uuid for dict_id in response.project.project.firewall_ids]

    def get_ct(self) -> ContinuousTest:
        """Return the active ContinuousTest for a Project if one exists.

        Query the backend for an active `ContinuousTest` in this Project which
        can be used to perform ContinuousTest operations. If there is no active
        ContinuousTest for the project, this call will return an error.

        Returns:
            ContinuousTest:
                A ``ContinuousTest`` object.

        Raises:
            ValueError
                This error is generated when the ContinuousTest does not exist
                or when the request to the ContinuousTest Service fails.

        Example:
            .. code-block:: python

                # Get ContinuousTest for this Project.
                ct = project.get_ct()
        """
        ct_ids = self._get_ct_ids()
        if len(ct_ids) == 0 or ct_ids[0] is None:
            raise ValueError("No ContinuousTest found for given Project.")
        return ContinuousTest(self._api_client, ct_ids[0])

    def has_ct(self) -> bool:
        """Check whether a Project has a ContinuousTest."""
        ct_ids = self._get_ct_ids()
        return len(ct_ids) > 0 and ct_ids[0] is not None

    def delete_ct(self, force: Optional[bool] = False) -> None:
        """Delete the ContinuousTest for this Project if one exists.

        Args:
            force: Optional[bool] = False
                When set to True, the ContinuousTest will be deleted immediately. By default,
                a confirmation is required.
        """
        ct = self.get_ct()
        ct.delete_ct(force=force)

    def _list_notification_settings(self) -> RimeListNotificationsResponse:
        """Get list of notifications associated with the current Project."""
        api = swagger_client.NotificationSettingApi(self._api_client)
        with RESTErrorHandler():
            response = api.list_notifications(
                list_notifications_query_object_ids=[self._project_id]
            )
            return response

    def _set_create_notification_setting_config_from_type(
        self, req: RimeCreateNotificationRequest, notif_type: str
    ) -> None:
        if notif_type == NotificationNotificationType.JOB_ACTION:
            req.config.job_action_config = NotificationJobActionConfig()
        elif notif_type == NotificationNotificationType.MONITORING:
            req.config.monitoring_config = NotificationMonitoringConfig()
        elif notif_type == NotificationNotificationType.DIGEST:
            req.config.digest_config = NotificationDigestConfig(
                frequency=DigestConfigDigestFrequency.DAILY
            )

    def _get_notification_type_from_str(self, notif_type: str) -> str:
        if notif_type == NOTIFICATION_TYPE_JOB_ACTION_STR:
            return NotificationNotificationType.JOB_ACTION
        elif notif_type == NOTIFICATION_TYPE_MONITORING_STR:
            return NotificationNotificationType.MONITORING
        elif notif_type == NOTIFICATION_TYPE_DIGEST_STR:
            return NotificationNotificationType.DIGEST
        else:
            raise ValueError(
                f"Notification type must be one of {NOTIFICATION_TYPES_STR_LIST}"
            )

    def _get_notification_type_str(self, notif_type: str) -> str:
        if notif_type == NotificationNotificationType.JOB_ACTION:
            return NOTIFICATION_TYPE_JOB_ACTION_STR
        elif notif_type == NotificationNotificationType.MONITORING:
            return NOTIFICATION_TYPE_MONITORING_STR
        elif notif_type == NotificationNotificationType.DIGEST:
            return NOTIFICATION_TYPE_DIGEST_STR
        else:
            # This function is called only to show the user notification types
            # as string as defined in NOTIFICATION_TYPES_STR_LIST. We will have
            # to update this if we add more notification types in the future.
            # Making it unspecified will not break any SDK/BE mismatch and still
            # show users the new notification type with unspecified tag.
            # This situation should not happen ideally
            return NOTIFICATION_TYPE_UNSPECIFIED_STR

    def get_notification_settings(self) -> Dict:
        """List all Notification settings for the Project.

        Queries the backend to get a list of Notifications settings
        added to the Project. The Notifications are grouped by the type
        of Notification: each type contains a list of emails and webhooks
        which are added to the Notification setting.

        Returns:
            Dict:
                A Dictionary of Notification type and corresponding
                emails and webhooks added for that Notification type.

        Example:
            .. code-block:: python

                notification_settings = project.get_notification_settings()
        """
        notif_list = self._list_notification_settings()
        out: Dict = {}
        for notif in notif_list.notifications:
            notif_type_str = self._get_notification_type_str(notif.notification_type)
            out[notif_type_str] = {}
            out[notif_type_str]["emails"] = notif.emails
            out[notif_type_str]["webhooks"] = []
            for webhook in notif.webhooks:
                out[notif_type_str]["webhooks"].append(webhook.webhook)
        return out

    def _add_notif_entry(
        self,
        notif_type_str: str,
        email: Optional[str],
        webhook_config: Optional[NotificationWebhookConfig],
    ) -> None:
        """Add the email or webhook in the notification settings of notif_type.

        This function should be called with either one of an email or a webhook
        to be added in a single call. emails are checked first and we add a
        webhook only when email is set to None. The function first checks if
        a notification object exists for the give notification type and appends
        the email/webhook if found, else it creates a new notification object
        """
        api = swagger_client.NotificationSettingApi(self._api_client)
        if email is not None and webhook_config is not None:
            raise ValueError(
                "_add_notif_entry expects exactly one of email or "
                "webhook config to be set"
            )
        notif_setting_list = self._list_notification_settings()
        notif_type = self._get_notification_type_from_str(notif_type_str)
        mask = FieldMask()
        for notif_setting in notif_setting_list.notifications:
            if notif_setting.notification_type == notif_type:
                if email is not None:
                    for existing_email in notif_setting.emails:
                        if existing_email == email:
                            print(
                                f"Email: {email} already exists in notification "
                                f"settings for notification type: {notif_type_str}"
                            )
                            return
                    mask.paths.append("emails")
                    notif_setting.emails.append(email)
                elif webhook_config is not None:
                    for existing_webhook in notif_setting.webhooks:
                        if existing_webhook.webhook == webhook_config.webhook:
                            print(
                                f"Webhook: {webhook_config.webhook} "
                                "already exists in Notification settings "
                                f"for Notification type: {notif_type_str}"
                            )
                            return
                    mask.paths.append("webhooks")
                    notif_setting.webhooks.append(webhook_config)
                with RESTErrorHandler():
                    # Note: the FieldMask object is not a Swagger model so we must
                    # serialize it to a dictionary before invoking Swagger API methods.
                    serialized_mask = MessageToDict(mask)
                    body = {"notification": notif_setting, "mask": serialized_mask}
                    api.update_notification(
                        body=body,
                        notification_id_uuid=notif_setting.id.uuid,
                    )
                    return
        # Notification setting does not exist for the notif_type.
        req = RimeCreateNotificationRequest(
            object_type=NotificationObjectType.PROJECT,
            object_id=self.project_id,
            config=SchemanotificationConfig(),
            emails=[],
            webhooks=[],
        )
        self._set_create_notification_setting_config_from_type(req, notif_type)
        notif_entry_str = ""
        if email is not None:
            req.emails.append(email)
            notif_entry_str = "Email " + email
        elif webhook_config is not None:
            req.webhooks.append(webhook_config)
            notif_entry_str = "Webhook " + webhook_config.webhook
        with RESTErrorHandler():
            api.create_notification(body=req)
            print(f"{notif_entry_str} added for Notification type {notif_type_str}")
            return

    def _remove_notif_entry(  # noqa: PLR0912
        self,
        notif_type_str: str,
        email: Optional[str],
        webhook_config: Optional[NotificationWebhookConfig],
    ) -> None:
        """Remove the email or webhook in the notification settings of notif_type.

        This function should be called with either one of an email or a webhook
        to be removed in a single call. emails are checked first and we remove
        webhook only when email is set to None. In case a delete operation
        leads to the notification object having no email or webhook, that
        notification object is deleted as well.
        """
        if email is not None and webhook_config is not None:
            raise ValueError(
                "_remove_notif_entry expects exactly one of email "
                "or webhook config to be set"
            )
        notif_setting_list = self._list_notification_settings()
        notif_type = self._get_notification_type_from_str(notif_type_str)
        mask = FieldMask()
        for notif_setting in notif_setting_list.notifications:
            if notif_setting.notification_type == notif_type:
                found = False
                if email is not None:
                    for existing_email in notif_setting.emails:
                        if existing_email == email:
                            notif_setting.emails.remove(existing_email)
                            mask.paths.append("emails")
                            found = True
                elif webhook_config is not None:
                    for existing_webhook in notif_setting.webhooks:
                        if existing_webhook.webhook == webhook_config.webhook:
                            notif_setting.webhooks.remove(existing_webhook)
                            mask.paths.append("webhooks")
                            found = True
                if found:
                    api = swagger_client.NotificationSettingApi(self._api_client)
                    with RESTErrorHandler():
                        if (
                            len(notif_setting.emails) == 0
                            and len(notif_setting.webhooks) == 0
                        ):
                            api.delete_notification(
                                id_uuid=notif_setting.id.uuid,
                            )
                        else:
                            # Note: the FieldMask object is not a Swagger model, so we
                            # must serialize it to a dictionary before invoking Swagger
                            # API methods.
                            serialized_mask = MessageToDict(mask)
                            body = {
                                "notification": notif_setting,
                                "mask": serialized_mask,
                            }
                            api.update_notification(
                                body=body,
                                notification_id_uuid=notif_setting.id.uuid,
                            )
                        return
        notif_entry_str = ""
        if email is not None:
            notif_entry_str = "Email " + email
        elif webhook_config is not None:
            notif_entry_str = "Webhook " + webhook_config.webhook
        print(f"{notif_entry_str} not found for Notification type {notif_type_str}")

    def add_email(self, email: str, notif_type_str: str) -> None:
        """Add an email to the Notification settings for the specified Notification type.

        The valid Notification types are:
        ["Job_Action", "Monitoring", "Daily_Digest"]

        Example:
            .. code-block:: python

                notification_settings = project.add_email("<email>", "Monitoring")
        """
        if email == "":
            raise ValueError("Email must be a non-empty string")
        return self._add_notif_entry(
            notif_type_str=notif_type_str, email=email, webhook_config=None
        )

    def remove_email(self, email: str, notif_type_str: str) -> None:
        """Remove an email from the Notification settings for the specified Notification type.

        The valid Notification types are:
        ["Job_Action", "Monitoring", "Daily_Digest"]

        Example:
            .. code-block:: python

                notification_settings = project.remove_email("<email>", "Monitoring")
        """
        if email == "":
            raise ValueError("Email must be a non-empty string")
        return self._remove_notif_entry(
            notif_type_str=notif_type_str, email=email, webhook_config=None
        )

    def add_webhook(self, webhook: str, notif_type_str: str) -> None:
        """Add a webhook to the Notification settings for the specified Notification type.

        The valid Notification types are:
        ["Job_Action", "Monitoring", "Daily_Digest"]

        Example:
            .. code-block:: python

                notification_settings = project.add_webhook("<webhook>", "Monitoring")
        """
        if webhook == "":
            raise ValueError("Webhook must be a non empty string")
        webhook_config = NotificationWebhookConfig(webhook=webhook)
        return self._add_notif_entry(
            notif_type_str=notif_type_str, email=None, webhook_config=webhook_config
        )

    def remove_webhook(self, webhook: str, notif_type_str: str) -> None:
        """Remove a webhook from the Notification settings for the specified Notification type.

        The valid Notification types are:
        ["Job_Action", "Monitoring", "Daily_Digest"]

        Example:
            .. code-block:: python

                notification_settings = project.remove_webhook("<webhook>", "Monitoring")
        """
        if webhook == "":
            raise ValueError("Webhook must be a non empty string")
        webhook_config = NotificationWebhookConfig(webhook=webhook)
        return self._remove_notif_entry(
            notif_type_str=notif_type_str, email=None, webhook_config=webhook_config
        )

    @prompt_confirmation("Are you sure you want to delete this Project? (y/n) ")
    def delete(
        self, force: Optional[bool] = False  # noqa: ARG002 (unused-method-argument)
    ) -> None:
        """Delete this Project.

        Args:
            force: Optional[bool] = False
                When set to True, the Project will be deleted immediately. By default,
                a confirmation is required.

        Raises:
            ValueError
                This error is generated when the Project does not exist or when
                the request to the Project service fails.
        """
        api = swagger_client.ProjectServiceApi(self._api_client)

        try:
            api.delete_project(self._project_id)
        except ApiException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                raise ValueError(
                    f"Project with this id {self._project_id} does not exist"
                )
            raise ValueError(e.reason)
        print(f"Project with id {self._project_id} was successfully deleted.")

    @deprecated(
        "register_dataset is replaced by register_and_validate_dataset and will be removed in a future release."
    )
    def register_dataset(
        self,
        name: str,
        data_config: dict,
        integration_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        ct_info: Optional[dict] = None,
        skip_validation: Optional[bool] = False,
        agent_id: Optional[str] = None,
    ) -> str:
        """Register and validate a new dataset in this Project.

        Args:
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
            DatasetValidationError
                This error is generated when the dataset is invalid.

        Example:
            .. code-block:: python

                dataset_id = project.register_dataset(
                    name=DATASET_NAME,
                    data_config={
                        "connection_info": {"data_file": {"path": FILE_PATH}},
                        "data_params": {"label_col": LABEL_COL},
                    },
                    integration_id=INTEGRATION_ID,
                    agent_id=AGENT_ID,
                )
        """
        return self._registry.register_dataset(
            self.project_id,
            name,
            data_config,
            integration_id=integration_id,
            tags=tags,
            metadata=metadata,
            ct_info=ct_info,
            skip_validation=skip_validation,
            agent_id=agent_id,
        )

    def register_and_validate_dataset(
        self,
        name: str,
        data_config: dict,
        integration_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        ct_info: Optional[dict] = None,
        agent_id: Optional[str] = None,
    ) -> Tuple[str, Optional[Job]]:
        """Register and validate a new dataset in this Project.

        Args:
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
            DatasetValidationError
                This error is generated when the dataset is invalid.

        Example:
            .. code-block:: python

                dataset_id = project.register_dataset(
                    name=DATASET_NAME,
                    data_config={
                        "connection_info": {"data_file": {"path": FILE_PATH}},
                        "data_params": {"label_col": LABEL_COL},
                    },
                    integration_id=INTEGRATION_ID,
                    agent_id=AGENT_ID,
                )
        """
        return self._registry.register_and_validate_dataset(
            self.project_id,
            name,
            data_config,
            integration_id=integration_id,
            tags=tags,
            metadata=metadata,
            ct_info=ct_info,
            agent_id=agent_id,
        )

    @deprecated(
        "register_dataset_from_file is replaced by register_and_validate_dataset_from_file and will be removed in a future release."
    )
    def register_dataset_from_file(
        self,
        name: str,
        remote_path: str,
        data_params: Optional[dict] = None,
        integration_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        ct_info: Optional[dict] = None,
        skip_validation: Optional[bool] = False,
        agent_id: Optional[str] = None,
    ) -> str:
        """Register and validate a new dataset in this Project.

        Args:
            name: str
                The chosen name of the dataset.
            remote_path: str
                The path to the dataset artifact.
            data_params: dict
                A dictionary that contains the data parameters.
                The data parameters must match the API specification
                of the `data_info.data_params` field in the `RegisterDataset` request.
            integration_id: Optional[str] = None,
                Provide the integration ID for datasets that require an
                integration.
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
            DatasetValidationError
                This error is generated when the dataset is invalid.
        """
        data_config = {
            "connection_info": {"data_file": {"path": remote_path}},
        }
        if data_params is not None:
            data_config["data_params"] = data_params
        return self._registry.register_dataset(
            self.project_id,
            name,
            data_config,
            integration_id=integration_id,
            tags=tags,
            metadata=metadata,
            ct_info=ct_info,
            skip_validation=skip_validation,
            agent_id=agent_id,
        )

    def register_and_validate_dataset_from_file(
        self,
        name: str,
        remote_path: str,
        data_params: Optional[dict] = None,
        integration_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        ct_info: Optional[dict] = None,
        agent_id: Optional[str] = None,
    ) -> Tuple[str, Optional[Job]]:
        """Register and validate a new dataset in this Project.

        Args:
            name: str
                The chosen name of the dataset.
            remote_path: str
                The path to the dataset artifact.
            data_params: dict
                A dictionary that contains the data parameters.
                The data parameters must match the API specification
                of the `data_info.data_params` field in the `RegisterDataset` request.
            integration_id: Optional[str] = None,
                Provide the integration ID for datasets that require an
                integration.
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
            DatasetValidationError
                This error is generated when the dataset is invalid.
        """
        data_config = {
            "connection_info": {"data_file": {"path": remote_path}},
        }
        if data_params is not None:
            data_config["data_params"] = data_params
        return self._registry.register_and_validate_dataset(
            self.project_id,
            name,
            data_config,
            integration_id=integration_id,
            tags=tags,
            metadata=metadata,
            ct_info=ct_info,
            agent_id=agent_id,
        )

    @deprecated(
        "upload_and_register_dataset_from_file is replaced by upload_register_and_validate_dataset_from_file and will be removed in a future release."
    )
    def upload_and_register_dataset_from_file(
        self,
        name: str,
        file_path: Union[Path, str],
        upload_path: Optional[str] = None,
        data_params: Optional[dict] = None,
        integration_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        ct_info: Optional[dict] = None,
        skip_validation: Optional[bool] = False,
        agent_id: Optional[str] = None,
    ) -> str:
        """Upload, register and validate a new dataset in this Project.

        The uploaded file is stored in the Robust Intelligence cluster in a blob store
        using its file name.

        Args:
            name: str
                The chosen name of the dataset.
            file_path: Union[Path, str]
                The local path to the dataset artifact, to be uploaded to Robust
                Intelligence's blob store.
            upload_path: Optional[str] = None,
                Name of the directory in the blob store file system. If omitted,
                a unique random string will be the directory.
            data_params: Optional[dict] = None,
                A dictionary that contains the data parameters.
                The data parameters must match the API specification
                of the `data_info.data_params` field in the `RegisterDataset` request.
            integration_id: Optional[str] = None,
                Provide the integration ID for datasets that require an
                integration.
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
            DatasetValidationError
                This error is generated when the dataset is invalid.
        """

        if upload_path is not None and upload_path == "":
            raise ValueError("specified upload_path must not be an empty string")
        if isinstance(file_path, str):
            file_path = Path(file_path)
        with RESTErrorHandler():
            fum = FileUploadModule(self._api_client)
            remote_path = fum.upload_dataset_file(file_path, upload_path)
        return self.register_dataset_from_file(
            name,
            remote_path,
            data_params=data_params,
            integration_id=integration_id,
            tags=tags,
            metadata=metadata,
            ct_info=ct_info,
            skip_validation=skip_validation,
            agent_id=agent_id,
        )

    def upload_register_and_validate_dataset_from_file(
        self,
        name: str,
        file_path: Union[Path, str],
        upload_path: Optional[str] = None,
        data_params: Optional[dict] = None,
        integration_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        ct_info: Optional[dict] = None,
        agent_id: Optional[str] = None,
    ) -> Tuple[str, Optional[Job]]:
        """Upload, register and validate a new dataset in this Project.

        The uploaded file is stored in the Robust Intelligence cluster in a blob store
        using its file name.

        Args:
            name: str
                The chosen name of the dataset.
            file_path: Union[Path, str]
                The local path to the dataset artifact, to be uploaded to Robust
                Intelligence's blob store.
            upload_path: Optional[str] = None,
                Name of the directory in the blob store file system. If omitted,
                a unique random string will be the directory.
            data_params: Optional[dict] = None,
                A dictionary that contains the data parameters.
                The data parameters must match the API specification
                of the `data_info.data_params` field in the `RegisterDataset` request.
            integration_id: Optional[str] = None,
                Provide the integration ID for datasets that require an
                integration.
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
            DatasetValidationError
                This error is generated when the dataset is invalid.
        """

        if upload_path is not None and upload_path == "":
            raise ValueError("specified upload_path must not be an empty string")
        if isinstance(file_path, str):
            file_path = Path(file_path)
        with RESTErrorHandler():
            fum = FileUploadModule(self._api_client)
            remote_path = fum.upload_dataset_file(file_path, upload_path)
        return self.register_and_validate_dataset_from_file(
            name,
            remote_path,
            data_params=data_params,
            integration_id=integration_id,
            tags=tags,
            metadata=metadata,
            ct_info=ct_info,
            agent_id=agent_id,
        )

    @deprecated(
        "register_model is replaced by register_and_validate_model and will be removed in a future release."
    )
    def register_model(
        self,
        name: str,
        model_config: Optional[dict] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        external_id: Optional[str] = None,
        integration_id: Optional[str] = None,
        model_endpoint_integration_id: Optional[str] = None,
        skip_validation: Optional[bool] = False,
        agent_id: Optional[str] = None,
    ) -> str:
        """Register and validate a new model in this Project.

        Args:
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
                integration for accessing the model.
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
            ModelValidationError
                This error is generated when the model is invalid.

        Example:
            .. code-block:: python

                model_id = project.register_model(
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
        return self._registry.register_model(
            self.project_id,
            name,
            model_config=model_config,
            tags=tags,
            metadata=metadata,
            external_id=external_id,
            integration_id=integration_id,
            model_endpoint_integration_id=model_endpoint_integration_id,
            skip_validation=skip_validation,
            agent_id=agent_id,
        )

    def register_and_validate_model(
        self,
        name: str,
        model_config: Optional[dict] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        external_id: Optional[str] = None,
        integration_id: Optional[str] = None,
        model_endpoint_integration_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> Tuple[str, Optional[Job]]:
        """Register and validate a new model in this Project.

        Args:
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
                integration for accessing the model.
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
            ModelValidationError
                This error is generated when the model is invalid.

        Example:
            .. code-block:: python

                model_id = project.register_model(
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
        return self._registry.register_and_validate_model(
            self.project_id,
            name,
            model_config=model_config,
            tags=tags,
            metadata=metadata,
            external_id=external_id,
            integration_id=integration_id,
            model_endpoint_integration_id=model_endpoint_integration_id,
            agent_id=agent_id,
        )

    @deprecated(
        "register_model_from_path is replaced by register_and_validate_model_from_path and will be removed in a future release."
    )
    def register_model_from_path(
        self,
        name: str,
        remote_path: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        external_id: Optional[str] = None,
        integration_id: Optional[str] = None,
        model_endpoint_integration_id: Optional[str] = None,
        skip_validation: Optional[bool] = False,
        agent_id: Optional[str] = None,
    ) -> str:
        """Register and validate a new model in this Project.

        Args:
            name: str
                The chosen name of the model.
            remote_path: str
                The path to the model artifact.
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
            ModelValidationError
                This error is generated when the model is invalid.

        Example:
            .. code-block:: python

                model_id = project.register_model_from_path(
                    name=MODEL_NAME,
                    remote_path=MODEL_PATH,
                )
        """
        model_config = {"model_path": {"path": remote_path}}
        return self._registry.register_model(
            self.project_id,
            name,
            model_config,
            tags=tags,
            metadata=metadata,
            external_id=external_id,
            integration_id=integration_id,
            model_endpoint_integration_id=model_endpoint_integration_id,
            skip_validation=skip_validation,
            agent_id=agent_id,
        )

    def register_and_validate_model_from_path(
        self,
        name: str,
        remote_path: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        external_id: Optional[str] = None,
        integration_id: Optional[str] = None,
        model_endpoint_integration_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> Tuple[str, Optional[Job]]:
        """Register and validate a new model in this Project.

        Args:
            name: str
                The chosen name of the model.
            remote_path: str
                The path to the model artifact.
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
            ModelValidationError
                This error is generated when the model is invalid.

        Example:
            .. code-block:: python

                model_id = project.register_model_from_path(
                    name=MODEL_NAME,
                    remote_path=MODEL_PATH,
                )
        """
        model_config = {"model_path": {"path": remote_path}}
        return self._registry.register_and_validate_model(
            self.project_id,
            name,
            model_config,
            tags=tags,
            metadata=metadata,
            external_id=external_id,
            integration_id=integration_id,
            model_endpoint_integration_id=model_endpoint_integration_id,
            agent_id=agent_id,
        )

    @deprecated(
        "upload_and_register_model_from_path is replaced by upload_register_and_validate_model_from_path and will be removed in a future release."
    )
    def upload_and_register_model_from_path(
        self,
        name: str,
        file_path: Union[Path, str],
        upload_model_dir: bool = False,
        upload_hidden: bool = False,
        upload_path: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        external_id: Optional[str] = None,
        integration_id: Optional[str] = None,
        skip_validation: Optional[bool] = False,
        agent_id: Optional[str] = None,
    ) -> str:
        """Upload, register and validate a new model in this Project.

        The uploaded file is stored in the Robust Intelligence cluster in a blob store
        using its file name.

        Args:
            name: str
                The chosen name of the model.
            file_path: Union[Path, str]
                The local path to the model artifact, to be uploaded to Robust
                Intelligence's blob store.
            upload_model_dir: bool = False
                Whether to upload the directory containing the model artifact, in
                addition to the model artifact itself. Note that if set to True, this
                method will upload *everything* in the model's containing directory, so
                only place files required to run the model in the directory.
            upload_hidden: bool = False
                Whether or not to upload hidden files or subdirectories
                (ie. those beginning with a '.') in dir_path.
            upload_path: Optional[str] = None,
                Name of the directory in the blob store file system. If omitted,
                a unique random string will be the directory.
            tags: Optional[List[str]] = None,
                An optional list of tags to associate with the model.
            metadata: Optional[dict] = None,
                An optional dictionary of metadata to associate with the model.
            external_id: Optional[str] = None,
                An optional external ID that can be used to identify the model.
            integration_id: Optional[str] = None,
                Provide the integration ID for models that require an
                integration for access.
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
            ModelValidationError
                This error is generated when the model is invalid.

        Example:
            .. code-block:: python

                model_id = project.upload_and_register_model_from_path(
                    name=MODEL_NAME,
                    file_path=MODEL_PATH,
                )
        """
        if upload_path is not None and upload_path == "":
            raise ValueError("specified upload_path must not be an empty string")
        if isinstance(file_path, str):
            file_path = Path(file_path)
        with RESTErrorHandler():
            fum = FileUploadModule(self._api_client)
            if upload_model_dir:
                remote_dir_path = fum.upload_model_directory(
                    file_path.parent,
                    upload_hidden=upload_hidden,
                    upload_path=upload_path,
                )
                remote_path = os.path.join(remote_dir_path, file_path.name)
            else:
                remote_path = fum.upload_dataset_file(file_path, upload_path)
        return self.register_model_from_path(
            name,
            remote_path,
            tags=tags,
            metadata=metadata,
            external_id=external_id,
            integration_id=integration_id,
            skip_validation=skip_validation,
            agent_id=agent_id,
        )

    def upload_register_and_validate_model_from_path(
        self,
        name: str,
        file_path: Union[Path, str],
        upload_model_dir: bool = False,
        upload_hidden: bool = False,
        upload_path: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        external_id: Optional[str] = None,
        integration_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> Tuple[str, Optional[Job]]:
        """Upload, register and validate a new model in this Project.

        The uploaded file is stored in the Robust Intelligence cluster in a blob store
        using its file name.

        Args:
            name: str
                The chosen name of the model.
            file_path: Union[Path, str]
                The local path to the model artifact, to be uploaded to Robust
                Intelligence's blob store.
            upload_model_dir: bool = False
                Whether to upload the directory containing the model artifact, in
                addition to the model artifact itself. Note that if set to True, this
                method will upload *everything* in the model's containing directory, so
                only place files required to run the model in the directory.
            upload_hidden: bool = False
                Whether or not to upload hidden files or subdirectories
                (ie. those beginning with a '.') in dir_path.
            upload_path: Optional[str] = None,
                Name of the directory in the blob store file system. If omitted,
                a unique random string will be the directory.
            tags: Optional[List[str]] = None,
                An optional list of tags to associate with the model.
            metadata: Optional[dict] = None,
                An optional dictionary of metadata to associate with the model.
            external_id: Optional[str] = None,
                An optional external ID that can be used to identify the model.
            integration_id: Optional[str] = None,
                Provide the integration ID for models that require an
                integration for access.
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
            ModelValidationError
                This error is generated when the model is invalid.

        Example:
            .. code-block:: python

                model_id = project.upload_and_register_model_from_path(
                    name=MODEL_NAME,
                    file_path=MODEL_PATH,
                )
        """
        if upload_path is not None and upload_path == "":
            raise ValueError("specified upload_path must not be an empty string")
        if isinstance(file_path, str):
            file_path = Path(file_path)
        with RESTErrorHandler():
            fum = FileUploadModule(self._api_client)
            if upload_model_dir:
                remote_dir_path = fum.upload_model_directory(
                    file_path.parent,
                    upload_hidden=upload_hidden,
                    upload_path=upload_path,
                )
                remote_path = os.path.join(remote_dir_path, file_path.name)
            else:
                remote_path = fum.upload_dataset_file(file_path, upload_path)
        return self.register_and_validate_model_from_path(
            name,
            remote_path,
            tags=tags,
            metadata=metadata,
            external_id=external_id,
            integration_id=integration_id,
            agent_id=agent_id,
        )

    @deprecated(
        "register_predictions is replaced by register_and_validate_predictions and will be removed in a future release."
    )
    def register_predictions(
        self,
        dataset_id: str,
        model_id: str,
        pred_config: dict,
        integration_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        skip_validation: Optional[bool] = False,
        agent_id: Optional[str] = None,
    ) -> None:
        """Register and validate a new prediction corresponding to a model and a dataset.

        Args:
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
            PredictionsValidationError
                This error is generated when the predictions are invalid.

        Example:
            .. code-block:: python

                project.register_predictions(
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
                    agent_id=AGENT_ID,
                )
        """
        self._registry.register_predictions(
            self.project_id,
            dataset_id,
            model_id,
            pred_config,
            integration_id=integration_id,
            tags=tags,
            metadata=metadata,
            skip_validation=skip_validation,
            agent_id=agent_id,
        )

    def register_and_validate_predictions(
        self,
        dataset_id: str,
        model_id: str,
        pred_config: dict,
        integration_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        agent_id: Optional[str] = None,
    ) -> Optional[Job]:
        """Register and validate a new prediction corresponding to a model and a dataset.

        Args:
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
            PredictionsValidationError
                This error is generated when the predictions are invalid.

        Example:
            .. code-block:: python

                project.register_predictions(
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
                    agent_id=AGENT_ID,
                )
        """
        return self._registry.register_and_validate_predictions(
            self.project_id,
            dataset_id,
            model_id,
            pred_config,
            integration_id=integration_id,
            tags=tags,
            metadata=metadata,
            agent_id=agent_id,
        )

    @deprecated(
        "register_predictions_from_file is replaced by register_and_validate_predictions_from_file and will be removed in a future release."
    )
    def register_predictions_from_file(
        self,
        dataset_id: str,
        model_id: str,
        remote_path: str,
        pred_params: Optional[dict] = None,
        integration_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        skip_validation: Optional[bool] = False,
        agent_id: Optional[str] = None,
    ) -> None:
        """Register and validate a new set of predictions for a model on a dataset.

        Args:
            dataset_id: str,
                The ID of the dataset used to generate the predictions.
            model_id: str,
                The ID of the model used to generate the predictions.
            remote_path: str,
                The path to the prediction artifact.
            pred_params: Optional[dict] = None,
                A dictionary that contains the prediction parameters.
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
            PredictionsValidationError
                This error is generated when the predictions are invalid.

        Example:
            .. code-block:: python

                project.register_predictions_from_file(
                    dataset_id=DATASET_ID,
                    model_id=MODEL_ID,
                    remote_path=PREDICTIONS_PATH,
                    agent_id=AGENT_ID,
                )
        """
        pred_config = {
            "connection_info": {"data_file": {"path": remote_path}},
        }
        if pred_params is not None:
            pred_config["pred_params"] = pred_params
        self._registry.register_predictions(
            self.project_id,
            dataset_id,
            model_id,
            pred_config,
            integration_id=integration_id,
            tags=tags,
            metadata=metadata,
            skip_validation=skip_validation,
            agent_id=agent_id,
        )

    def register_and_validate_predictions_from_file(
        self,
        dataset_id: str,
        model_id: str,
        remote_path: str,
        pred_params: Optional[dict] = None,
        integration_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
        agent_id: Optional[str] = None,
    ) -> Optional[Job]:
        """Register and validate a new set of predictions for a model on a dataset.

        Args:
            dataset_id: str,
                The ID of the dataset used to generate the predictions.
            model_id: str,
                The ID of the model used to generate the predictions.
            remote_path: str,
                The path to the prediction artifact.
            pred_params: Optional[dict] = None,
                A dictionary that contains the prediction parameters.
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
            PredictionsValidationError
                This error is generated when the predictions are invalid.

        Example:
            .. code-block:: python

                project.register_predictions_from_file(
                    dataset_id=DATASET_ID,
                    model_id=MODEL_ID,
                    remote_path=PREDICTIONS_PATH,
                    agent_id=AGENT_ID,
                )
        """
        pred_config = {
            "connection_info": {"data_file": {"path": remote_path}},
        }
        if pred_params is not None:
            pred_config["pred_params"] = pred_params
        return self._registry.register_and_validate_predictions(
            self.project_id,
            dataset_id,
            model_id,
            pred_config,
            integration_id=integration_id,
            tags=tags,
            metadata=metadata,
            agent_id=agent_id,
        )

    def list_datasets(self) -> Iterator[Dict]:
        """Return a list of datasets registered in this Project.

        Returns:
            Iterator[Dict]:
                Iterator of dictionaries: each dictionary represents a
                dataset.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.
        """
        return self._registry.list_datasets(self.project_id)

    def list_models(self) -> Iterator[Dict]:
        """Return a list of models.

        Returns:
            Iterator[Dict]:
                Iterator of dictionaries: each dictionary represents a
                model.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.
        """
        return self._registry.list_models(self.project_id)

    def get_data_collector(self) -> DataCollector:
        """Get Data Collector for Project.

        When Project has no existing Data Collector, this method creates and returns
        a new Data Collector.

        Returns:
            DataCollector:
                Data Collector object for Project

        Raises:
            ValueError:
                This error is generated when the request to the Data Collector
                service fails.
        """
        if self._data_collector is None:
            self._data_collector = DataCollector(self._api_client, self._project_id)
        return self._data_collector

    def get_general_access_roles(self) -> Dict[RimeActorRole, str]:
        """Get the roles of workspace members for the project.

        Returns:
            Dict[RimeActorRole, str]
                Returns a map of Actor Roles for workspace and their
                roles for the project.
        """
        api = swagger_client.ProjectServiceApi(self._api_client)
        with RESTErrorHandler():
            response = api.get_workspace_roles_for_project(
                project_id_uuid=self.project_id,
            )
            roles_map = {}
            for role_pair in response.role_pairs:
                workspace_role = "Workspace Role: " + role_pair.parent_role
                project_role = "Project Role:" + role_pair.subject_role
                roles_map[workspace_role] = project_role
            return roles_map

    def list_predictions(
        self,
        model_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
    ) -> Iterator[Dict]:
        """Return a list of predictions.

        Args:
            model_id: Optional[str] = None
                The ID of the model to which the prediction sets belong.
            dataset_id: Optional[str] = None
                The ID of the dataset to which the prediction sets belong.

        Returns:
            Iterator[Dict]:
                Iterator of dictionaries: each dictionary represents a
                prediction.

        Raises:
            ValueError
                This error is generated when the request to the Registry
                service fails.
        """
        return self._registry.list_predictions(
            self.project_id, model_id=model_id, dataset_id=dataset_id
        )

    def get_dataset(
        self, dataset_id: Optional[str] = None, dataset_name: Optional[str] = None
    ) -> Dict:
        """Return a registered dataset.

        Args:
            dataset_id: Optional[str] = None,
                The ID of the dataset to retrieve.
            dataset_name: Optional[str] = None,
                The name of the dataset to retrieve.

        Returns:
            Dict:
                A dictionary representing the dataset.

        Raises:
            ValueError:
                This error is generated when the request to the Registry
                service fails.
        """
        return self._registry.get_dataset(
            dataset_id=dataset_id, dataset_name=dataset_name
        )

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
        return self._registry.has_dataset(
            dataset_id=dataset_id, dataset_name=dataset_name
        )

    def get_model(
        self, model_id: Optional[str] = None, model_name: Optional[str] = None
    ) -> Dict:
        """Return a registered model.

        Args:
            model_id: Optional[str] = None,
                The ID of the model to retrieve.
            model_name: Optional[str] = None,
                The name of the model to retrieve.

        Returns:
            Dict:
                A dictionary representing the model.

        Raises:
            ValueError:
                This error is generated when the request to the Registry
                service fails.
        """
        return self._registry.get_model(model_id=model_id, model_name=model_name)

    def get_predictions(self, model_id: str, dataset_id: str) -> Dict:
        """Get predictions for a model and dataset.

        Args:
            model_id: str,
                The ID of the model used to generate the predictions.
            dataset_id: str,
                The ID of the dataset used to generate the predictions.

        Returns:
            Dict:
                A dictionary representing the predictions.

        Raises:
            ValueError:
                This error is generated when the request to the Registry
                service fails.
        """
        return self._registry.get_predictions(model_id, dataset_id)

    def delete_dataset(self, dataset_id: str) -> None:
        """Delete a dataset.

        Args:
            dataset_id: str,
                The ID of the dataset to delete.

        Returns:
            None

        Raises:
            ValueError:
                This error is generated when the request to the Registry
                service fails.
        """
        self._registry.delete_dataset(dataset_id=dataset_id)

    def delete_model(self, model_id: str) -> None:
        """Delete a model.

        Args:
            model_id: str,
                The ID of the model to delete.

        Returns:
            None

        Raises:
            ValueError:
                This error is generated when the request to the Registry
                service fails.
        """
        self._registry.delete_model(model_id=model_id)

    def delete_predictions(self, model_id: str, dataset_id: str) -> None:
        """Delete predictions for a model and dataset.

        Args:
            model_id: str,
                The ID of the model used to generate the predictions.
            dataset_id: str,
                The ID of the dataset used to generate the predictions.

        Returns:
            None

        Raises:
            ValueError:
                This error is generated when the request to the Registry
                service fails.
        """
        self._registry.delete_predictions(model_id, dataset_id)

    def update_stress_test_categories(self, categories: List[str]) -> None:
        """Update the project's stress test categories.

        Args:
            categories: List[str]
                The list of stress test categories to update.

        Returns:
            None

        Raises:
            ValueError
                This error is generated when the request to the Project service fails.
        """
        project = ProjectProject(stress_test_categories=categories)
        body = ProjectsProjectIdUuidBody(
            project_id=RimeUUID(uuid=self._project_id),
            project=project,
            mask=get_swagger_field_mask(project),
        )
        api = swagger_client.ProjectServiceApi(self._api_client)
        with RESTErrorHandler():
            api.update_project(body=body, project_id_uuid=self._project_id)

    def update_ct_categories(self, categories: List[str]) -> None:
        """Update the project's continuous test categories.

        Args:
            categories: List[str]
                The list of continuous test categories to update.

        Returns:
            None

        Raises:
            ValueError
                This error is generated when the request to the Project service fails.
        """
        project = ProjectProject(continuous_test_categories=categories)
        body = ProjectsProjectIdUuidBody(
            project_id=RimeUUID(uuid=self._project_id),
            project=project,
            mask=get_swagger_field_mask(project),
        )
        api = swagger_client.ProjectServiceApi(self._api_client)
        with RESTErrorHandler():
            api.update_project(body=body, project_id_uuid=self._project_id)

    def update_model_profiling_config(self, model_profiling_config: dict) -> None:
        """Update the project's model profiling configuration.

        Args:
            model_profiling_config: dict
                Model profiling configuration with which to update the project.

        Returns:
            None

        Raises:
            ValueError
                This error is generated when the request to the Project service fails.
        """
        with RESTErrorHandler():
            cv_api = swagger_client.ConfigValidatorApi(self._api_client)
            validate_body = ConfigvalidatorConfigTypeBody(
                config_json=json.dumps(model_profiling_config),
            )
            cv_api.config_validator_validate_test_config(
                config_type="CONFIG_TYPE_MODEL_PROFILING", body=validate_body
            )
        project = ProjectProject(
            profiling_config=TestrunProfilingConfig(
                model_profiling=model_profiling_config
            )
        )
        body = ProjectsProjectIdUuidBody(
            project_id=RimeUUID(uuid=self._project_id),
            project=project,
            mask=get_swagger_field_mask(project),
        )
        api = swagger_client.ProjectServiceApi(self._api_client)
        with RESTErrorHandler():
            api.update_project(body=body, project_id_uuid=self._project_id)

    def update_data_profiling_config(self, data_profiling_config: dict) -> None:
        """Update the project's data profiling configuration.

        Args:
            data_profiling_config: dict
                Data profiling configuration with which to update the project.

        Returns:
            None

        Raises:
            ValueError
                This error is generated when the request to the Project service fails.
        """
        with RESTErrorHandler():
            cv_api = swagger_client.ConfigValidatorApi(self._api_client)
            validate_body = ConfigvalidatorConfigTypeBody(
                config_json=json.dumps(data_profiling_config),
            )
            cv_api.config_validator_validate_test_config(
                config_type="CONFIG_TYPE_DATA_PROFILING", body=validate_body
            )
        project = ProjectProject(
            profiling_config=TestrunProfilingConfig(
                data_profiling=data_profiling_config
            )
        )
        body = ProjectsProjectIdUuidBody(
            project_id=RimeUUID(uuid=self._project_id),
            project=project,
            mask=get_swagger_field_mask(project),
        )
        api = swagger_client.ProjectServiceApi(self._api_client)
        with RESTErrorHandler():
            api.update_project(body=body, project_id_uuid=self._project_id)

    def update_test_suite_config(self, test_suite_config: dict) -> None:
        """Update the project's test suite config.

        Args:
            test_suite_config: dict
                Test suite configuration with which to update the project.

        Returns:
            None

        Raises:
            ValueError
                This error is generated when the request to the Project service fails.
        """
        cv_api = swagger_client.ConfigValidatorApi(self._api_client)
        # We allow users to specify the individual tests config as a dict, but the BE
        # expects a JSON string.
        if "individual_tests_config" in test_suite_config:
            # Allow the user to pass in a JSON string as well as a dict.
            if isinstance(test_suite_config["individual_tests_config"], dict):
                test_suite_config[
                    "individual_tests_config"
                ] = _get_individual_tests_config_swagger(
                    test_suite_config["individual_tests_config"]
                )
        with RESTErrorHandler():
            validate_body = ConfigvalidatorConfigTypeBody(
                config_json=json.dumps(test_suite_config),
            )
            cv_api.config_validator_validate_test_config(
                config_type="CONFIG_TYPE_TEST_SUITE", body=validate_body
            )
            project = ProjectProject(project_test_suite_config=test_suite_config)
            body = ProjectsProjectIdUuidBody(
                project_id=RimeUUID(uuid=self._project_id),
                project=project,
                mask=get_swagger_field_mask(project),
            )
            api = swagger_client.ProjectServiceApi(self._api_client)
            api.update_project(body=body, project_id_uuid=self._project_id)

    def update_run_time_info(self, run_time_info: dict) -> None:
        """Update the runtime information object that specifies how this Project runs.

        If no runtime information is provided when the test is created or started,
        then this runtime information is used.

        Args:
            run_time_info: dict
                Runtime information object with which to update the Project.

        Returns:
            None

        Raises:
            ValueError
                This error is generated when the request to the Project service fails.
        """
        project = ProjectProject(run_time_info=run_time_info)
        body = ProjectsProjectIdUuidBody(
            project_id=RimeUUID(uuid=self._project_id),
            project=project,
            mask=get_swagger_field_mask(project),
        )
        api = swagger_client.ProjectServiceApi(self._api_client)
        with RESTErrorHandler():
            api.update_project(body=body, project_id_uuid=self._project_id)

    def get_schedule(self, schedule_id: str) -> Schedule:
        """Return a schedule.

        Returns:
            Schedule:
                Schedule object for the Project.

        Raises:
            ValueError:
                This error is generated when the request to the Schedule service fails.
        """
        schedule = Schedule(self._api_client, schedule_id)
        schedule_object = schedule.info
        if schedule_object.project_id != self.project_id:
            raise ValueError(
                f"Schedule {schedule_id} does not belong to project {self.project_id}.  "
                f"Schedule belongs to project {schedule_object.project_id}."
            )

        return schedule

    def get_active_schedule(self) -> Schedule:
        """Return the active schedule.

        Returns:
            Schedule:
                Schedule object for the Project.

        Raises:
            ValueError:
                This error is generated when the request to the Schedule service fails.
        """

        project = self._get_project()
        if project.active_schedule is None:
            raise ValueError("Project has no active schedule.")

        return self.get_schedule(project.active_schedule.schedule_id.uuid)

    def create_schedule(
        self, test_run_config: dict, frequency_cron_expr: str
    ) -> Schedule:
        """Create a new schedule for the project.

        Args:
            test_run_config: dict,
                The test run configuration to use for the schedule, which specifies
                unique ids to locate the model and datasets to be used for the test.
            frequency_cron_expr: str,
                The cron expression for the frequency of the schedule.  Accepts
                "@hourly", "@daily", "@weekly" or "@monthly"

        Returns:
            Schedule:
                Schedule object associated with the Project.

        Raises:
            ValueError:
                This error is generated when the request to the Schedule service fails.
        """
        api = swagger_client.ScheduleServiceApi(self._api_client)
        validate_config(test_run_config)
        with RESTErrorHandler():
            body = RimeCreateScheduleRequest(
                project_id=RimeUUID(self.project_id),
                test_run_config=test_run_config,
                frequency_cron_expr=frequency_cron_expr,
            )

            response: RimeCreateScheduleResponse = api.create_schedule(body=body)

            return Schedule(self._api_client, schedule_id=response.schedule_id.uuid)

    def update_schedule(
        self,
        schedule_id: str,
        frequency_cron_expr: str,
    ) -> ScheduleSchedule:
        """Update a schedule associated with the project.

        Currently only the frequency can be updated.

        Args:
            schedule_id: str,
                The ID of the schedule to update.
            frequency_cron_expr: str,
                The cron expression for the frequency of the schedule.  Accepts
                "@hourly", "@daily", "@weekly" or "@monthly"

        Returns:
            Schedule:
                The updated schedule object.

        Raises:
            ValueError:
                This error is generated when the request to the Schedule service fails.
        """
        schedule = Schedule(self._api_client, schedule_id)

        if schedule.info.project_id != self.project_id:
            raise ValueError(
                f"Schedule {schedule_id} does not belong to project {self.project_id}.  "
                f"Schedule belongs to project {schedule.info.project_id}."
            )

        return schedule.update(
            frequency_cron_expr=frequency_cron_expr,
        )

    def delete_schedule(self, schedule_id: str) -> None:
        """Delete a schedule.

        Args:
            schedule_id: str,
                The ID of the schedule to delete.

        Returns:
            None

        Raises:
            ValueError:
                This error is generated when the request to the Schedule service fails.
        """
        schedule = Schedule(self._api_client, schedule_id)
        schedule_object = schedule.info
        if schedule_object.project_id != self.project_id:
            raise ValueError(
                f"Schedule {schedule_id} does not belong to project {self.project_id}.  "
                f"Schedule belongs to project {schedule_object.project_id}."
            )

        schedule.delete()

    def activate_schedule(
        self,
        schedule_id: str,
    ) -> dict:
        """Activate a schedule for this project.

        Returns:
            A dict containing the response from the Project service.

        Raises:
            ValueError:
                This error is generated when the request to the Project service fails.
            AttributeError:
                This error is generated when the response from the Project service
                is not as expected.  This should not happen.
        """
        with RESTErrorHandler():
            body = ScheduleIdUuidActivateBody(
                project_id=RimeUUID(uuid=self._project_id),
                schedule_id=RimeUUID(uuid=schedule_id),
            )
            api = swagger_client.ProjectServiceApi(self._api_client)
            response: ProjectActivateScheduleForProjectResponse = (
                api.activate_schedule_for_project(
                    body=body,
                    project_id_uuid=self._project_id,
                    schedule_id_uuid=schedule_id,
                )
            )
            active_schedule: ProjectScheduleInfo = response.active_schedule
            try:
                return active_schedule.to_dict()
            except AttributeError as e:
                raise AttributeError(
                    "Response from Project service is not as expected.  Please try to activate the schedule again"
                ) from e

    def deactivate_schedule(
        self,
        schedule_id: str,
    ) -> None:
        """Deactivate a schedule for this project.

        Returns:
            None

        Raises:
            ValueError:
                This error is generated when the request to the Project service fails.
        """
        with RESTErrorHandler():
            body = ScheduleIdUuidDeactivateBody(
                project_id=RimeUUID(uuid=self._project_id),
                schedule_id=RimeUUID(uuid=schedule_id),
            )
            api = swagger_client.ProjectServiceApi(self._api_client)
            api.deactivate_schedule_for_project(
                body=body,
                project_id_uuid=self._project_id,
                schedule_id_uuid=schedule_id,
            )
