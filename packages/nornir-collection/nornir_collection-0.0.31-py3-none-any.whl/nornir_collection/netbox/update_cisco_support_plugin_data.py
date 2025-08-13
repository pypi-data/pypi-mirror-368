#!/usr/bin/env python3
"""
This module updates Cisco support plugin data in NetBox using Nornir.
The Main function is intended to import and execute by other scripts.
"""

import sys
from nornir.core.filter import F
from nornir.core import Nornir
from nornir.core.task import Task, Result
from nornir_collection.nornir_plugins.inventory.utils import init_nornir
from nornir_collection.netbox.utils import patch_nb_resources
from nornir_collection.cisco.configuration_management.cli.show_tasks import _get_software_version
from nornir_collection.utils import (
    print_task_title,
    task_name,
    task_info,
    exit_error,
    print_result,
    load_yaml_file,
)


__author__ = "Willi Kubny"
__maintainer__ = "Willi Kubny"
__version__ = "1.0"
__license__ = "MIT"
__email__ = "willi.kubny@dreyfusbank.ch"
__status__ = "Production"


def update_cisco_support_contract_supplier(task: Task, data: dict) -> Result:
    """
    Update the contract supplier information for a Cisco device in NetBox using the Cisco Support Plugin API.

    Args:
        task (Task): The Nornir task object.
        data (dict): A dictionary containing the contract supplier information for the device.

    Returns:
        Result: A Nornir Result object containing the result of the task.
    """
    # Create empty lists to fill with the payload and the serials of all devices
    payload = []
    serials = []

    # Get the NetBox device serial number and database id for the device depending if its a virtual chassis
    if "master" in task.host["cisco_support"]:
        nb_serial = task.host["cisco_support"]["master"]["serial"]
        nb_id = task.host["cisco_support"]["master"]["id"]
    else:
        nb_serial = task.host["cisco_support"]["serial"]
        nb_id = task.host["cisco_support"]["id"]
    # Add the serial to the serials list
    serials.append(nb_serial)
    # Check if the master is covered by a 3rd party support contract
    if nb_serial not in data.keys():
        payload.append(
            {
                "id": nb_id,
                "contract_supplier": None,
                "partner_status": None,
                "partner_service_level": None,
                "partner_customer_number": None,
                "partner_coverage_end_date": None,
            }
        )
    else:
        payload.append(
            {
                "id": nb_id,
                "contract_supplier": data[str(nb_serial)]["contract_supplier"],
                "partner_status": data[str(nb_serial)]["partner_status"],
                "partner_service_level": data[str(nb_serial)]["partner_service_level"],
                "partner_customer_number": data[str(nb_serial)]["partner_customer_number"],
                "partner_coverage_end_date": data[str(nb_serial)]["partner_coverage_end_date"],
            }
        )

    # Check if the members are covered by a 3rd party support contract
    if "members" in task.host["cisco_support"]:
        for member in task.host["cisco_support"]["members"]:
            # Get the NetBox device serial number and database id for the virtual chassis member
            nb_serial = member["serial"]
            nb_id = member["id"]
            # Add the serial to the serials list
            serials.append(nb_serial)
            if nb_serial not in data.keys():
                payload.append(
                    {
                        "id": nb_id,
                        "contract_supplier": None,
                        "partner_status": None,
                        "partner_service_level": None,
                        "partner_customer_number": None,
                        "partner_coverage_end_date": None,
                    }
                )
            else:
                payload.append(
                    {
                        "id": nb_id,
                        "contract_supplier": data[str(nb_serial)]["contract_supplier"],
                        "partner_status": data[str(nb_serial)]["partner_status"],
                        "partner_service_level": data[str(nb_serial)]["partner_service_level"],
                        "partner_customer_number": data[str(nb_serial)]["partner_customer_number"],
                        "partner_coverage_end_date": data[str(nb_serial)]["partner_coverage_end_date"],
                    }
                )

    # Get the NetBox url from the inventory options
    nb_url = task.nornir.config.inventory.options["nb_url"]
    # POST request to update the Cisco Support Plugin desired release
    response = patch_nb_resources(
        url=f"{nb_url}/api/plugins/device-support/cisco-device/",
        payload=payload,
    )

    # Verify the response code and set the result
    if response.status_code == 200:
        result = "'Update contract supplier' -> NetBoxResponse: <Success: True>\n" + f"-> Serials: {serials}"
        return Result(host=task.host, result=result, changed=False, failed=False)

    result = (
        "'Update contract supplier' -> NetBoxResponse: <Success: True>\n"
        + f"-> Response Status Code: {response.status_code}\n"
        + f"-> Response Text: {response.text}\n"
        + f"-> Payload: {payload}"
    )
    return Result(host=task.host, result=result, changed=False, failed=True)


