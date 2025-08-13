#!/usr/bin/env python3

"""
This module contains general functions and tasks related to Pure Storage.

The functions are ordered as followed:
- Helper Functions
- Task Helper Functions
- Single Nornir tasks
- Nornir Tasks in regular Function
"""

from typing import Any, Union
import pypureclient
from nornir.core.task import Task, Result


#### Helper Functions #######################################################################################


#### Task Helper Functions ##################################################################################


def _purestorage_get_connection(task: Task) -> Union[Any, Result]:
    """
    Manually create the Fortinet connection inside a Nornir task.
    Args:
        task (Task): The Nornir task object.
    Returns:
        Result: The connection object if successful, otherwise a failed Nornir result.
    """
    try:
        # Connect to the Pure Storage FlashArray
        api_token = task.host["pure_storage_api_token"][f"env_token_{task.host.name}"]
        conn = pypureclient.flasharray.Client(task.host.hostname, api_token=api_token, verify_ssl=False)
        # Return the connection object
        return conn

    except Exception as error:
        # Return the Nornir result as failed
        result = (
            f"'{task.name}' -> APIResponse <Success: False>\n"
            f"-> Failed to connect to '{task.host.name}'\n\n"
            f"Error:\n{error}"
        )
        return Result(host=task.host, result=result, failed=True)


#### Nornir Tasks ###########################################################################################


#### Nornir Tasks in regular Function #######################################################################
