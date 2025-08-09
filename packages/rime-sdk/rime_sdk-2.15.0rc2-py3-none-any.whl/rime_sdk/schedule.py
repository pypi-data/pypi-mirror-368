"""Library defining the interface for the schedule API."""

from __future__ import annotations

import logging
from typing import NamedTuple

from rime_sdk.internal.rest_error_handler import RESTErrorHandler
from rime_sdk.swagger.swagger_client import (
    ApiClient,
    RimeGetScheduleResponse,
    RimeUpdateScheduleResponse,
)
from rime_sdk.swagger.swagger_client import ScheduleSchedule as ScheduleSchema
from rime_sdk.swagger.swagger_client import (
    ScheduleServiceApi,
    SchedulesScheduleScheduleIdUuidBody,
)

logger = logging.getLogger(__name__)


class ScheduleInfo(NamedTuple):
    """A named tuple for the schedule information."""

    project_id: str
    schedule_id: str
    test_run_config: dict
    frequency_cron_expr: str


class Schedule:
    """An interface for the schedule API.

    This interface provides methods to interact with the schedule API which allows
    you to manage schedules with various methods.

    Args:
        api_client: The API client.
        schedule_id: The schedule ID.
    """

    def __init__(self, api_client: ApiClient, schedule_id: str) -> None:
        """Initialize the schedule interface.

        Args:
            api_client: The API client.
            schedule_id: The schedule ID to interface with.
        """
        self._api_client = api_client
        self._schedule_id = schedule_id

    def __repr__(self) -> str:
        """Get the string representation of the schedule."""
        return f"{self.__class__.__name__}({self._schedule_id})"

    def __str__(self) -> str:
        """Get the string form of the schedule."""
        return f"Schedule  (ID: {self._schedule_id})"

    def __eq__(self, other: object) -> bool:
        """Check if the schedule is equal to another schedule."""
        if not isinstance(other, Schedule):
            return False

        return self._schedule_id == other._schedule_id

    @property
    def schedule_id(self) -> str:
        """Get the schedule ID.

        Returns:
            str: The schedule ID.
        """
        return self._schedule_id

    @property
    def info(self) -> ScheduleInfo:
        """Get the schedule information.

        Returns:
            dict: The schedule information.
        """
        schedule = self._get()
        return ScheduleInfo(
            project_id=schedule.project_id.uuid,
            schedule_id=schedule.schedule_id.uuid,
            test_run_config=schedule.test_run_config,
            frequency_cron_expr=schedule.frequency_cron_expr,
        )

    def _get(self) -> ScheduleSchema:
        """Get the schedule information.

        Returns:
            Schedule: The schedule information.
        """
        api = ScheduleServiceApi(self._api_client)
        with RESTErrorHandler():
            response: RimeGetScheduleResponse = api.get_schedule(
                schedule_id_uuid=self._schedule_id,
            )

            return response.schedule

    def update(
        self,
        frequency_cron_expr: str,
    ) -> ScheduleSchema:
        """Update the schedule.

        Args:
            frequency_cron_expr: The frequency cron expression.

        Returns:
            str: The updated schedule id.
        """
        if not self._schedule_id:
            raise ValueError(
                "No schedule ID has been attached to the object.  Please add a schedule ID to the object or create a new schedule."
            )
        api = ScheduleServiceApi(self._api_client)
        with RESTErrorHandler():
            body = SchedulesScheduleScheduleIdUuidBody(
                frequency_cron_expr=frequency_cron_expr,
            )

            response: RimeUpdateScheduleResponse = api.update_schedule(
                body=body,
                schedule_schedule_id_uuid=self._schedule_id,
                mask="frequency_cron_expr",
            )

            return response.schedule

    def delete(self) -> None:
        """Delete the schedule."""
        if not self._schedule_id:
            raise ValueError(
                "No schedule ID has been attached to the object.  Please add a schedule ID to the object or create a new schedule."
            )
        api = ScheduleServiceApi(self._api_client)
        with RESTErrorHandler():
            api.delete_schedule(schedule_id_uuid=self._schedule_id)
            self._schedule_id = ""
