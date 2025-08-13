#!/usr/bin/env python3
"""
This module contains Cisco specific RESTCONF operation RPC tasks and functions for Nornir. Other custom
RESTCONF tasks for the /data url are not part of this helper file. Please take a look to nr_restconf.

The functions are ordered as followed:
- Helper Functions
- Single Nornir RESTCONF RPC Tasks
- Nornir RESTCONF RPC Tasks in regular Function
- Nornir RESTCONF RPC Tasks with CLI Fallback in regular Function
"""

import json
import time
from typing import Union
import requests
from nornir.core import Nornir
from nornir.core.task import Task, Result
from nornir_collection.utils import print_result


#### Helper Functions ########################################################################################


def rc_cisco_operation_rpc(task_obj: Task, rpc: str, payload: dict = {}) -> requests.Response:
    """
    TBD
    """

    # RESTCONF HTTP URL
    host = task_obj.host.hostname
    url = f"https://{host}:443/restconf/operations/{rpc}"

    # RESTCONF HTTP header
    headers = {"Accept": "application/yang-data+json", "Content-Type": "application/yang-data+json"}

    # RESTCONF HTTP API call
    response = requests.post(
        url=url,
        headers=headers,
        data=json.dumps(payload),
        auth=(task_obj.host.username, task_obj.host.password),
        verify=False,  # nosec
        timeout=120,
    )

    return response


#### Single Nornir RESTCONF RPC Tasks ########################################################################


def rc_cisco_rpc_is_syncing_task(task: Task, verbose: bool = False) -> Result:
    """
    This Nornir task executes the Cisco specific operations RESTCONF RPC cisco-ia:is-syncing to check if the
    configuration datastore is ready. If a sync is active the task backoff and try again until the datastore
    is ready. The Nornir Result object is returned.
    """
    # Backoff sleep and attempt values
    max_retry = 180  # How many times the range() loop will be done
    sleep = 1  # Seconds to sleep between each range() loop attempt
    waited = 0  # How many seconds hat to be waited until the datastore is ready

    for _ in range(max_retry):
        # RESTCONF HTTP API call
        response = rc_cisco_operation_rpc(task_obj=task, rpc="cisco-ia:is-syncing")

        # Set the verbose result string to add to the result summary
        result_verbose = (
            f"\n\nPayload: {json.dumps({}, indent=4)}\n"
            + f"\nURL: {response.url}\n"
            + f"Method: {response.request}\n"
            + f"Response: {response}\n"
            + f"Text: {response.text}"
        )

        if response.status_code == 200 and "No sync in progress" in response.text:
            # No datastore sync -> Return the Nornir task result as successful
            result = (
                f"'{task.name}' -> RestconfResponse: <Success: True>\n"
                + f"-> Datastore is ready after waiting {waited}s"
            )
            result = result + f"{result_verbose}" if verbose else result

            # Return the Nornir task result
            return Result(host=task.host, result=result, failed=False)

        # Continue with next range() loop attempt
        time.sleep(sleep)
        waited = waited + sleep

    # If the for loop is finish without success
    result = f"'{task.name}' -> RestconfResponse: <Success: False>"
    # Set the message based on the response status code
    result += (
        f"\n-> Datastore is not ready after max waiting timeout of {waited}s"
        if response.status_code == 200
        else f"\n-> RESTCONF RPC API call failed with status code {response.status_code}"
    )
    result = result + result_verbose if verbose else result

    # Return the Nornir task result as failed
    return Result(host=task.host, result=result, failed=True)


def rc_cisco_rpc_save_config_task(task: Task, verbose: bool = False) -> Result:
    """
    TBD
    """
    # RESTCONF HTTP API call
    response = rc_cisco_operation_rpc(task_obj=task, rpc="cisco-ia:save-config")

    # Set the verbose result string to add to the result summary
    result_verbose = (
        f"\n\nPayload: {json.dumps({}, indent=4)}\n"
        + f"\nURL: {response.url}\n"
        + f"Method: {response.request}\n"
        + f"Response: {response}\n"
        + f"Text: {response.text}"
    )

    if response.status_code == 200:
        result = f"'{task.name}' -> RestconfResponse: <Success: True>"
        # Set the result print level
        result = result + result_verbose if verbose else result

        # Return the Nornir task result as successful
        return Result(host=task.host, result=result)

    result = f"'{task.name}' -> RestconfResponse: <Success: False>" + result_verbose
    # Return the Nornir task result as failed
    return Result(host=task.host, result=result, failed=True)


