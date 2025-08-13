#!/usr/bin/env python3
"""
This module contains general configuration management functions and tasks related to Nornir.

The functions are ordered as followed:
- Helper Functions
- Nornir Result Helper Functions
- Nornir Helper Tasks
"""

import os
import re
import argparse
import ipaddress
from typing import Literal
import __main__
from requests import Response
from colorama import init
from nornir_jinja2.plugins.tasks import template_file
from nornir.core.task import Task, Result
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from nornir_collection.utils import (
    task_result,
    print_task_name,
    task_info,
    task_error,
    get_env_vars,
    CustomArgParse,
    CustomArgParseWidthFormatter,
)
from nornir_collection.netbox.inventory import get_nb_resources

init(autoreset=True, strip=False)


#### Helper Functions ########################################################################################


def create_tpl_int_list(task: Task) -> list:
    """
    This function loops over all host inventory keys and append the key which start with tpl_int to the list
    of interface groups and returns a Nornir AggregatedResult Object
    """
    tpl_int_list = []
    for key in task.host.keys():
        if key.startswith("tpl_int"):
            tpl_int_list.append(key)

    return tpl_int_list


def _split_nb_interface_addresses(addresses: dict) -> dict:
    """
    TBD
    """
    # Split NetBox address field e.g. 10.1.4.253/24 into ip and mask and create new key-value pairs
    for item in addresses:
        # For a single address (e.g. GET ip-addresses)
        if "address" in item:
            ip_address = ipaddress.ip_interface(item["address"])
            item["ip"] = str(ip_address.ip)
            item["mask"] = str(ip_address.netmask)
        # For a list of addresses (e.g. GET fhrp-groups)
        if "ip_addresses" in item:
            for address in item["ip_addresses"]:
                ip_address = ipaddress.ip_interface(address["address"])
                address["ip"] = str(ip_address.ip)
                address["mask"] = str(ip_address.netmask)

    return addresses


def _flatten_interface_custom_field(addresses: dict) -> dict:
    """
    TBD
    """
    # Flatten the NetBox custom_field (e.g. GET ip-addresses or GET fhrp-groups)
    for address in addresses:
        if "custom_fields" in address:
            for custom_fields, value in address["custom_fields"].items():
                address[custom_fields] = value
            address.pop("custom_fields")

    return addresses


def index_of_first_number(string: str) -> int:
    """
    Return the index of the first number in a string
    """

    for i, c in enumerate(string):
        if c.isdigit():
            index = i
            break

    return index


def extract_interface_number(string: str) -> str:
    """
    Removes the interface name and returns only the interface number
    """
    try:
        index = index_of_first_number(string)
        interface_number = string[index:]

    except UnboundLocalError:
        interface_number = string

    return interface_number


def extract_interface_name(string: str) -> str:
    """
    Removes the interface number and returns only the interface name
    """
    try:
        index = index_of_first_number(string)
        interface_name = string[:index]

    except UnboundLocalError:
        interface_name = string

    return interface_name


def complete_interface_name(
    interface_string: str,
) -> Literal[
    "Ethernet",
    "FastEthernet",
    "GigabitEthernet",
    "TenGigabitEthernet",
    "TwentyFiveGigE",
    "HundredGigE",
    "Port-channel",
    "Vlan",
]:
    """
    This function takes a string with an interface name only or a full interface with its number and returns
    the full interface name but without the number:
    Gi -> GigabitEthernet
    Tw -> TwentyFiveGigE
    etc.
    """
    if isinstance(interface_string, str):
        # Extract the interface name / delete the interface number
        interface_name = extract_interface_name(interface_string)
        # String normalization
        interface_name = interface_name.lower()

        # Starting string order from most characters frist to least characters last
        interfaces = {
            "eth": "Ethernet",
            "twe": "TwentyFiveGigE",
            "fa": "FastEthernet",
            "gi": "GigabitEthernet",
            "tw": "TwoGigabitEthernet",
            "te": "TenGigabitEthernet",
            "hu": "HundredGigE",
            "po": "Port-channel",
            "vlan": "Vlan",
        }

        # Return the correct full interface name
        for key, value in interfaces.items():
            if interface_name.startswith(key):
                return value

        raise ValueError(f"'{interface_string}' is not a known interface name")

    raise TypeError(f"Variable interface_string has type '{type(interface_string)}' and not type string")


