#!/usr/bin/env python3
"""
This module contains RESTCONF functions and tasks related to Nornir.

The functions are ordered as followed:
- Single Nornir RESTCONF tasks
- Nornir RESTCONF tasks in regular function
"""

import json
import traceback
import requests
from nornir.core import Nornir
from nornir.core.task import Task, Result
from nornir_collection.cisco.configuration_management.restconf.cisco_rpc import (
    rc_software_install_one_shot_task,
    rc_install_remove_inactive_task,
)
from nornir_collection.cisco.configuration_management.cli.show_tasks import (
    cli_verify_current_software_version_task,
    cli_install_one_shot_task,
    cli_install_remove_inactive_task,
)
from nornir_collection.utils import (
    print_result,
    exit_error,
    nr_filter_inventory_from_host_list,
)


#### Helper Functions #######################################################################################


def rc_cisco_get(url: str, auth: tuple, verify: bool = False, timeout: int = 120) -> dict:
    """
    TBD
    """
    # RESTCONF HTTP header
    headers = {"Accept": "application/yang-data+json", "Content-Type": "application/yang-data+json"}

    # RESTCONF HTTP API call
    response = requests.get(url=url, headers=headers, auth=auth, verify=verify, timeout=timeout)  # nosec

    # Result dict to return as task result
    result = {
        "url": url,
        "response": response,
        "method": response.request,
        "status_code": response.status_code,
        "elapsed": response.elapsed.total_seconds(),
        "text": response.text,
        "json": response.json(),
    }

    # Return the result dictionary
    return result


#### Single Nornir RESTCONF Tasks ###########################################################################


def rc_cisco_get_task(task: Task, yang_data_query: str) -> Result:
    """
    This custom Nornir task executes a RESTCONF GET request to a yang data query and returns a dictionary with
    the whole RESTCONF response as well as some custom formated data for further processing.
    """
    # RESTCONF HTTP URL
    restconf_path = f"restconf/data/{yang_data_query}"
    url = f"https://{task.host.hostname}:443/{restconf_path}"

    # RESTCONF HTTP header
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json",
    }

    # RESTCONF HTTP API call
    rc_response = requests.get(  # nosec
        url=url, headers=headers, auth=(task.host.username, task.host.password), verify=False, timeout=120
    )

    # Result dict to return as task result
    result = {
        "url": url,
        "response": rc_response,
        "method": rc_response.request,
        "status_code": rc_response.status_code,
        "elapsed": rc_response.elapsed.total_seconds(),
        "json": rc_response.json(),
    }

    return Result(host=task.host, result=result)


def rc_verify_current_software_version_task(task: Task, verbose=False) -> Result:
    """
    TBD
    """
    # Get the desired version from the Nornir inventory
    desired_version = task.host["software"]["version"]

    # RESTCONF HTTP URL
    rc_path = "restconf/data/Cisco-IOS-XE-install-oper:install-oper-data/install-location-information"
    url = f"https://{task.host.hostname}:443/{rc_path}"
    # RESTCONF HTTP header
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json",
    }

    try:
        # RESTCONF HTTP API call
        response = requests.get(  # nosec
            url=url, headers=headers, auth=(task.host.username, task.host.password), verify=False, timeout=120
        )
        # Get the current version from the task result
        current_version = response.json()["Cisco-IOS-XE-install-oper:install-location-information"][0][
            "install-version-state-info"
        ][0]["version"]
    except:  # noqa: E722
        # Define the result as iosxe_c9200 is not implemented yet
        custom_result = f"'{task.name}' -> NornirResponse: <Success: False>\n\n{traceback.format_exc()}"
        # Return the custom Nornir result as success
        return Result(host=task.host, custom_result=custom_result, failed=True, use_fallback=True)

    # Slice the variable to have only the fist 8 characters of the version number which should match to
    # the Cisco version naming convention of xx.xx.xx
    current_version = current_version[:8]
    # Replace all 0 in the xe_version to normalizing iosxe and non-iosxe version format
    # -> Make 17.03.05 to 17.3.5
    current_version = current_version.replace("0", "")
    # Write the current version into the Nornir inventory
    task.host["software"]["current_version"] = current_version
    # Prepare needed variables for further processing
    elapsed = response.elapsed.total_seconds()

    # Define the verbose result
    verbose_result = (
        f"URL: {url}\n"
        f"Method: {response.request}\n"
        f"Response: {response}\n"
        f"Current version from JSON payload: {json.dumps(current_version, sort_keys=True, indent=4)}"
    )

    # If the RESTCONF call was successful
    if response.status_code == 200:
        # If the desired version and the current version are the same
        if desired_version in current_version:
            # Define the summary result
            result_summary = (
                f"'{task.name}' -> RestconfResponse {response} in {elapsed}s\n"
                f"-> Desired version {desired_version} match installed version {current_version}"
            )
            # Define the custom_result variable for print_result
            custom_result = result_summary + "\n\n" + verbose_result if verbose else result_summary

            # Return the custom Nornir result as success
            return Result(host=task.host, custom_result=custom_result)

        # Else the desired version and the current version are not the same
        # Define the summary result
        result_summary = (
            f"'{task.name}' -> RestconfResponse {response} in {elapsed}s\n"
            f"-> Desired version {desired_version} don't match installed version {current_version}"
        )
        # Define the custom_result variable for print_result
        custom_result = result_summary + "\n\n" + verbose_result if verbose else result_summary

        # Return the custom Nornir result as failed
        return Result(host=task.host, custom_result=custom_result, failed=True, need_upgrade=True)

    # Define the custom_result variable for print_result
    custom_result = f"'{task.name}' -> RestconfResponse {response} in {elapsed}s\n\n{verbose_result}"

    # If the RESTCONF call was not successful -> The task failed and set the use_fallback to True
    return Result(host=task.host, custom_result=custom_result, failed=True, use_fallback=True)