def rc_cisco_rpc_copy_file_task(task: Task, source: str, destination: str, verbose: bool = False) -> Result:
    """
    TBD
    """
    # Payload
    payload = {
        "Cisco-IOS-XE-rpc:input": {
            "source-drop-node-name": source,
            "destination-drop-node-name": destination,
        }
    }
    # RESTCONF HTTP API call
    response = rc_cisco_operation_rpc(task_obj=task, rpc="Cisco-IOS-XE-rpc:copy", payload=payload)

    # Set the verbose result string to add to the result summary
    result_verbose = (
        f"\n\nPayload: {json.dumps(payload, indent=4)}\n"
        + f"\nURL: {response.url}\n"
        + f"Method: {response.request}\n"
        + f"Response: {response}\n"
        + f"Text: {response.text}"
    )

    if response.status_code == 200:
        result = (
            f"'{task.name}' -> RestconfResponse: <Success: True>\n"
            + f"-> Source: '{source}'\n"
            + f"-> Destination: '{destination}'"
        )
        # Set the result print level
        result = result + result_verbose if verbose else result

        # Return the Nornir task result as successful
        return Result(host=task.host, result=result, failed=False)

    result = (
        f"'{task.name}' -> RestconfResponse: <Success: False>\n"
        + f"-> Source: '{source}'\n"
        + f"-> Destination: '{destination}'"
        + result_verbose
    )
    # Return the Nornir task result as failed
    return Result(host=task.host, result=result, failed=True)


def rc_cisco_rpc_rollback_config_task(
    task: Task, target_url: str, revert_timer: int = None, verbose: bool = False
) -> Result:
    """
    TBD
    """
    # Base Payload
    payload = {
        "cisco-ia:input": {
            "target-url": target_url,
            "verbose": True,
        }
    }
    # Optional add the revert-timer to the payload
    if revert_timer:
        payload["cisco-ia:input"]["revert-timer"] = revert_timer

    # RESTCONF HTTP API call
    response = rc_cisco_operation_rpc(task_obj=task, rpc="cisco-ia:rollback", payload=payload)

    # Set the verbose result string to add to the result summary
    result_verbose = (
        f"\n\nPayload: {json.dumps(payload, indent=4)}\n"
        + f"\nURL: {response.url}\n"
        + f"Method: {response.request}\n"
        + f"Response: {response}\n"
        + f"Text: {response.text}"
    )

    # If the rollback was successful
    if response.status_code == 200:
        result = f"'{task.name}' -> RestconfResponse: <Success: True>\n" + f"-> Target-URL: '{target_url}'"
        if revert_timer:
            result = result + f"\n-> Revert-Timer: '{revert_timer}min'"
        # Set the result print level
        result = result + result_verbose if verbose else result

        # Return the Nornir task result as successful
        return Result(host=task.host, result=result, failed=False)

    # Failed because the rollback file does not exist
    if (response.status_code == 400) and (("cisco-ia:rollback" and "Could not open file") in response.text):
        result = f"'{task.name}' -> RestconfResponse: <Success: False>\n" + f"-> Target-URL: '{target_url}'"
        if revert_timer:
            result = result + f"\n-> Revert-Timer: '{revert_timer}'"
        result = result + result_verbose
        # Return the Nornir task result as successful
        return Result(host=task.host, result=result, failed=True)

    # Success but with some failed rollback commands -> Happen when commands change between software releases
    if (response.status_code == 400) and (("cisco-ia:rollback" and "inconsistent value") in response.text):
        result = f"'{task.name}' -> RestconfResponse: <Success: True>\n" + f"-> Target-URL: '{target_url}'"
        if revert_timer:
            result = result + f"\n-> Revert-Timer: '{revert_timer}'"
        # Set the result print level
        result = result + result_verbose if verbose else result
        # Return the Nornir task result as successful
        return Result(host=task.host, result=result, failed=False)

    # Return the Nornir task result as failed
    result = f"'{task.name}' -> RestconfResponse: <Success: False>\n" + f"-> Target-URL: '{target_url}'"
    if revert_timer:
        result = result + f"\n-> Revert-Timer: '{revert_timer}'"
    result = result + result_verbose
    return Result(host=task.host, result=result, failed=True)


