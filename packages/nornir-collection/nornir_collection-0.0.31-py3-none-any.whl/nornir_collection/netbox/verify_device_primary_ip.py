#!/usr/bin/env python3
"""
This module load the NetBox device inventory, find active management IP addresses, and verify their integrity.
The Main function is intended to import and execute by other scripts.
"""

import sys
import subprocess  # nosec
from nornir_collection.netbox.utils import get_nb_resources
from nornir_collection.utils import (
    print_task_title,
    task_name,
    exit_error,
    load_yaml_file,
    task_result,
)


__author__ = "Willi Kubny"
__maintainer__ = "Willi Kubny"
__version__ = "1.0"
__license__ = "MIT"
__email__ = "willi.kubny@dreyfusbank.ch"
__status__ = "Production"


def main(
    nr_config: str,
    mgmt_subnets: list[str],
    add_addresses: list[str] = [],
    exclude_addresses: list[str] = [],
) -> None:
    """
    Main function is intended to import and execute by other scripts.
    It verify the integrity of NetBox primary device management IP addresses.

    * Args:
        * nr_config (str): Path to the Nornir configuration file.
        * mgmt_subnets (list[str]): List of management subnets to scan for active IP addresses.
        * add_addresses (list[str], optional): List of additional IP addresses to scan. Defaults to [].
        * exclude_addresses (list[str], optional): List of IP addresses to exclude. Defaults to [].

    * Steps:
        * Loads the NetBox device inventory.
        * Finds all active NetBox primary device management IP addresses.
        * Scans all provided management subnets and additional addresses for active IP addresses using fping.
        * Verifies the integrity of NetBox primary device management IP addresses by checking:
            * If any NetBox primary IP addresses are missing from the scan.
            * If any active IP addresses from the scan are not part of the NetBox inventory.

    * Exits:
        * Exits with code 1 if the Nornir configuration file is empty or if any task fails.
    """
    #### Load NetBox Device Inventory ########################################################################

    task_title = "Load NetBox Device Inventory"
    print_task_title(title=task_title)

    # Load the Nornir yaml config file as dict and print a error message
    nr_config_dict = load_yaml_file(
        file=nr_config, text="Load Nornir Config File", silent=False, verbose=False
    )
    # Check the loaded config file and exit the script with exit code 1 if the dict is empty
    if not nr_config_dict:
        sys.exit(1)

    task_text = "Load NetBox Device Inventory"
    print(task_name(text=task_text))

    # Get the NetBox URL (Authentication token will be loaded as nb_token env variable)
    nb_url = nr_config_dict["inventory"]["options"]["nb_url"]
    params = {"status": "active", "has_primary_ip": True}
    nb_devices = get_nb_resources(url=f"{nb_url}/api/dcim/devices/?limit=0", params=params)

    # Set the task level to INFO if the nb_devices list if not empty
    level_name = "INFO" if nb_devices else "ERROR"
    success = "True" if level_name == "INFO" else "False"
    print(task_result(text=task_text, changed=False, level_name=level_name))
    print(
        f"'Load NetBox device inventory' -> NetBoxResult <Success: {success}>\n"
        + f"-> NetBox device count: {len(nb_devices)}",
    )
    # Exit the script if fping failed and the nb_devices list is empty
    if not nb_devices:
        exit_error(task_text=f"{task_text} Failed", msg="-> No NetBox device in API response")

    #### Find all NetBox primary device MGMT ip-addresses ###################################################

    task_text = "Find all active NetBox primary device mgmt ip-addresses"
    print(task_name(text=task_text))

    # Loop over all NetBox devices and create a list of their primary ipv4 address
    nb_mgmt_ips = [str(device["primary_ip"]["address"])[:-3] for device in nb_devices]

    # Set the task level to INFO if the nb_mgmt_ips list if not empty
    level_name = "INFO" if nb_mgmt_ips else "ERROR"
    success = "True" if level_name == "INFO" else "False"
    print(task_result(text=task_text, changed=False, level_name=level_name))
    print(
        f"'Find active mgmt ip-addresses' -> NornirResult <Success: {success}>\n"
        + f"-> NetBox primary device mgmt ip-address count: {len(nb_mgmt_ips)}",
    )
    # Exit the script if fping failed and the nb_mgmt_ips list is empty
    if not nb_mgmt_ips:
        exit_error(task_text=f"{task_text} Failed", msg="-> No NetBox primary device mgmt ip-addresses found")

    #### Find all active MGMT ip-addresses with fping #######################################################

    task_title = "Scan all script input mgmt ip-addresses with fping"
    print_task_title(title=task_title)

    task_text = "Find all active mgmt ip-addresses with fping"
    print(task_name(text=task_text))

    # Loop over all mgmt_subnets and create a list of active ip-addresses
    alive_ips = []
    for subnet in mgmt_subnets:
        # fmt: off
        fping = subprocess.run(["fping", "-a", "-g", subnet,], check=False, capture_output=True) # nosec
        # fmt: on
        output = fping.stdout.decode("utf-8").splitlines()
        alive_ips.extend([ip for ip in output if ip not in exclude_addresses])
    # Loop over all add_addresses and add them to the list of active ip-addresses
    for ip in add_addresses:
        # fmt: off
        fping = subprocess.run(["fping", "-a", ip,], check=False, capture_output=True) # nosec
        # fmt: on
        output = fping.stdout.decode("utf-8").splitlines()
        alive_ips.extend([ip for ip in output if ip not in exclude_addresses])

    # Set the task level to INFO if the alive_ip list if not empty
    level_name = "INFO" if alive_ips else "ERROR"
    success = "True" if level_name == "INFO" else "False"
    print(task_result(text=task_text, changed=False, level_name=level_name))
    print(
        f"'Find active mgmt ip-addresses' -> NornirResult <Success: {success}>\n"
        + f"-> Active mgmt ip-address count: {len(alive_ips)}",
    )
    # Exit the script if fping failed and the alive_ips list is empty
    if not alive_ips:
        exit_error(
            task_text=f"{task_text} Failed",
            msg=["-> No active mgmt ip-addresses found", "-> Verify the provided 'mgmt_subnets' input list"],
        )

    #### Verify NetBox primary device MGMT ip-addresses integrity ###########################################

    # Set a boolean to True if the integrity check fails
    integrity_failed = False

    task_title = "Verify NetBox primary device mgmt ip-address integrity"
    print_task_title(title=task_title)

    #### Verify NetBox ip-addresses not part of the script input parameters

    task_text = "Verify missing NetBox device ip-addresses for scan"
    print(task_name(text=task_text))

    # Find all NetBox primary ip-addresses which are not covered by the script input parameters
    ip_diff = list(set(nb_mgmt_ips) - set(alive_ips))

    # Set the task level to INFO if the ip_diff list if not empty
    level_name = "ERROR" if ip_diff else "INFO"
    success = "True" if level_name == "INFO" else "False"
    print(task_result(text=task_text, changed=False, level_name=level_name))
    print(f"'{task_text}' -> NornirResult <Success: {success}>")
    if ip_diff:
        integrity_failed = True
        print("-> The following NetBox device ip-addresses are not part of the script input parameters")
        for ip in ip_diff:
            print(f"- {ip}")
    else:
        print("-> All NetBox device ip-addresses are part of the script input parameters")

    #### Verify NetBox primary device mgmt ip-address integrity

    task_text = "Verify active device ip-addresses covered by NetBox"
    print(task_name(text=task_text))

    # Find all active ip-addresses which are not part of a NetBox primary ip-address
    ip_diff = list(set(alive_ips) - set(nb_mgmt_ips))

    # Set the task level to INFO if the ip_diff list if not empty
    level_name = "ERROR" if ip_diff else "INFO"
    success = "True" if level_name == "INFO" else "False"
    print(task_result(text=task_text, changed=False, level_name=level_name))
    print(f"'{task_text}' -> NornirResult <Success: {success}>")
    if ip_diff:
        integrity_failed = True
        print("-> The following active device ip-addresses are not part of the NetBox inventory")
        for ip in ip_diff:
            print(f"- {ip}")
    else:
        print("-> All active device ip-addresses are part of the NetBox inventory")

    # Exit the script with an error if the integrity check failed
    if integrity_failed:
        print("\r")
        exit_error(task_text=f"{task_title} Failed", msg="-> Verify the script results for failes tasks")