def create_single_interface_list(interface: str) -> list:
    """
    This function takes a list of interfaces that are like the cisco interface range command and makes a list
    of full interface names for each interface:
    Gi1/0/1 -> GigabitEthernet1/0/1
    Gi1/0/1 - 10 -> GigabitEthernet1/0/1, GigabitEthernet1/0/2, etc.
    Gi1/0/1 - Gi1/0/10 -> GigabitEthernet1/0/1, GigabitEthernet1/0/2, etc.
    """
    # Define a list to return at the end of the function
    single_interface_list = []

    # Create the full name of the interface, eg. Gi -> GigabitEthernet
    interface_name = complete_interface_name(interface)

    # If the list element is a single interface add it to the list to return
    if "-" not in interface or "Port-channel" in interface:
        interface_number = extract_interface_number(interface)
        single_interface = interface_name + interface_number
        single_interface_list.append(single_interface)

        return single_interface_list

    # Else the list element is a interface range to fullfil every single interface
    # Create a list with the two interfaces for the range
    interface_range = interface.replace(" ", "")
    interface_range = interface.split("-")

    # Regex pattern to match only the last number after the /
    pattern = r"(\d+)(?!.*\d)"

    # 1. Match the interface number prefix without the last number
    interface_prefix = extract_interface_number(interface_range[0])
    interface_prefix = re.sub(pattern, "", interface_prefix)

    # 2. Match the number after the last / in the interface number
    last_interface_numbers = []
    for interface in interface_range:
        # Extract only the interface number
        interface_number = extract_interface_number(interface)
        last_interface_number = re.findall(pattern, interface_number)
        last_interface_numbers.append(last_interface_number[0])

    # Define integers for the first and the last number of the range
    range_first_number = int(last_interface_numbers[0])
    range_last_number = int(last_interface_numbers[1])
    # Iterate over the range and construct each single interface
    while range_first_number <= range_last_number:
        single_interface = interface_name + interface_prefix + str(range_first_number)
        single_interface = single_interface.replace(" ", "")
        single_interface_list.append(single_interface)
        range_first_number += 1

    return single_interface_list


def add_interface_data(task: Task, interface: dict) -> dict:
    """
    TBD
    """
    # If the interface is part of a Port-channel
    if "lag" in interface and interface["lag"] is not None:
        po_interface = [i for i in task.host["interfaces"] if i["name"] == interface["lag"]["name"]]
        interface["description"] = po_interface[0]["description"]
        interface["portchannel_number"] = extract_interface_number(interface["lag"]["name"])

    # Get the NetBox url from the inventory options
    nb_url = task.nornir.config.inventory.options["nb_url"]

    # Add the ip-addresses if the counter is bigger then 0
    if "count_ipaddresses" in interface and interface["count_ipaddresses"] > 0:
        response = get_nb_resources(
            url=f"{nb_url}/api/ipam/ip-addresses/?device={task.host['name']}&interface={interface['name']}"
        )
        # Flatten custom_fields
        response = _flatten_interface_custom_field(addresses=response)
        # Split NetBox address field e.g. 10.1.4.253/24 into ip and mask
        response = _split_nb_interface_addresses(addresses=response)
        # Add the modified response
        interface["ipaddresses"] = response
    else:
        interface["ipaddresses"] = None

    # Add the fhrp-groups if the counter is bigger then 0
    if "count_fhrp_groups" in interface and interface["count_fhrp_groups"] > 0:
        response = get_nb_resources(url=f"{nb_url}/api/ipam/fhrp-groups/?name={interface['name']}")
        # Flatten custom_fields
        response = _flatten_interface_custom_field(addresses=response)
        # Split NetBox address field e.g. 10.1.4.253/24 into ip and mask
        response = _split_nb_interface_addresses(addresses=response)
        # Add the modified response
        interface["fhrp_groups"] = response
    else:
        interface["fhrp_groups"] = None

    # Add the fhrp group-assignement if the counter is bigger then 0
    if "count_fhrp_groups" in interface and interface["count_fhrp_groups"] > 0:
        # Didn't found a querry to filter to interface and device
        # Therefor the loop to select the correct dicts matching interface and device
        response = get_nb_resources(url=f"{nb_url}/api/ipam/fhrp-group-assignments/")
        # Delete all assignments which are not for that interface
        response = [i for i in response if i["interface"]["name"] == interface["name"]]
        # Delete all assignments which are not for that host
        response = [i for i in response if i["interface"]["device"]["name"] == task.host["name"]]
        # Add the modified response
        interface["fhrp_group_assignment"] = response if response else None

    return interface


