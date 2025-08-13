#!/usr/bin/env python3
"""
This module contains general functions and tasks related to NetBox.

The functions are ordered as followed:
- Helper Functions
- Task Helper Functions
- Single Nornir tasks
- Nornir tasks in regular function
"""

import os
import argparse
import json
from typing import Tuple, Union, Any, Dict, List
import __main__
import requests
import pynetbox
from nornir.core.task import Task, Result
from nornir_collection.utils import (
    CustomArgParse,
    CustomArgParseWidthFormatter,
    get_env_vars,
    print_task_name,
    task_info,
)


#### Helper Functions #######################################################################################


def init_pynetbox(nb_url: str, ssl_verify=False) -> Tuple[pynetbox.api, pynetbox.api]:
    """
    This function instantiate a Pynetbox API object, print the result and returns the API object
    """
    task_text = "Initialize PyNetBox"
    print_task_name(text=task_text)

    # Load environment variables or raise a TypeError when is None
    env_vars = get_env_vars(envs=["NB_TOKEN"], task_text=task_text)

    # Instantiate the NetBox API
    session = requests.Session()
    session.verify = ssl_verify
    nb = pynetbox.api(url=nb_url, token=env_vars["NB_TOKEN"], threading=False)
    nb.http_session = session

    # Print success result
    print(task_info(text=task_text, changed=False))
    print(f"'{task_text}' -> Pynetbox.Api <Success: True>")
    print(f"-> Instantiate the PyNetBox API for '{nb_url}'")

    return nb


def init_args_for_nornir_config_filepath() -> str:
    """
    This function initialze arguments to specify which NetBox instance and Nornir config filepath to use.
    """
    task_text = "Argparse verify arguments"
    print_task_name(text=task_text)

    # Load environment variables or raise a TypeError when is None
    env_vars = get_env_vars(envs=["NR_CONFIG_PROD", "NR_CONFIG_TEST"], task_text=task_text)
    nr_config_prod = env_vars["NR_CONFIG_PROD"]
    nr_config_test = env_vars["NR_CONFIG_TEST"]

    # Define the arguments which needs to be given to the script execution
    argparser = CustomArgParse(
        prog=os.path.basename(__main__.__file__),
        description="Specify the NetBox PROD or TEST instance and Nornir config filepath to be used",
        epilog="One of the two mandatory arguments is required.",
        argument_default=argparse.SUPPRESS,
        formatter_class=CustomArgParseWidthFormatter,
    )
    # Add a argparser group for mutual exclusive arguments
    group = argparser.add_mutually_exclusive_group(required=True)
    # Add the test argument
    group.add_argument(
        "--prod",
        action="store_true",
        default=False,
        help=f"use the NetBox 'PROD' instance and Nornir config '{nr_config_prod}'",
    )
    # Add the test argument
    group.add_argument(
        "--test",
        action="store_true",
        default=False,
        help=f"use the NetBox 'TEST' instance and Nornir config '{nr_config_test}'",
    )
    # Verify the provided arguments and print the custom argparse error message in case of an error
    args = argparser.parse_args()

    # Set the NetBox instance and the Nornir config file based on the arguments
    nb_instance = "TEST" if args.test else "PROD"
    nr_config = nr_config_test if args.test else nr_config_prod

    # If argparser.parse_args() is successful -> no argparse error message
    print(task_info(text=task_text, changed=False))
    print(f"'{task_text}' -> ArgparseResponse <Success: True>")
    print(f"-> Run on the NetBox '{nb_instance}' instance and Nornir config '{nr_config}'")

    return nr_config


def init_args_for_ipam_update() -> str:
    """
    This function initialze arguments to specify which NetBox instance and Nornir config filepath to use.
    """
    task_text = "Argparse verify arguments"
    print_task_name(text=task_text)

    # Load environment variables or raise a TypeError when is None
    env_vars = get_env_vars(envs=["NR_CONFIG_PROD", "NR_CONFIG_TEST"], task_text=task_text)
    nr_config_prod = env_vars["NR_CONFIG_PROD"]
    nr_config_test = env_vars["NR_CONFIG_TEST"]

    # Define the arguments which needs to be given to the script execution
    argparser = CustomArgParse(
        prog=os.path.basename(__main__.__file__),
        description="Specify the NetBox PROD or TEST instance and Nornir config filepath to be used",
        epilog="One of the two mandatory arguments is required.",
        argument_default=argparse.SUPPRESS,
        formatter_class=CustomArgParseWidthFormatter,
    )
    # Add all NetBox arguments
    argparser.add_argument(
        "--prod",
        action="store_true",
        default=False,
        help=f"use the NetBox 'PROD' instance and Nornir config '{nr_config_prod}'",
    )
    argparser.add_argument(
        "--test",
        action="store_true",
        default=False,
        help=f"use the NetBox 'TEST' instance and Nornir config '{nr_config_test}'",
    )
    # Add the optional rebuild argument
    argparser.add_argument(
        "--nmap",
        action="store_true",
        default=False,
        help="enable additionally to IP-Fabric a NMAP scan (default: no NMAP scan)",
    )
    # Verify the provided arguments and print the custom argparse error message in case any error or wrong
    # arguments are present and exit the script
    args = argparser.parse_args()

    # Verify the NetBox instance and Nornir config filepath
    if not (hasattr(args, "prod") or hasattr(args, "test")):
        argparser.error("No NetBox instance specified, add --prod or --test")

    # Set the NetBox instance and the Nornir config file based on the arguments
    nb_instance = "TEST" if args.test else "PROD"
    nr_config = nr_config_test if args.test else nr_config_prod

    # If argparser.parse_args() is successful -> no argparse error message
    print(task_info(text=task_text, changed=False))
    print(f"'{task_text}' -> ArgparseResponse <Success: True>")
    print("-> Arguments:")
    print(f"  - Run on the '{nb_instance}' NetBox instance and Nornir config '{nr_config}'")
    if args.nmap:
        print("  - NMAP scan additionally to IP-Fabric is enabled (default: no NMAP scan)")
    else:
        print("  - NMAP scan additionally to IP-Fabric is disabled (default: no NMAP scan)")

    return nr_config, args


