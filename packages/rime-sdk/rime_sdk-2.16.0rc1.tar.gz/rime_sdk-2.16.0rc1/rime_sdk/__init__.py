"""Python package providing access to Robust Intelligence.

The RIME SDK provides a programmatic interface to a Robust Intelligence
instance, allowing you to create projects, start stress tests, query the
backend for test run results, and more from within your Python code. To
begin, initialize a client, which acts as the main entry point to SDK
functions.
"""

from rime_sdk.client import (
    Client,
    ManagedImagePackageRequirement,
    ManagedImagePipRequirement,
)
from rime_sdk.continuous_test import ContinuousTest
from rime_sdk.data_collector import DataCollector
from rime_sdk.detection_event import DetectionEvent
from rime_sdk.generative_firewall import FirewallClient, FirewallInstance
from rime_sdk.image_builder import ImageBuilder
from rime_sdk.job import ContinuousTestJob, Job
from rime_sdk.monitor import Monitor
from rime_sdk.project import Project
from rime_sdk.registry import Registry
from rime_sdk.swagger.swagger_client.models import RuntimeinfoCustomImage as CustomImage
from rime_sdk.test_batch import TestBatch
from rime_sdk.test_run import ContinuousTestRun, TestRun

__all__ = [
    "Client",
    "ManagedImagePackageRequirement",
    "ManagedImagePipRequirement",
    "Project",
    "Job",
    "ContinuousTestJob",
    "TestRun",
    "ContinuousTestRun",
    "TestBatch",
    "ContinuousTest",
    "ImageBuilder",
    "CustomImage",
    "DataCollector",
    "Registry",
    "DetectionEvent",
    "Monitor",
    "FirewallClient",
    "FirewallInstance",
]