def rc_software_install_one_shot_task(task: Task, issu: bool = False, verbose: bool = False) -> Result:
    """
    This custom Nornir task loads the software destination file which have to be installed from the Nornir
    inventory executes the Cisco specific operations RESTCONF RPC Cisco-IOS-XE-install-rpc:install to install
    a software file in a one-shot approach which will install, commit and reload the switch. The Nornir
    result object will be returned.
    """

    # Get the host destination file from the Nornir inventory
    dest_file = task.host["software"]["dest_file"]

    # Set the base payload for the RESTCONF API call
    payload = {
        "Cisco-IOS-XE-install-rpc:input": {
            "uuid": f"Install {dest_file}",
            "one-shot": True,
            "path": f"flash:{dest_file}",
        }
    }
    # Optional add issu to the payload
    if issu:
        payload["Cisco-IOS-XE-install-rpc:input"]["issu"] = True

    # RESTCONF HTTP API call
    response = rc_cisco_operation_rpc(
        task_obj=task,
        rpc="Cisco-IOS-XE-install-rpc:install",
        payload=payload,
    )

    # Set the verbose result string to add to the result summary
    result_verbose = (
        f"\n\nPayload: {json.dumps(payload, indent=4)}\n"
        + f"\nURL: {response.url}\n"
        + f"Method: {response.request}\n"
        + f"Response: {response}\n"
        + f"Text: {response.text}"
    )

    if response.status_code == 204:
        result = f"'{task.name}' -> RestconfResponse: <Success: True>"
        # Set the result print level
        result = result + result_verbose if verbose else result

        # Return the Nornir task result as successful
        return Result(host=task.host, result=result)

    result = f"'{task.name}' -> RestconfResponse: <Success: False>" + result_verbose
    # Return the Nornir task result as failed
    return Result(host=task.host, result=result, failed=True)


def rc_install_remove_inactive_task(task: Task, verbose: bool = False) -> Result:
    """
    This Nornir task executes the Cisco specific operations RESTCONF RPC Cisco-IOS-XE-install-rpc:remove to
    remove all not needed software packages and files on the filesystem.
    """
    # Payload
    payload = {
        "Cisco-IOS-XE-install-rpc:input": {
            "uuid": "Install Remove Inactive",
            "inactive": True,
        }
    }

    # RESTCONF HTTP API call
    response = rc_cisco_operation_rpc(
        task_obj=task,
        rpc="Cisco-IOS-XE-install-rpc:remove",
        payload=payload,
    )

    # Set the verbose result string to add to the result summary
    result_verbose = (
        f"\n\nPayload: {json.dumps(payload, indent=4)}\n"
        + f"\nURL: {response.url}\n"
        + f"Method: {response.request}\n"
        + f"Response: {response}\n"
        + f"Text: {response.text}"
    )

    if response.status_code == 204:
        result = f"'{task.name}' -> RestconfResponse: <Success: True>"
        # Set the result print level
        result = result + result_verbose if verbose else result

        # Return the Nornir task result as successful
        return Result(host=task.host, result=result)

    result = f"'{task.name}' -> RestconfResponse: <Success: False>" + result_verbose
    # Return the Nornir task result as failed
    return Result(host=task.host, result=result, failed=True)


#### Nornir RESTCONF RPC Tasks in regular Function ###########################################################


def rc_cisco_rpc_is_syncing(nr: Nornir, cfg_status: bool = True, verbose: bool = False) -> bool:
    """
    This function runs the custom Nornir task rc_cisco_rpc_is_syncing_task to verify the configuration
    datastore sync state on a Cisco device with RESTCONF. Its a Cisco specific RPC that is sent to the device.
    The result will be printed to std-out in custom Nornir style.
    """

    # Return False if cfg_status argument is False
    if not cfg_status:
        return False

    # Run the Nornir Task rc_cisco_rpc_is_syncing_task
    task_result = nr.run(
        task=rc_cisco_rpc_is_syncing_task,
        name="RESTCONF verify is-syncing",
        verbose=verbose,
        on_failed=True,
    )

    # Print the Nornir task result
    print_result(task_result)

    # Return False if the task failed or True if the task was successful
    return not bool(task_result.failed)


