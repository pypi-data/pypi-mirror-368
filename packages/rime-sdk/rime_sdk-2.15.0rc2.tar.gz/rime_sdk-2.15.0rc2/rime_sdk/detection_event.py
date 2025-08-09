"""Library defining the interface to a Detection Event."""

from rime_sdk.swagger.swagger_client.api_client import ApiClient


class DetectionEvent:
    """An interface to a Detection Event.

    RIME surfaces Detection Events to indicate problems with a
    model that is in production or during model validation.
    """

    def __init__(self, api_client: ApiClient, event_dict: dict) -> None:
        """Create a new Detection Event object.

        Args:
            api_client: ApiClient
                The client to query for the status of the Event object.
            event_dict: dict
                Dictionary with the contents of the Event object.
        """
        self._api_client = api_client
        self._event_dict = event_dict

    def to_dict(self) -> dict:
        """Return a dictionary representation of the Event object."""
        return self._event_dict
