#!/usr/bin/env python3
"""
This module updates the serial numbers of Fortinet devices in NetBox using Nornir.
The Main function is intended to import and execute by other scripts.
"""

from nornir.core import Nornir
from nornir.core.filter import F
from nornir.core.task import Task, Result
from nornir_collection.nornir_plugins.inventory.utils import init_nornir
from nornir_collection.fortinet.utils import get_fgt_resources
from nornir_collection.netbox.utils import _nb_patch_resources, _nb_create_payload_patch_device_serials
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
    Update the device serial number in NetBox based on the serial number retrieved from the Fortinet device.

    Args:
        task (Task): The Nornir task object.

    Returns:
        Result: The Nornir result object.
    """
    task_text = "Update device serial number"

    # Get the Fortinet device serial number from the Fortinet Rest API
    response = get_fgt_resources(task=task, url="api/v2/monitor/system/ha-peer/")

    # Verify the response code and return the result
    if response.status_code != 200:
        result = (
            f"'{task.name}' -> APIResponse: <Success: False>\n"
            + f"-> Response Status Code: {response.status_code}\n"
            + f"-> Response Text: {response.text}"
        )
        # Return the Nornir result
        return Result(host=task.host, result=result, changed=False, failed=True)

    # Create the serials dict to us in the function _nb_create_payload_patch_device_serials
    serials = {}
    if task.host["virtual_chassis"]:
        # Create a serials dict to map the serials to the virtual chassis member hostname
        response = {serial["hostname"]: serial["serial_no"] for serial in response.json()["results"]}
        # Create the serials dict for a HA cluster
        serials["1"] = response[f"{task.host['virtual_chassis']['master']['name']}"]
        if "members" in task.host["virtual_chassis"]:
            for num, member in enumerate(task.host["virtual_chassis"]["members"], start=2):
                serials[str(num)] = response[f"{member['name']}"]
    else:
        # Create the serials dict for a single device
        serials["1"] = response.json()["serial"]

    # Create the API payload to update the device serial number or return the Nornir result as failed
    payload = _nb_create_payload_patch_device_serials(task=task, task_text=task_text, serials=serials)

    # Get the NetBox url from the inventory options and update the device serial number in NetBox
    url = f"{task.nornir.config.inventory.options['nb_url']}/api/dcim/devices/"
    result = _nb_patch_resources(task=task, task_text=task_text, url=url, payload=payload)
    result += f"\n-> Serials: {[item['serial'] for item in payload]}"

    # Return the result
    return Result(host=task.host, result=result, changed=False, failed=False)


def update_fortinet_inventory_data(nr: Nornir) -> bool:
    """
    Update NetBox Cisco Device Inventory Data. This function runs a Nornir task to update the serial number
    of Fortinet devices in NetBox. The Nornir inventory is filtered by device manufacturer (fortinet). If any
    of the tasks fail, the function returns True, otherwise it returns False.

    Args:
        nr: The Nornir inventory object.

    Returns:
        bool: True if any of the tasks failed, False otherwise.
    """

    # Track if one of the tasks has failed
    failed = False

    print_task_title(title="Update NetBox Fortinet Device Inventory Data")

    # Filter Nornir inventory by device manufacturer (a device can have only one manufacturer)
    nr_fortinet = nr.filter(
        F(device_type__manufacturer__slug__contains="fortinet") & F(status__value="active")
    )
    task_text = "Filter nornir inventory"
    print(task_name(text=task_text))
    print(task_info(text=task_text, changed=False))
    print(
        f"'{task_text}' -> NornirResult <Success: True>\n"
        + "-> Filter condition: Device manufacturer slug contains 'fortinet'\n"
        + "                     & Device status value is 'active'"
    )

    # Run the custom Nornir task update_serial_number
    name = "NETBOX update device serial number"
    result = nr_fortinet.run(name=name, task=update_serial_number, on_failed=True)
    # Print the whole result for each host
    print_result(result)
    if result.failed:
        failed = True

    return failed


def main(nr_config: str) -> None:
    """
    Main function is intended to import and execute by other scripts.
    It initialize Nornir and update Fortinet inventory data in NetBox.

    * Args:
        * nr_config (str): Path to the Nornir configuration file.

    * Steps:
        * Initializes the Nornir inventory object using the provided configuration file.
        * Runs the task to update Fortinet inventory data in NetBox.
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

    # Update NetBox Fortigate inventory data
    result_failed = update_fortinet_inventory_data(nr=nr)

    # Check the result and exit the script with exit code 1 and a error message
    if result_failed:
        text = "Update NetBox Fortinet Device Inventory Data with Nornir"
        print(task_name(text=text))
        exit_error(
            task_text=f"{text} Failed",
            msg="Check the result details for failed Nornir tasks",
        )
