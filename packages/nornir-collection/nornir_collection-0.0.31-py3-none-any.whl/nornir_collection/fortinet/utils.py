#!/usr/bin/env python3
"""
This module contains general functions and tasks related to Fortinet.

The functions are ordered as followed:
- Helper Functions
- Single Nornir tasks
- Nornir tasks in regular function
"""

import requests
from nornir.core.task import Task


#### Helper Functions #######################################################################################


#### Nornir Tasks ###########################################################################################


def get_fgt_resources(task: Task, url: str, port: int = None) -> requests.Response:
    """
    TBD
    """
    # Get the API token and create the url
    api_token = task.host["fortigate_api_token"][f"env_token_{task.host.name}"]
    port = port if port else 4443
    url = f"https://{task.host.hostname}:{port}/{url}?access_token={api_token}"

    # Do the http request and return the result
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    return requests.get(url=url, headers=headers, verify=False, timeout=(3.05, 27))  # nosec


#### Nornir Tasks ###########################################################################################