def init_args_for_netconf_cm() -> argparse.Namespace:
    """
    This function initialze all arguments which are needed for further script execution. The default arguments
    will be supressed. Returned will be a tuple with a use_nornir variable which is a boolian to indicate if
    Nornir should be used for dynamically information gathering or not.
    """
    task_text = "ARGPARSE verify arguments"
    print_task_name(text=task_text)

    # Load environment variables or raise a TypeError when is None
    env_vars = get_env_vars(envs=["NR_CONFIG_PROD", "NR_CONFIG_TEST"], task_text=task_text)
    nr_config_prod = env_vars["NR_CONFIG_PROD"]
    nr_config_test = env_vars["NR_CONFIG_TEST"]

    # Define the arguments which needs to be given to the script execution
    argparser = CustomArgParse(
        prog=os.path.basename(__main__.__file__),
        description="Specify the NetBox instance and Filter the Nornir inventory based on various criterias",
        epilog="At least one of the mandatory arguments role tags or hosts needs to be specified.",
        argument_default=argparse.SUPPRESS,
        formatter_class=CustomArgParseWidthFormatter,
    )

    # Add all NetBox arguments
    argparser.add_argument(
        "--prod",
        action="store_true",
        help=f"use the NetBox 'PROD' instance and Nornir config '{nr_config_prod}'",
    )
    argparser.add_argument(
        "--test",
        action="store_true",
        help=f"use the NetBox 'TEST' instance and Nornir config '{nr_config_test}'",
    )
    argparser.add_argument(
        "--role", type=str, metavar="<ROLE>", help="inventory filter for a single device role"
    )

    argparser.add_argument(
        "--tags", type=str, metavar="<TAGS>", help="inventory filter for comma seperated device tags"
    )

    argparser.add_argument(
        "--hosts", type=str, metavar="<HOST-NAMES>", help="inventory filter for comma seperated device hosts"
    )

    # Add the optional verbose argument
    argparser.add_argument(
        "--verbose", action="store_true", default=False, help="show extensive result details"
    )

    # Add the optional rebuild argument
    argparser.add_argument(
        "--rebuild",
        action="store_true",
        default=False,
        help="rebuild the config from day0 (default: golden-config)",
    )

    # Add the optional rebuild argument
    argparser.add_argument(
        "--disable-commit-confirm",
        action="store_true",
        default=False,
        help="disable NETCONF commit-confirm (default: enabled)",
    )

    # Add the optional rebuild argument
    argparser.add_argument(
        "--confirm-timeout",
        type=int,
        metavar="<INT>",
        default=240,
        help="set NETCONF commit-confirm timeout in seconds (default: 240s)",
    )

    # Add the optional rebuild argument
    argparser.add_argument(
        "--dryrun",
        action="store_true",
        default=False,
        help="perform a NETCONF dry-run (default: no dry-run)",
    )

    # Add the optional rebuild argument
    argparser.add_argument(
        "--pre-check",
        action="store_true",
        default=False,
        help="enable the pre-configuration check (default: False)",
    )

    # Verify the provided arguments and print the custom argparse error message in case any error or wrong
    # arguments are present and exit the script
    args = argparser.parse_args()

    # Verify the NetBox instance and Nornir config filepath
    if not (hasattr(args, "prod") or hasattr(args, "test")):
        argparser.error("No NetBox instance specified, add --prod or --test")
    # Verify the Nornir filter arguments
    if not (hasattr(args, "hosts") or hasattr(args, "role") or hasattr(args, "tags")):
        argparser.error("No Nornir inventory filter specified, add --hosts and/or roles and/or --tags")

    # Set the NetBox instance and the Nornir config file based on the arguments
    nb_instance = "TEST" if hasattr(args, "test") else "PROD"
    nr_config = nr_config_test if hasattr(args, "test") else nr_config_prod

    # If argparser.parse_args() is successful -> no argparse error message
    print(task_info(text=task_text, changed=False))
    print(f"'{task_text}' -> ArgparseResponse <Success: True>")

    print("-> Configuration-MGMT arguments:")
    print(f"  - Run on the '{nb_instance}' NetBox instance and Nornir config '{nr_config}'")
    if args.pre_check:
        print("  - Pre-configuration check is enabled (diff running-config/golden-config)")
    else:
        print("  - Pre-configuration check is disabled (diff running-config/golden-config)")
    if args.dryrun:
        print("  - NETCONF dry-run is enabled")
    else:
        if args.rebuild:
            print("  - Rebuild the configuration from the 'Day0-Config'")
        else:
            print("  - Rebuild the configuration from the 'Golden-Config'")
        if args.disable_commit_confirm:
            print("  - NETCONF commit-confirm is disabled")
        else:
            print(f"  - NETCONF commit-confirm is enabled (timeout: {args.confirm_timeout}s)")

    if args.verbose:
        print(f"\n{args}")

    return nr_config, args


