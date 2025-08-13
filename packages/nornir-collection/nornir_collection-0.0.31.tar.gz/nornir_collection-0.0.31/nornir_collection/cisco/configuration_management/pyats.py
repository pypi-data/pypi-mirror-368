#!/usr/bin/env python3
"""
This module contains Nornir pyATS functions and tasks.

The functions are ordered as followed:
- Nornir pyATS tasks in regular functions
"""

import subprocess  # nosec
import sys
from typing import Union
import yaml
from colorama import Fore, Style, init
from nornir.core import Nornir
from nornir_collection.utils import (
    print_task_title,
    print_task_name,
    task_host,
    task_info,
    task_error,
)
from nornir_collection.cisco.configuration_management.cli.show_tasks import write_commands_to_file
from nornir_collection.cisco.configuration_management.restconf.cisco_rpc import (
    rc_cisco_rpc_copy_file,
    rc_cisco_rpc_is_syncing,
)

init(autoreset=True, strip=False)


#### Nornir pyATS Functions ##################################################################################


def pyats_create_testbed(nr: Nornir, pyats_testbed_file: str) -> None:
    """
    This function create a pyATS testbed from a nornir inventory. The nornir object can be the whole inventory
    or a filtered subset.
    """

    # Create a empty dictionary to populate with every nornir host details
    pyats_testbed = {}
    pyats_testbed["devices"] = {}

    try:
        # Add each nornir host details to the dictionary
        for host in nr.inventory.hosts:
            # Create a nornir host object
            host_obj = nr.inventory.hosts[host]
            # Add a dictionary key for the nornir host
            pyats_testbed["devices"][str(host_obj)] = {}
            # Add dictionary keys and values from nornir inventory
            pyats_testbed["devices"][str(host_obj)].update(
                {
                    "type": host_obj["pyats"]["type"],
                    "os": host_obj["pyats"]["os"],
                    "platform": host_obj["pyats"]["platform"],
                    "credentials": {
                        "default": {
                            "username": nr.inventory.defaults.username,
                            "password": nr.inventory.defaults.password,
                        }
                    },
                    "connections": {
                        "cli": {
                            "protocol": host_obj["pyats"]["protocol"],
                            "ip": host_obj.hostname,
                        }
                    },
                }
            )

    except KeyError as error:
        # KeyError exception handles not existing host inventory data keys
        print(task_host(host=host, changed=False))
        print(task_error(text="PyATS create testbed failed", changed=False))
        print(f"Nornir inventory host key ['data']['pyats'][{error}] don't exist\n")
        sys.exit(1)

    # Write the pyATS testbed to a file encoded in yaml
    with open(pyats_testbed_file, "w", encoding="utf-8") as stream:
        stream.writelines(["---\n"])
        yaml.dump(pyats_testbed, stream, default_flow_style=False)


def pyats_update_golden_config(pyats_testbed_file: str) -> None:
    """
    This function creates or updates the pyATS golden config and prints a Nornir output to std-out
    """
    try:
        golden_config = "network_state/golden-config-cli"

        # fmt: off
        subprocess.run( # nosec
            ["pyats", "learn", "config", "--testbed-file",pyats_testbed_file, "--output", golden_config,],
            check=True, capture_output=True,
        )
        # fmt: on

        task_info_text = "PyATS update golden config"
        print(task_info(text=task_info_text, changed=False))
        print(f"'Update {golden_config}' -> PyATSResponse <Success: True>")

    except subprocess.CalledProcessError as error:
        # Exception is raised if subprocess exits with a non 0 status code
        task_error_text = "PyATS update golden config"
        print(task_error(text=task_error_text, changed=False))
        print(f"'Update {golden_config}' -> PyATSResponse <Success: False>\n")
        print(f"{error}")