#### Nornir RESTCONF tasks in regular Function ##############################################################


def rc_verify_current_software_version_fallback_cli(nr: Nornir, verbose=False) -> list:
    """
    TBD
    """

    # Get software version with RESTCONF
    rc_task_result = nr.run(
        task=rc_verify_current_software_version_task,
        name="RESTCONF verify current software version",
        verbose=verbose,
        on_failed=True,
    )

    # Print the Nornir rc_verify_current_software_version_task task result
    print_result(rc_task_result, attrs="custom_result")

    # Create a list with all host that failed the RESTCONF task and need to use the CLI fallback task
    rc_fallback_hosts = [host for host in rc_task_result if hasattr(rc_task_result[host], "use_fallback")]

    # If the rc_fallback_hosts list is empty, the CLI fallback is not needed and the failed_hosts list can
    # be returned. The failed host list contains now only host with not matching software version
    if not rc_fallback_hosts:
        failed_hosts = list(rc_task_result.failed_hosts)
        return failed_hosts

    # Re-filter the Nornir inventory on the failed_hosts only
    nr_obj_fallback = nr_filter_inventory_from_host_list(
        nr=nr,
        filter_reason="CLI fallback for hosts that failed the RESTCONF task:",
        host_list=rc_fallback_hosts,
    )

    # Get software version with CLI
    cli_task_result = nr_obj_fallback.run(
        task=cli_verify_current_software_version_task,
        name="CLI verify current software version",
        verbose=verbose,
        on_failed=True,
    )

    # Print the Nornir cli_verify_current_software_version_task task result
    print_result(cli_task_result)

    # If the overall task result failed -> Print results and exit the script
    for host in cli_task_result:
        if hasattr(cli_task_result[host], "overall_task_failed"):
            exit_error(task_text="RESTCONF and CLI verify current software version")

    # Create a list with all host which the RESTCONF task was successful but they need a software upgrade
    rc_upgrade_hosts = [host for host in rc_task_result if hasattr(rc_task_result[host], "need_upgrade")]
    # Create a list with all host which the CLI task was successful but they need a software upgrade
    cli_upgrade_hosts = [host for host in cli_task_result if hasattr(cli_task_result[host], "need_upgrade")]

    # List to fill with all hosts not matching the desired software version
    failed_hosts = rc_upgrade_hosts + cli_upgrade_hosts

    return failed_hosts


def rc_software_install_one_shot_fallback_cli(nr: Nornir, issu: bool = False, verbose: bool = False) -> bool:
    """
    TBD
    """

    # Run the custom Nornir task rc_software_install_one_shot_task
    rc_task_result = nr.run(
        task=rc_software_install_one_shot_task,
        name="RESTCONF one-shot install",
        issu=issu,
        verbose=verbose,
        on_failed=True,
    )

    # Print the Nornir rc_software_install_one_shot_task task result
    print_result(rc_task_result)

    # If the failed_hosts list is empty, the CLI fallback is not needed and True can be returned.
    if not list(rc_task_result.failed_hosts):
        return True

    # Re-filter the Nornir inventory on the failed_hosts of rc_task_result only
    nr_obj_fallback = nr_filter_inventory_from_host_list(
        nr=nr,
        filter_reason="CLI fallback for hosts that failed the RESTCONF task:",
        host_list=list(rc_task_result.failed_hosts),
    )

    # Run the custom Nornir task cli_install_one_shot_task
    cli_task_result = nr_obj_fallback.run(
        task=cli_install_one_shot_task,
        name="CLI one-shot install",
        issu=issu,
        verbose=verbose,
        on_failed=True,
    )

    # Print the Nornir cli_install_one_shot_task task result
    print_result(cli_task_result)

    # Return False if the task failed or True if the task was successful
    return not bool(cli_task_result.failed)


def rc_install_remove_inactive_fallback_cli(nr: Nornir, verbose: bool = False) -> bool:
    """
    TBD
    """

    # Run the custom Nornir task rc_install_remove_inactive_task
    rc_task_result = nr.run(
        task=rc_install_remove_inactive_task,
        name="RESTCONF install remove inactive",
        verbose=verbose,
        on_failed=True,
    )
    # Print the Nornir rc_install_remove_inactive_task task result
    print_result(rc_task_result)

    # If the failed_hosts list is empty, the CLI fallback is not needed and True can be returned.
    if not list(rc_task_result.failed_hosts):
        return True

    # Re-filter the Nornir inventory on the failed_hosts of rc_task_result only
    nr_obj_fallback = nr_filter_inventory_from_host_list(
        nr=nr,
        filter_reason="CLI fallback for hosts that failed the RESTCONF task:",
        host_list=list(rc_task_result.failed_hosts),
    )

    # Run the custom Nornir task cli_install_remove_inactive_task
    cli_task_result = nr_obj_fallback.run(
        task=cli_install_remove_inactive_task,
        name="CLI install remove inactive",
        verbose=verbose,
        on_failed=True,
    )
    # Print the Nornir cli_install_remove_inactive_task task result
    print_result(cli_task_result)

    # Return False if the task failed or True if the task was successful
    return not bool(cli_task_result.failed)
