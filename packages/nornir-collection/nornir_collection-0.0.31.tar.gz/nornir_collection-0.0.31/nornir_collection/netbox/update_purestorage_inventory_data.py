#!/usr/bin/env python3
"""
This module updates the serial number of Pure Storage devices in NetBox using Nornir.
The Main function is intended to import and execute by other scripts.
"""

from nornir.core import Nornir
from nornir.core.filter import F
from nornir.core.task import Task, Result
from nornir_collection.nornir_plugins.inventory.utils import init_nornir
from nornir_collection.purestorage.utils import _purestorage_get_connection
from nornir_collection.netbox.utils import _nb_patch_resources
from nornir_collection.utils import (
    print_task_title,
    print_result,
    task_name,
    task_info,
    exit_error,
)


__author__ = "Willi Kubny"
__maintainer__ = "Willi Kubny"
__version__ = "1.0"
__license__ = "MIT"
__email__ = "willi.kubny@dreyfusbank.ch"
__status__ = "Production"


def update_serial_number(task: Task) -> Result:
    """
    Update the serial number of a device in NetBox with the one retrieved from a Pure Storage FlashArray.

    Args:
        task (Task): A Nornir task object representing the device to update.

    Returns:
        Result: A Nornir result object with the outcome of the operation.
    """
    task_text = "Update device serial number"

    # Manually create the PureStorage connection or return the Nornir result as failed
    conn = _purestorage_get_connection(task=task)

    # Get all hardware details from the FlashArray
    response = conn.get_hardware()
    # Get the serial number of the chassis
    serial = [item["serial"] for item in response.items if item["type"] == "chassis"][0]
    if not serial:
        # Return the Nornir result as failed
        result = f"'{task_text}' -> APIResponse: <Success: False>\n-> Device serial not found in API response"
        return Result(host=task.host, result=result, failed=True)

    # Create the API payload to update the device serial number
    payload = [{"id": task.host["id"], "serial": serial}]

    # Get the NetBox url from the inventory options and update the device serial number in NetBox
    url = f"{task.nornir.config.inventory.options['nb_url']}/api/dcim/devices/"
    result = _nb_patch_resources(task=task, task_text=task_text, url=url, payload=payload)
    result += f"\n-> Serial: {serial}"

    # Return the result
    return Result(host=task.host, result=result, failed=False)


def update_purestorage_inventory_data(nr: Nornir) -> bool:
    """
    Update Pure-Storage device inventory data in NetBox. This function runs a custom Nornir task to update
    the serial number of each Pure-Storage device in NetBox.

    Args:
        nr (Nornir): The Nornir object representing the inventory.

    Returns:
        bool: True if any of the tasks failed, False otherwise.
    """

    # Track if one of the tasks has failed
    failed = False

    print_task_title(title="Update NetBox Pure-Storage Device Inventory Data")

    # Filter Nornir inventory by device manufacturer (a device can have only one manufacturer)
    nr_purestorage = nr.filter(
        F(device_type__manufacturer__slug__contains="pure-storage") & F(status__value="active")
    )
    task_text = "Filter nornir inventory"
    print(task_name(text=task_text))
    print(task_info(text=task_text, changed=False))
    print(
        f"'{task_text}' -> NornirResult <Success: True>\n"
        + "-> Filter condition: Device manufacturer slug contains 'pure-storage'",
    )

    # Run the custom Nornir task update_serial_number
    name = "NETBOX update device serial number"
    result = nr_purestorage.run(name=name, task=update_serial_number, on_failed=True)
    # Print the whole result for each host
    print_result(result)
    if result.failed:
        failed = True

    return failed


def main(nr_config: str) -> None:
    """
    Main function is intended to import and execute by other scripts.
    It initialize Nornir and update NetBox Pure-Storage inventory data.

    * Args:
        * nr_config (str): Path to the Nornir configuration file.

    * Steps:
        * Initializes the Nornir inventory object using the provided configuration file.
        * Executes the task to update NetBox Pure-Storage inventory data.
        * Checks the result of the update task and exits the script with an error message if the task failed.

    * Exits:
        * Exits with code 1 if the Nornir configuration file is empty or if any task fails.
    """

    #### Initialize Nornir ##################################################################################

    # Initialize, transform and filter the Nornir inventory are return the filtered Nornir object
    # Define data to load from NetBox in addition to the base Nornir inventory plugin
    add_netbox_data = {"load_virtual_chassis_data": True}
    nr = init_nornir(config_file=nr_config, add_netbox_data=add_netbox_data)

    #### Run Nornir Cisco Support Plugin Update Tasks #######################################################

    # Update NetBox Pure-Storate inventory data
    result_failed = update_purestorage_inventory_data(nr=nr)

    # Check the result and exit the script with exit code 1 and a error message
    if result_failed:
        text = "Update NetBox Pure-Storage Device Inventory Data with Nornir"
        print(task_name(text=text))
        exit_error(
            task_text=f"{text} Failed",
            msg="Check the result details for failed Nornir tasks",
        )