def rc_cisco_rpc_save_config(nr: Nornir, cfg_status: bool = True, verbose: bool = False) -> bool:
    """
    This function runs the custom Nornir task rc_cisco_rpc_save_config_task to save the configuration on a
    Cisco device with RESTCONF. Its a Cisco specific RPC that is sent to the device. The result will be
    printed to std-out in Nornir style and the function return True or False depending wheather the task was
    successful.
    """

    # Return False if cfg_status argument is False
    if not cfg_status:
        return False

    # Run the custom Nornir task rc_cisco_rpc_save_config_task
    task_result = nr.run(
        task=rc_cisco_rpc_save_config_task,
        name="RESTCONF save config",
        verbose=verbose,
        on_failed=True,
    )

    # Print the Nornir task result
    print_result(task_result)

    # Return False if the task failed or True if the task was successful
    return not bool(task_result.failed)


def rc_cisco_rpc_copy_file(
    nr: Nornir, source: str, destination: str, name: Union[str, None] = None, verbose=False
) -> bool:
    """
    This function runs the custom Nornir task rc_cisco_rpc_copy_file_task to copy a file from or to a Cisco
    device with RESTCONF. Its a Cisco specific RPC that is sent to the device. The result will be printed to
    std-out in  Nornir style and the function return True or False depending wheather the task was successful.
    """

    # Set a custom task name if the argument name is not None
    name = name if name else "RESTCONF copy file"

    # Run the custom Nornir task rc_cisco_rpc_copy_file_task
    task_result = nr.run(
        task=rc_cisco_rpc_copy_file_task,
        name=name,
        source=source,
        destination=destination,
        verbose=verbose,
        on_failed=True,
    )

    # Print the Nornir task result
    print_result(task_result)

    # Return False if the task failed or True if the task was successful
    return not bool(task_result.failed)


def rc_cisco_rpc_rollback_config(
    nr: Nornir,
    target_url: str,
    revert_timer: int = None,
    name: Union[str, None] = None,
    verbose: bool = False,
) -> bool:
    """
    This function runs the custom Nornir task rc_cisco_rpc_rollback_config_task to rollback the copy of a
    Cisco device to a config specified by a target-url with RESTCONF. Its a Cisco specific RPC that is sent to
    the device. The result will be printed to std-out in custom Nornir style and the function return True or
    False depending wheather the task was successful.
    """

    # Set a custom task name if the argument name is not None
    name = name if name else "RESTCONF rollback config"

    # Run the custom Nornir task rc_cisco_rpc_rollback_config_task
    task_result = nr.run(
        task=rc_cisco_rpc_rollback_config_task,
        name=name,
        target_url=target_url,
        revert_timer=revert_timer,
        verbose=verbose,
        on_failed=True,
    )

    # Print the Nornir task result
    print_result(task_result)

    # Return False if the task failed or True if the task was successful
    return not bool(task_result.failed)


def rc_software_install_one_shot(nr: Nornir, issu: bool = False, verbose: bool = False) -> bool:
    """
    This function takes the result of the function host_dict as an argument andruns the custom
    Nornir task rc_software_install_one_shot_task to start the one-shot installation process of the desired
    software version. The result will be printed to std-out in custom Nornir style and the script terminates
    with an info message in case of an error.
    """

    # Run the custom Nornir task rc_software_install_one_shot_task
    task_result = nr.run(
        task=rc_software_install_one_shot_task,
        name="RESTCONF one-shot install",
        issu=issu,
        verbose=verbose,
        on_failed=True,
    )

    # Print the Nornir task result
    print_result(task_result)

    # Return False if the task failed or True if the task was successful
    return not bool(task_result.failed)


def rc_install_remove_inactive(nr: Nornir, verbose: bool = False) -> bool:
    """
    This function runs the Nornir task rc_install_remove_inactive_task to to remove all not needed software
    packages and files on the filesystem with RESTCONF. The result will be printed to std-out in custom Nornir
    style and the script terminates with an info message in case of an error.
    """

    # Run the custom Nornir task rc_install_remove_inactive_task
    task_result = nr.run(
        task=rc_install_remove_inactive_task,
        name="RESTCONF install remove inactive",
        verbose=verbose,
        on_failed=True,
    )

    # Print the Nornir task result
    print_result(task_result)

    # Return False if the task failed or True if the task was successful
    return not bool(task_result.failed)


#### Nornir RESTCONF RPC Tasks with CLI Fallback in regular Function #########################################