def update_cisco_support_desired_and_current_release(task: Task) -> Result:
    """
    Update the current and desired release of a Cisco device in NetBox using the Cisco Support Plugin.

    Args:
        task (Task): A Nornir task object.

    Returns:
        Result: A Nornir result object with the following attributes:
            - result (str): A string describing the result of the task.
            - changed (bool): Whether or not the task made any changes.
            - failed (bool): Whether or not the task failed.
    """
    # Skip hosts which have no software -> 'PID without Cisco software' (managed over a controller)
    if "recommended_release" in task.host["cisco_support"]:
        if "PID without Cisco software" in task.host["cisco_support"]["recommended_release"]:
            result = (
                "'Update device current and desired release' -> NetBoxResponse: <Success: True>\n"
                + "-> Device without Cisco software (managed over a controller)"
            )
            return Result(host=task.host, result=result, changed=False, failed=False)

    # Use the helper function _get_software_version to get the current software release
    current_rel, verbose_result, failed = _get_software_version(task=task)
    # If failed, the the verbose result contains the full Nornir result string (result + verbose_result)
    if failed:
        # Return the Nornir result as failed
        return Result(host=task.host, result=verbose_result, failed=True)

    try:
        # Get the desired release from the host config context
        desired_rel = task.host["software"]["version"]

        # Create a list of dicts. Multiple dicts if its a virtual chassis
        payload = []
        # Add the device depending if its a virtual chassis in NetBox or not
        nb_id = (
            task.host["cisco_support"]["master"]["id"]
            if "master" in task.host["cisco_support"]
            else task.host["cisco_support"]["id"]
        )
        payload.append({"id": nb_id, "current_release": current_rel, "desired_release": desired_rel})

        # Add all members to the payload if available
        if "members" in task.host["cisco_support"]:
            for member in task.host["cisco_support"]["members"]:
                payload.append(
                    {"id": member["id"], "current_release": current_rel, "desired_release": desired_rel}
                )

    except KeyError as error:
        result = (
            f"'{task.name}' -> NornirResponse <Success: False>\n"
            + f"-> Nornir inventory key {error} not found"
        )
        # Return the Nornir result
        return Result(host=task.host, result=result, changed=False, failed=True)

    # Get the NetBox url from the inventory options
    nb_url = task.nornir.config.inventory.options["nb_url"]
    # POST request to update the Cisco Support Plugin desired release
    response = patch_nb_resources(
        url=f"{nb_url}/api/plugins/device-support/cisco-device/",
        payload=payload,
    )

    # Verify the response code and set the result
    if response.status_code == 200:
        result = (
            "'Update device current and desired release' -> NetBoxResponse: <Success: True>\n"
            + f"-> Current release: {current_rel}\n"
            + f"-> Desired release: {desired_rel}"
        )
        return Result(host=task.host, result=result, changed=False, failed=False)

    result = (
        "'Update device current and desired release' -> NetBoxResponse: <Success: False>\n"
        + f"-> Response Status Code: {response.status_code}\n"
        + f"-> Response Text: {response.text}\n"
        + f"-> Payload: {payload}"
    )
    return Result(host=task.host, result=result, changed=False, failed=True)


