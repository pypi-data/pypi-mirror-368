#!/usr/bin/env python3
"""
This module updates the serial numbers of Cisco devices in NetBox using Nornir.
The Main function is intended to import and execute by other scripts.
"""

from nornir.core import Nornir
from nornir.core.filter import F
from nornir.core.task import Task, Result
from nornir_collection.nornir_plugins.inventory.utils import init_nornir
from nornir_collection.cisco.configuration_management.cli.show_tasks import _get_serial_numbers
from nornir_collection.netbox.utils import get_nb_resources, patch_nb_resources
from nornir_collection.netbox.utils import _nb_patch_resources, _nb_create_payload_patch_device_serials
from nornir_collection.utils import (
    print_task_title,
    print_result,
    task_name,
    task_info,
    exit_error,
)


def update_serial_number(task: Task) -> Result:
    """
    Update the device serial number in NetBox based on the serial number retrieved from the Cisco device.

    Args:
        task (Task): The Nornir task object.

    Returns:
        Result: The Nornir result object.
    """
    task_text = "Update device serial number"

    # Use the helper function _get_serial_numbers to get the software version
    serials, sub_serials, verbose_result, failed = _get_serial_numbers(task=task)
    # If failed is the the verbose result contains the full Nornir result string (result + verbose_result)
    if failed:
        # Return the Nornir result as failed
        return Result(host=task.host, result=verbose_result, failed=True)

    # Create the API payload to update the device serial number or return the Nornir result as failed
    payload = _nb_create_payload_patch_device_serials(task=task, task_text=task_text, serials=serials)

    # Update the device serial number in NetBox
    url = f"{task.nornir.config.inventory.options['nb_url']}/api/dcim/devices/"
    result = _nb_patch_resources(task=task, task_text=task_text, url=url, payload=payload)
    result += f"\n-> Serials: {[item['serial'] for item in payload]}"

    # If the add_serials dict is not empty, then the dict contains managed devices by a controller (e.g. WLC)
    if not sub_serials:
        return Result(host=task.host, result=result, changed=False, failed=failed)

    # Create a list of dicts. Multiple dicts if its a virtual chassis
    payload = []
    for serial, device in sub_serials.items():
        nb_device = get_nb_resources(url=f"{url}?name={device}")
        if nb_device:
            payload.append({"id": nb_device[0]["id"], "serial": serial})
            result += f"\n-> Serial: {serial} (Sub-Device)"
        else:
            result += f"\n-> Serial: {serial} (Sub-Device '{device}' not in NetBox)"
            failed = True

    # POST request to update the Cisco Support Plugin desired release
    response = patch_nb_resources(url=url, payload=payload)
    # Verify the response code and return the result
    if response.status_code != 200:
        failed = True

    return Result(host=task.host, result=result, changed=False, failed=failed)


def update_cisco_inventory_data(nr: Nornir) -> bool:
    """
    Update NetBox Cisco Device Inventory Data. This function runs a Nornir task to update the serial number
    of Cisco devices in NetBox. The Nornir inventory is filtered by device manufacturer (Cisco), device
    status (active), and device role (router, switch or wlc). If any of the tasks fail, the function returns
    True, otherwise it returns False.

    Args:
        nr: The Nornir inventory object.

    Returns:
        bool: True if any of the tasks failed, False otherwise.
    """

    # Track if one of the tasks has failed
    failed = False

    print_task_title(title="Update NetBox Cisco Device Inventory Data")

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

    # Run the custom Nornir task update_serial_number
    task_text = "NETBOX update device serial number"
    result = nr_cisco.run(name=task_text, task=update_serial_number, on_failed=True)
    # Print the whole result for each host
    print_result(result)
    if result.failed:
        failed = True

    return failed


def main(nr_config: str) -> None:
    """
    Main function is intended to import and execute by other scripts. It initialize Nornir and update Cisco
    inventory data in NetBox.

    * Args:
        * nr_config (str): Path to the Nornir configuration file.

    * Steps:
        * Initializes the Nornir inventory object using the provided configuration file.
        * Runs the Nornir Cisco support plugin to update NetBox Cisco inventory data.
        * Checks the result of the update task and exits the script with an error message if the task failed.

    * Exit:
        * Exits with code 1 if the Nornir configuration file is empty or if any task fails.
    """

    #### Initialize Nornir ##################################################################################

    # Initialize, transform and filter the Nornir inventory are return the filtered Nornir object
    # Define data to load from NetBox in addition to the base Nornir inventory plugin
    add_netbox_data = {"load_virtual_chassis_data": True}
    nr = init_nornir(config_file=nr_config, add_netbox_data=add_netbox_data)

    #### Run Nornir Cisco Support Plugin Update Tasks #######################################################

    # Update NetBox Cisco inventory data
    result_failed = update_cisco_inventory_data(nr=nr)

    # Check the result and exit the script with exit code 1 and a error message
    if result_failed:
        text = "Update NetBox Cisco Device Inventory Data with Nornir"
        print(task_name(text=text))
        exit_error(
            task_text=f"{text} Failed",
            msg="Check the result details for failed Nornir tasks",
        )