def get_nb_resources(url: str, params: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """
    TBD
    """
    # Define the resource list
    resources: List[Dict[str, Any]] = []
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Token {os.environ.get('NB_TOKEN')}",
    }
    # While there is a next page continue the loop
    while url:
        # Do the http request
        response = requests.get(  # nosec
            url=url, headers=headers, params=params, verify=False, timeout=(3.05, 27)
        )
        # Verify the response code
        if not response.status_code == 200:
            print(response.status_code)
            print(response.text)
            raise ValueError(f"Failed to get data from NetBox instance {url}")
        # Extract the json data from the http response
        resp = response.json()
        # Add the response to the resource list
        resources.extend(resp.get("results"))
        # Get the url of the next page
        url = resp.get("next")

    # Retrun the resources list
    return resources


def post_nb_resources(url: str, payload: List[Dict]) -> requests.Response:
    """
    TBD
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Token {os.environ.get('NB_TOKEN')}",
    }
    # Do the http request and return the result
    return requests.post(  # nosec
        url=url, headers=headers, data=json.dumps(payload), verify=False, timeout=(3.05, 27)
    )


def patch_nb_resources(url: str, payload: List[Dict]) -> requests.Response:
    """
    TBD
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Token {os.environ.get('NB_TOKEN')}",
    }
    # Do the http request and return the result
    return requests.patch(  # nosec
        url=url, headers=headers, data=json.dumps(payload), verify=False, timeout=(3.05, 27)
    )


def delete_nb_resources(url: str, payload: List[Dict]) -> requests.Response:
    """
    TBD
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Token {os.environ.get('NB_TOKEN')}",
    }
    # Do the http request and return the result
    return requests.delete(  # nosec
        url=url, headers=headers, data=json.dumps(payload), verify=False, timeout=(3.05, 27)
    )


#### Task Helper Functions ##################################################################################


def _nb_patch_resources(task: Task, task_text: str, url: str, payload: list) -> Union[str, Result]:
    """
    Sends a PATCH request to update the resources of a device in NetBox.
    Args:
        task (Task): The Nornir task object.
        task_text (str): The description of the task.
        payload (list): A list of dictionaries containing the resources to be updated.
    Returns:
        tuple: A tuple containing the result string and a boolean indicating whether the task failed.
    """
    # POST request to update the Cisco Support Plugin desired release
    response = patch_nb_resources(url=url, payload=payload)

    # Verify the response code and return the result
    if response.status_code != 200:
        result = (
            f"'{task_text}' -> NetBoxResponse: <Success: False>\n"
            + f"-> Response Status Code: {response.status_code}\n"
            + f"-> Response Text: {response.text}\n"
            + f"-> Payload: {payload}"
        )
        # Return the Nornir result
        return Result(host=task.host, result=result, changed=False, failed=True)

    # Return the result string
    result = f"'{task_text}' -> NetBoxResponse: <Success: True>"
    return result


def _nb_create_payload_patch_device_serials(task: Task, task_text: str, serials: dict) -> Union[list, Result]:
    """
    Create a payload for patching device serial numbers in NetBox.
    Args:
        task (Task): The Nornir task object.
        task_text (str): The task description.
        serials (dict): A dictionary containing the serial numbers for the devices.
    Returns:
        Union[List, Result]: A list of dictionaries containing the device IDs and serial numbers,
        or a Nornir Result object if an error occurs.
    """
    try:
        # Create a list of dicts. Multiple dicts if its a virtual chassis
        payload = []

        # Add the device depending if its a virtual chassis in NetBox or not
        if "virtual_chassis" in task.host and task.host["virtual_chassis"] is not None:
            # Add the master
            payload.append({"id": task.host["virtual_chassis"]["master"]["id"], "serial": serials["1"]})

            # Add all members to the payload if available
            if "members" in task.host["virtual_chassis"]:
                # Start enumerate with 2 as 1 is the virtual chassis master
                for num, member in enumerate(task.host["virtual_chassis"]["members"], start=2):
                    payload.append({"id": member["id"], "serial": serials[str(num)]})
        else:
            # Add the device (no virtual chassis)
            payload.append({"id": task.host["id"], "serial": serials["1"]})

        # Return the payload
        return payload

    except KeyError as error:
        result = f"'{task_text}' -> PythonResponse <Success: False>\n-> Dictionary key {error} not found"
        # Return the Nornir result
        return Result(host=task.host, result=result, changed=False, failed=True)


#### Nornir Tasks ###########################################################################################


#### Nornir Tasks ###########################################################################################