def pyats_artifacts_cleanup(artifacts_list: list) -> None:
    """
    This function deletes a list of pyATS artifact files and prints a Nornir output to std-out
    """
    # Define a empty string to return at the end of the function
    task_info_result = ""
    task_error_result = ""

    # Delete each artifact in the artifacts_list
    for artifact in artifacts_list:
        try:
            # Delete all pyATS artifacts
            # fmt: off
            subprocess.run(["rm", "-r", artifact,],check=True, capture_output=True,) # nosec
            # fmt: on

            task_info_result += f"'Delete {artifact}' -> SubprocessResponse <Success:True>\n"

        except subprocess.CalledProcessError as error:
            # Exception is raised if subprocess exits with a non 0 status code
            task_error_result += f"{error}\n"

    task_text = "PyATS clean-up of artifact"

    # Return if all subprocess failed
    if not task_info_result:
        # Return error result only
        print(f"{task_error(text=task_text, changed=False)}\n" + f"{task_error_result.rstrip()}")
    # Return if all subprocess were successful
    elif not task_error_result:
        # Return info result only
        print(f"{task_info(text=task_text, changed=True)}\n" + f"{task_info_result.rstrip()}")
    # Return if it's a mix of failed and successfull subprocess
    else:
        # Return info and error result
        print(
            f"{task_info(text=task_text, changed=True)}\n"
            + f"{task_info_result.rstrip()}\n"
            + f"{task_error(text=task_text, changed=False)}\n"
            + f"{task_error_result.rstrip()}"
        )


def pyats_update_golden_cleanup(
    nr: Nornir, cfg_status: bool, task_text: str, pyats: dict, verbose: bool = False
) -> Union[str, None]:
    """
    This function is used to verify if a new golden config can be created based on the cfg_status boolian.
    If veriy_status is True a new golden config will be created and the list of artifact files can be deleted.
    """

    # Verify status of the config results
    print_task_title("Verify network from code config status")
    print_task_name(text="Verify config results")

    if cfg_status:
        # If the config is successful -> update the golden config
        print(task_info(text="Verify config results", changed=True))
        print(task_text[0])

        # Save the running-config as text-file to local disk
        print_task_title("Backup config file to local disk")

        write_commands_to_file(
            nr=nr,
            name="Backup config file to local disk",
            commands=["show running-config"],
            path="config_backup",
            filename_suffix="_config.txt",
            backup_config=True,
            verbose=verbose,
        )

        # Update golden config and clean-up artifacts
        print_task_title("Update golden config and clean-up artifacts")

        if pyats["generate_testbed"]:
            text = "PyATS generate testbed from Nornir inventory"
            print_task_name(text=text)
            # Create a pyATS testbed from the filtered Nornir inventory
            # Exceptions are handled inside the function
            pyats_create_testbed(nr=nr, pyats_testbed_file=pyats["testbed"])
            print(task_info(text=text, changed=True))
            print(f"'Generate {pyats['testbed']}' -> PyATSResponse <Success: True>")

        print_task_name(text="PyATS update golden config")
        pyats_update_golden_config(pyats_testbed_file=pyats["testbed"])

        # Checks to see if sync from the network element to the running datastore is
        # in progress and wait until the configuration datastore if unlocked again
        rc_cisco_rpc_is_syncing(nr=nr, verbose=verbose)

        rc_cisco_rpc_copy_file(
            nr=nr,
            name="RESTCONF save golden config",
            source="running-config",
            destination="flash:golden-config",
            verbose=verbose,
        )

        print_task_name(text="PyATS clean-up artifacts")
        pyats_artifacts_cleanup(artifacts_list=pyats["artifacts_list"])

        # No configuration error message to be returned
        error_msg = None

    else:
        # If one or more of the network from code config tasks failed
        task_error_text = "Config from code failed"
        print(task_error(text=task_error_text, changed=True))
        print(task_text[1])

        if pyats["cleanup_else"]:
            print_task_name(text="PyATS clean-up artifacts")
            pyats_artifacts_cleanup(artifacts_list=pyats["artifacts_list"])

        error_msg = (
            f"\n{Style.BRIGHT}{Fore.RED}-> Analyse the Nornir output for failed config tasks\n"
            "-> May apply Nornir inventory changes and run the script again\n\n"
            f"The golden config has not been updated yet!{Fore.RESET}{Style.RESET_ALL}\n"
        )

    # Return error_msg if exists or return None
    return error_msg if error_msg else None
