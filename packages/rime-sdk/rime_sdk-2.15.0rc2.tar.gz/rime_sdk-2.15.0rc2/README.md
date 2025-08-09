# Overview

The RIME SDK provides a programmatic interface to a Robust Intelligence instance, allowing you to create projects,
start stress tests, query the backend for test run results, and more from within your Python code.

To begin, import the Client object from the package like so:
```Python
from rime_sdk import Client
```

The `Client` is the main entry point to SDK functions. To initialize the Client, provide the URL of your
Robust Intelligence instance and an API key generated from a workspace on that instance.

```Python
rime_client = Client("my_vpc.rime.com", "api-key")
```

Once initialized, you can use this Client to interact with your Robust Intelligence instance.

* Please refer to the full [SDK documentation](https://docs.rime.dev/en/latest/reference/python-sdk.html) for further instructions.
* Example notebooks of using the SDK to run tests using Robust Intelligence are available [here](https://docs.rime.dev/en/latest/documentation_home/notebooks.html).
