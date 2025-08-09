"""Library defining the interface to a Monitor."""

from typing import Any, Dict, Iterator, Optional

from rime_sdk.detection_event import DetectionEvent
from rime_sdk.internal.rest_error_handler import RESTErrorHandler
from rime_sdk.swagger.swagger_client import ApiClient, DetectionApi
from rime_sdk.swagger.swagger_client.api.monitor_service_api import MonitorServiceApi
from rime_sdk.swagger.swagger_client.models.detection_event_type import (
    DetectionEventType,
)
from rime_sdk.swagger.swagger_client.models.monitor_monitor import MonitorMonitor
from rime_sdk.swagger.swagger_client.models.rime_order import RimeOrder


class Monitor:
    """An interface to a Monitor object.

    Monitors track important model events over time including metric degradations or
    attacks on your model.
    """

    def __init__(
        self,
        api_client: ApiClient,
        monitor_id: str,
        firewall_id: str,
        project_id: str,
    ) -> None:
        """Initialize a new Monitor object.

        Args:
            api_client: ApiClient
                The client used to query for the up-to-date status of the Monitor.
            monitor_id: str
                The unique ID for the Monitor object.
            firewall_id: str
                The unique ID for the parent Firewall of the Monitor.
            project_id: str
                The unique ID for the parent Project of the Monitor.
        """
        self._api_client = api_client
        self._monitor_id = monitor_id
        self._firewall_id = firewall_id
        self._project_id = project_id

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return f"Monitor({self._monitor_id})"

    def update(self, notify: Optional[bool] = None) -> None:
        """Update the settings for the given Monitor in the backend.

        Args:
            notify: Optional[bool]
                A Boolean that specifies whether to enable Monitoring notifications
                for a given monitor. When Monitoring notifications are turned on for
                the same Project and the monitor finds a Detection Event, the system
                sends an alert.
        """
        api = MonitorServiceApi(self._api_client)
        monitor = MonitorMonitor(id=self._monitor_id)
        field_mask_list = []
        if notify is not None:
            field_mask_list.append("notify")
            monitor.notify = notify
        if len(field_mask_list) == 0:
            raise ValueError(
                "Please provide at least one keyword parameter to `update_monitor`."
            )
        body = {"monitor": monitor, "mask": ",".join(field_mask_list)}
        with RESTErrorHandler():
            api.update_monitor(body, self._monitor_id)

    def list_detected_events(self) -> Iterator[DetectionEvent]:
        """List detected Events for the given Monitor.

        For each continuous testing bin upload, RIME compares the
        metric value to the Monitor's thresholds and creates detection events
        when a degradation is detected.
        For a subset of Monitors, we perform Root Cause Analysis to explain
        the detailed cause of the Event.

        Returns:
            Iterator[DetectionEvent]:
                A generator of dictionary representations of Detection Events.
                They are sorted in reverse chronological order by the time at which
                the event occurred.

        Example:
            .. code-block:: python

                # List all default Monitors on the Firewall
                monitors = firewall.list_monitors(monitor_types=["Default"])
                # For each Monitor, list all detected Events.
                all_events = [monitor.list_detected_events() for monitor in monitors]
        """
        api = DetectionApi(self._api_client)
        next_page_token = ""
        has_more = True
        while has_more:
            kwargs: Dict[str, Any] = {}
            if len(next_page_token) > 0:
                kwargs["page_token"] = next_page_token
            else:
                # Return the events in reverse chronological order.
                # Also, only return CT events for the given monitor.
                kwargs["first_page_req_sort_sort_order"] = RimeOrder.DESCENDING
                kwargs["first_page_req_sort_sort_by"] = "event_time_range.end_time"
                kwargs["first_page_req_event_object_id"] = self._monitor_id
                kwargs["first_page_req_event_types"] = [
                    DetectionEventType.METRIC_DEGRADATION,
                    DetectionEventType.SECURITY,
                ]
            with RESTErrorHandler():
                res = api.list_detection_events(
                    project_id_uuid=self._project_id, **kwargs
                )
            for detection_event in res.events:
                yield DetectionEvent(self._api_client, detection_event.to_dict())
            next_page_token = res.next_page_token
            has_more = res.has_more
