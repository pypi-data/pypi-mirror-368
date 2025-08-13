#!/usr/bin/env python3
"""
This module contains functions related to NetBox custom scripts.

The functions are ordered as followed:
- Regular functions
"""

import os
import time
import json
import requests
from nornir_collection.utils import task_name, task_error, task_info, exit_error


#### Regular functions ######################################################################################


def run_nb_custom_script(name: str, url: str, payload: dict = {}, verbose: bool = False) -> bool:
    """
    Runs a custom script in NetBox.
    Args:
        name (str): The name of the custom script to run.
        url (str): The URL of the custom script to run.
        payload (dict, optional): The payload to send with the request. Defaults to {}.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.
    Returns:
        bool: True if the custom script failed, False otherwise.
    """
    task_text = f"Run NetBox Custom Script {name}"
    print(task_name(text=task_text))

    # Set the NetBox token, timeout, header
    timeout = (3.05, 27)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Token {os.environ.get('NB_TOKEN')}",
    }

    # Do the http post request to run the NetBox custom script
    response = requests.post(  # nosec
        url=url, headers=headers, data=json.dumps(payload), verify=False, timeout=timeout
    )
    # Verify the response code
    if not response.status_code == 200:
        msg = [
            f"Failed to run NetBox custom script {url}",
            f"Status code: {response.status_code}",
            f"Response Text: {response.text}",
        ]
        # Print the error message and exit the script
        exit_error(task_text=task_text, msg=msg)

    # Print the start of the custom script
    print(task_info(text="Started NetBox Custom Script", changed=False))
    print(f"Started NetBox Custom Script {name}")
    if verbose:
        print(json.dumps(response.json(), indent=4))

    # Create a result dict from the first API response to track the progress of the status
    result = response.json()["result"]
    # Do the http get request to verify the status of the running NetBox custom script
    # Terminate the while loop with a timeout of max 300s (5min)
    timeout_start = time.time()
    while time.time() < timeout_start + 300:
        if result["status"]["value"] not in ("pending", "running"):
            break
        result = requests.get(url=result["url"], headers=headers, verify=False, timeout=timeout)  # nosec
        result = result.json()
        time.sleep(1)

    # Print the end result after the custom script has finished or the timeout exeeded
    if result["status"]["value"] not in ("completed", "failed"):
        print(task_error(text="Failed NetBox Custom Script", changed=False))
        print(f"Failed NetBox Custom Script {name}")
        print(json.dumps(result, indent=4))

        # Return True because the custom script failed
        return True

    # Create a list of the log messages
    result_list = []
    result_list.append(f"Completed NetBox Custom Script {name}\n")
    for item in result["data"]["log"]:
        # Space after the info emoji needed to align the text
        symbol_lookup = {"debug": "🚧", "info": "ℹ️", "success": "✅", "warning": "🚨", "failure": "❌"}
        symbol = symbol_lookup.get(item["status"], "❓")
        result_list.append(f"{symbol} [{item['status'].capitalize()}] - {item['message']}")
    if verbose:
        result_list.append(json.dumps(result, indent=4))

    if "failed" in result["status"]["value"]:
        print(task_error(text="Completed NetBox Custom Script", changed=False))
        print("\n".join(result_list))

        # Return True because the custom script failed
        return True

    print(task_info(text="Completed NetBox Custom Script", changed=False))
    print("\n".join(result_list))

    # Return False because the custom script was successful
    return False