#### Nornir Result Helper Functions #########################################################################


def set_restconf_result(
    task: Task,
    task_text: str,
    yang_query: str,
    response: Response,
    custom_result: list,
    verbose: bool = False,
) -> tuple:
    """
    TBD
    """
    # Set the verbose result string to add to the result summary
    result_verbose = (
        f"URL: {response['url']}\n"
        + f"Method: {response['method']}\n"
        + f"Response: {response['response']}\n"
        + f"Text: {response['text']}"
    )

    # Set the Nornir result to return as failed if the RESTCONF response status_code is not 200
    if response["status_code"] != 200:
        custom_result.append(
            f"{task_result(text=task_text, changed=False, level_name='ERROR', failed=True)}\n"
            + f"'{task_text}' -> RestconfResponse <Success: False>\n"
            + f"\n{response}"
        )
        return Result(host=task.host, custom_result=custom_result, failed=True)

    # Set the Nornir result
    msg = (
        f"{task_result(text=task_text, changed=False, level_name='INFO', failed=False)}\n"
        + f"'{task_text}' -> RestconfResponse <Success: True>\n"
        + f"-> Get data for '{yang_query}'"
    )
    custom_result.append(msg + f"\n\n{result_verbose}" if verbose else msg)

    return custom_result


def render_jinja2_template(task: Task, tpl_path: str, kwargs: dict = None) -> str:
    """
    TBD
    """
    # Split the string into path and file (template)
    path, filename = os.path.split(tpl_path)
    # Load the Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(path), undefined=StrictUndefined, trim_blocks=True, autoescape=True
    )
    template = env.get_template(filename)
    # Renders contants of a file with jinja2. All the host data is available in the template
    kwargs = kwargs or {}
    nc_config = template.render(host=task.host, **kwargs)

    return nc_config


#### Nornir Helper Tasks ####################################################################################


def template_file_custom(task: Task, task_msg: str, path: str, template: str) -> Result:
    """
    This custom Nornir task generates a configuration from a Jinja2 template based on a path and a template
    filename. The path and the template filename needs to be Nornir inventory keys which holds the needed
    information as value.
    """
    try:
        path = task.host[path]
        template = task.host[template]

    except KeyError as error:
        # Jinja2 Nornir inventory key not found. Key which specify the path and the file don't exist
        error_msg = (
            f"{task_error(text=task_msg, changed=False)}\n"
            + f"'nornir.core.inventory.Host object' has no attribute {error}"
        )

        # Return the Nornir result as error -> interface can not be configured
        return Result(host=task.host, result=error_msg, failed=True)

    # Run the Nornir Task template_file
    j2_tpl_result = task.run(task=template_file, template=template, path=path, on_failed=True)

    return Result(host=task.host, result=j2_tpl_result)