def update_cisco_support_plugin_data(nr: Nornir, partner_inv: str = None) -> bool:
    """
    Update NetBox Cisco Support Plugin Data which can't be retrieved from the Cisco Support API.

    Args:
        nr (Nornir): The Nornir object.
        partner_inv (str, optional): Path to the partner inventory file. Defaults to None.

    Returns:
        bool: True if any of the tasks failed, False otherwise.
    """

    # Track if one of the tasks has failed
    failed = False

    print_task_title(title="Update NetBox Cisco Support Plugin Data")

    # Filter Nornir inventory by device manufacturer, device status and device role
    nr_cisco = nr.filter(
        F(device_type__manufacturer__slug__contains="cisco")
        & F(status__value="active")
        & ~F(role__slug__any=["ap", "access-point", "srv", "server"])
    )
    task_text = "Filter nornir inventory"
    print(task_name(text=task_text))
    print(task_info(text=task_text, changed=False))
    print(
        f"'{task_text}' -> NornirResult <Success: True>\n"
        + "-> Filter condition: Device manufacturer slug contains 'cisco'\n"
        + "                     & Device status value is 'active'\n"
        + "                     & Device role is not 'ap', 'access-point', 'srv' or 'server'"
    )

    # Run the custom Nornir task update_cisco_support_desired_and_current_release
    task_text = "NETBOX update device current and desired release"
    result = nr_cisco.run(
        name=task_text,
        task=update_cisco_support_desired_and_current_release,
        on_failed=True,
    )
    # Print the whole result for each host
    print_result(result)
    if result.failed:
        failed = True

    if not partner_inv:
        print(task_name(text=task_text))
        print(task_info(text=task_text, changed=False))
        print(f"'{task_text}' -> NornirResponse: <Success: True>")
        print("-> No list of 3rd party Cisco support partners provided")
        print("-> All devices are expected to be covered by Cisco SNTC")

        return failed

    # Load the partner inventory file as dict and print a error message
    data = load_yaml_file(
        file=partner_inv, text="Load Cisco support partner inventory file", silent=False, verbose=False
    )
    # Check the loaded file and exit the script with exit code 1 if the list is empty
    if not data:
        sys.exit(1)
    # Run the custom Nornir task update_cisco_support_contract_supplier
    task_text = "NETBOX update contract supplier"
    result = nr_cisco.run(
        name=task_text,
        task=update_cisco_support_contract_supplier,
        data=data,
        on_failed=True,
    )
    # Print the whole result for each host
    print_result(result)
    if result.failed:
        failed = True

    return failed


def main(nr_config: str, partner_inv: str = None) -> None:
    """
    Main function is intended to import and execute by other scripts.
    It initialize Nornir, filter the inventory for Cisco devices, and update the NetBox Cisco support
    plugin data.

    * Args:
        * nr_config (str): Path to the Nornir configuration file.
        * partner_inv (str, optional): Path to the partner inventory file. Defaults to None.

    * Steps:
        * Initializes the Nornir inventory object using the provided configuration file.
        * Filters the Nornir inventory by device manufacturer (Cisco) and status (active).
        * Runs the custom Nornir tasks update_cisco_support_desired_and_current_release and
          update_cisco_support_contract_supplier.
        * If no partner inventory file is provided, all devices are expected to be covered by Cisco SNTC.
        * Checks the result of the update tasks and exits the script with an error message if any task

    * Exit:
        * Exits with code 1 if the Nornir configuration file is empty or if any task fails.
    """

    #### Initialize Nornir ##################################################################################

    # Initialize and transform the Nornir inventory object
    # Define data to load from NetBox in addition to the base Nornir inventory plugin
    add_netbox_data = {"load_virtual_chassis_data": True, "load_cisco_support_data": True}
    nr = init_nornir(config_file=nr_config, add_netbox_data=add_netbox_data)

    #### Run Nornir Cisco Support Plugin Update Tasks #######################################################

    # Update NetBox Cisco support plugin data
    result_failed = update_cisco_support_plugin_data(nr=nr, partner_inv=partner_inv)

    # Check the result and exit the script with exit code 1 and a error message
    if result_failed:
        text = "Update NetBox Cisco Support Plugin Data with Nornir"
        print(task_name(text=text))
        exit_error(
            task_text=f"{text} Failed",
            msg="Check the result details for failed Nornir tasks",
        )
