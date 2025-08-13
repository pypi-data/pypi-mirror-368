#!/usr/bin/env python3
"""
This module contains general configuration management functions and tasks related to Nornir.

The functions are ordered as followed:
- Helper Functions
- Nornir print functions
- Nornir Helper Tasks
"""

import os
import sys
import time
import subprocess  # nosec
import argparse
import urllib
from typing import Literal
import __main__
from colorama import Fore, Style, init
from yaspin import yaspin
from yaspin.spinners import Spinners
from nornir_scrapli.tasks import send_commands
from nornir.core import Nornir
from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_file_transfer
from nornir_collection.utils import (
    CustomArgParse,
    CustomArgParseWidthFormatter,
    get_env_vars,
    print_result,
    print_task_name,
    task_name,
    task_host,
    task_info,
    compute_hash,
)

init(autoreset=True, strip=False)


#### Helper Functions ########################################################################################


def init_args_for_software_upgrade() -> argparse.Namespace:
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
        description="Specify the NetBox instance and filter the Nornir inventory based on a tag or a host",
        epilog="At least one of the mandatory arguments role, tags or hosts needs to be specified.",
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

    # Add the optional commit_reload argument
    argparser.add_argument(
        "-c",
        "--commit_reload",
        action="store_true",
        default=False,
        help="commit the software upgrade to reload the device (default: False)",
    )

    # Add the optional issu argument
    argparser.add_argument(
        "-i",
        "--issu",
        action="store_true",
        default=False,
        help="enable ISSU software upgrade (default: False)",
    )

    # Add the optional remove_inactive argument
    argparser.add_argument(
        "-r",
        "--remove_inactive",
        action="store_true",
        default=False,
        help="remove inactive software files (default: False)",
    )

    # Add the optional rebuild argument
    argparser.add_argument(
        "-l",
        "--local_upload",
        action="store_true",
        default=False,
        help="enable local upload with SCP (default: HTTP download)",
    )

    # Add the optional verbose argument
    argparser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="show extensive result details (default: False)",
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

    print("-> Upgrade arguments:")
    print(f"  - Run on the '{nb_instance}' NetBox instance and Nornir config '{nr_config}'")
    if args.commit_reload:
        print("  - Commit the software upgrade to reload the device")
    else:
        print("  - No reload to commit the software (Software copy only)")
    if args.issu:
        print("  - Enable ISSU software upgrade without downtime (C9500 only)")
    else:
        print("  - Regular software upgrade with downtime (No ISSU)")
    if args.remove_inactive:
        print("  - Filesystem cleanup to remove inactive software files before upgrade")
    else:
        print("  - No filesystem cleanup before upgrade")
    if args.local_upload:
        print("  - Local software image upload by SCP")
    else:
        print("  - Remote software download by HTTP")

    if args.verbose:
        print(f"\n{args}")

    return nr_config, args


def verify_issu_requirements(nr: Nornir) -> bool:
    """
    TBD
    """
    # Run the custom Nornir task verify_issu_requirements
    task_result = nr.run(
        task=verify_issu_requirements_task,
        name="NORNIR verify ISSU requirements",
        on_failed=True,
    )

    # Print the Nornir task result
    print_result(task_result)

    # Return False if the task failed or True if the task was successful
    return not bool(task_result.failed)


def cli_track_issu_upgrade_process(nr: Nornir, max_time: int) -> None:
    """
    This function creates a dictionary with the installation process status of each host and runs the standard
    Nornir Scrapli task send_commands in a range loop. In each loop the software installation status will be
    updated and printed to std-out. There are three expected status which each host will go through the
    installation process. When all hosts are upgraded successful the script exits the range loop and prints
    the result to std-out. In case the software upgrade is not successful after the range loop is finish, an
    info message will be printed and exit the script.
    """
    # Printout sleep and refresh values
    std_out_print = []
    refresh_timer = 10
    max_refresh = max_time // refresh_timer  # double slash division is a int / single slash would be a float
    elapsed_time = 0
    # Set a elapsed timer to wait for the switch reload to start
    elapsed_time_reload_switch_1 = 0
    elapsed_time_reload_switch_2 = 0
    # Stack reload and HA sync status list (except ready)
    show_switch_status_not_ready = ["Removed", "Initializing", "HA sync in progress", "V-Mismatch"]

    # Dict to track the host software upgrade status
    update_status = {}
    for host in nr.inventory.hosts:
        update_status[host] = (
            f"{Fore.YELLOW}No ISSU operation is in progress (Installing software){Fore.RESET}"
        )

    print(task_name("Track ISSU software upgrade process"))

    for _ in range(max_refresh):
        # Run the standard Scrapli task send_command to get the software upgrade status
        task = nr.run(
            task=send_commands,
            commands=["show issu state detail", "show switch"],
            strip_prompt=False,
            on_failed=True,
        )
        # Close all Nornir connections to ensure a reconnect after the switch reload is possible
        nr.close_connections(on_failed=True)

        # If std_out_print is not empty remove the previous print
        # Cursor up the number of lines in std_out_print to overwrite/delete the previous print
        if len(std_out_print) > 0:
            sys.stdout.write("\033[F" * len(std_out_print))  # Cursor up the number of lines in std_out_print
            sys.stdout.write("\033[2K")  # Clear the line
            sys.stdout.flush()  # Flush the stdout buffer
            std_out_print = []

        # Update the host software upgrade status and print the result
        for host in task:
            output = str(task[host].result).rstrip()

            # Get the lines from the Scrapli task result starting with "State transition:"
            for line in output.splitlines():
                # Step 1: Added Software and reload the Switch 2
                if line == "State transition: Added":
                    # Wait to reload timer to exceed 120s to check the stack status
                    if elapsed_time_reload_switch_2 <= 120:
                        update_status[host] = f"{Fore.YELLOW}{line}{Fore.RESET}"
                        elapsed_time_reload_switch_2 += refresh_timer
                    # Check if a reload or stack sync is in progress
                    elif any(status in output for status in show_switch_status_not_ready):
                        update_status[host] = f"{Fore.YELLOW}{line} (Reloading Switch 2){Fore.RESET}"
                    else:
                        update_status[host] = f"{Fore.YELLOW}{line}{Fore.RESET}"
                    # Break the loop to continue with the next host
                    break

                # Step 2: Activate the standby switch
                if line == "State transition: Added -> Standby activated":
                    update_status[host] = f"{Fore.YELLOW}{line}{Fore.RESET}"
                    # Break the loop to continue with the next host
                    break

                # Step 3: Reload the Switch 1
                if line == "State transition: Added -> Standby activated -> Active switched-over":
                    # Wait to reload timer to exceed 120s to check the stack status
                    if elapsed_time_reload_switch_1 <= 120:
                        update_status[host] = f"{Fore.YELLOW}{line}{Fore.RESET}"
                        elapsed_time_reload_switch_1 += refresh_timer
                    # Check if a reload or stack sync is in progress
                    elif any(status in output for status in show_switch_status_not_ready):
                        update_status[host] = f"{Fore.YELLOW}{line} (Reloading Switch 1){Fore.RESET}"
                    else:
                        update_status[host] = f"{Fore.GREEN}ISSU Upgrade finish{Fore.RESET}"
                    # Break the loop to continue with the next host
                    break

            # Add the host software upgrade status result to the std_out_print list
            std_out_print.append(task_host(host=host, changed=False))
            std_out_print.append(f"ISSU State: {update_status[host]}")

        # Print empty line
        std_out_print.append("")

        # Check if all hosts have upgraded successfull
        if not all(
            f"{Fore.GREEN}ISSU Upgrade finish{Fore.RESET}" in value for value in update_status.values()
        ):
            # Continue the range loop to track to software upgrade status
            total_time = max_refresh * refresh_timer
            std_out_print.append(
                f"{Style.BRIGHT}{Fore.YELLOW}Elapsed waiting time: {elapsed_time}/{total_time}s"
            )
            std_out_print.append(f"{Style.DIM}(The ISSU task result will refresh in {refresh_timer}s)")
            # Print the loop result
            for line in std_out_print:
                print(line)
            # Wait for the refresh timer to continue the range loop
            elapsed_time += refresh_timer
            time.sleep(refresh_timer)

        else:
            # Print result and exit the range loop
            std_out_print.append(
                f"{Style.BRIGHT}{Fore.GREEN}Elapsed waiting time: {elapsed_time}/{total_time}s"
            )
            std_out_print.append("Wait 120s to ensure the device NGINX RESTCONF server is ready")
            # Print the loop result
            for line in std_out_print:
                print(line)
            # Sleep for some seconds until the device NGINX RESTCONF server is ready
            time.sleep(120)
            break

    # If the range loop reached the end -> Software upgrade not successful
    else:
        sys.stdout.write("\033[F")  # Cursor up one line
        sys.stdout.write("\033[2K")  # Clear the line
        sys.stdout.flush()  # Flush the stdout buffer
        print(
            f"{Style.BRIGHT}{Fore.RED}"
            f"Total ISSU software upgrade waiting time of {max_refresh * refresh_timer}s exceeded"
        )


def fping_track_upgrade_process(nr: Nornir, max_time: int) -> None:
    """
    This function creates a dictionary with the installation process status of each host and runs the custom
    Nornir task fping_task in a range loop. In each loop the software installation status will be updated and
    printed to std-out. There are three expected status which each host will go through the installation
    process. These status are "Installing software", "Rebooting device" and the final status will be "Upgrade
    finish". When all hosts are upgraded successful the script exits the range loop and prints the result to
    std-out. In case the software upgrade is not successful after the range loop is finish, an info message
    will be printed and exit the script.
    """

    # Printout sleep and refresh values
    std_out_print = []
    refresh_timer = 10
    max_refresh = max_time // refresh_timer  # double slash division is a int / single slash would be a float
    elapsed_time = 0

    # Dict to track the host software upgrade status
    update_status = {}
    for host in nr.inventory.hosts:
        update_status[host] = "Installing software"

    print(task_name("Track software upgrade process"))

    for _ in range(max_refresh):
        # Run the custom Nornir task fping_task
        task = nr.run(task=fping_task, on_failed=True)
        # Close all Nornir connections to ensure a reconnect after the switch reload is possible
        nr.close_connections(on_failed=True)

        # If std_out_print is not empty remove the previous print
        # Cursor up the number of lines in std_out_print to overwrite/delete the previous print
        if len(std_out_print) > 0:
            sys.stdout.write("\033[F" * len(std_out_print))  # Cursor up the number of lines in std_out_print
            sys.stdout.write("\033[2K")  # Clear the line
            sys.stdout.flush()  # Flush the stdout buffer
            std_out_print = []

        # Update the host software upgrade status and print the result
        for host in task:
            # host fping task result
            fping = task[host].result["output"].rstrip()

            # Initial status -> Host is alive and is installing the software
            if "alive" in fping and "Installing software" in update_status[host]:
                update_status[host] = f"{Fore.YELLOW}Installing software{Fore.RESET}"
            # Second status -> Host is not alive and is rebooting
            if "alive" not in fping and "Installing software" in update_status[host]:
                update_status[host] = f"{Fore.RED}Reboot device{Fore.RESET}"
            if "alive" not in fping and "Rebooting device" in update_status[host]:
                pass
            # Third status -> host is rebooted with new software release
            if "alive" in fping and "Reboot device" in update_status[host]:
                update_status[host] = f"{Fore.GREEN}Upgrade finish{Fore.RESET}"

            # Add the host software upgrade status result to the std_out_print list
            std_out_print.append(task_host(host=host, changed=False))
            std_out_print.append(f"Status: {update_status[host]} (fping: {fping})")

        # Print empty line
        std_out_print.append("")

        # Check if all hosts have upgraded successfull
        if not all(f"{Fore.GREEN}Upgrade finish{Fore.RESET}" in value for value in update_status.values()):
            # Continue the range loop to track to software upgrade status
            total_time = max_refresh * refresh_timer
            std_out_print.append(
                f"{Style.BRIGHT}{Fore.YELLOW}Elapsed waiting time: {elapsed_time}/{total_time}s"
            )
            std_out_print.append(f"{Style.DIM}(The fping task result will refresh in {refresh_timer}s)")
            # Print the loop result
            for line in std_out_print:
                print(line)
            # Wait for the refresh timer to continue the range loop
            elapsed_time += refresh_timer
            time.sleep(refresh_timer)

        else:
            # Print result and exit the range loop
            std_out_print.append(
                f"{Style.BRIGHT}{Fore.GREEN}Elapsed waiting time: {elapsed_time}/{total_time}s"
            )
            std_out_print.append("Wait 120s to ensure the device NGINX RESTCONF server is ready")
            # Print the loop result
            for line in std_out_print:
                print(line)
            # Sleep for some seconds until the device NGINX RESTCONF server is ready
            time.sleep(120)
            break

    # If the range loop reached the end -> Software upgrade not successful
    else:
        sys.stdout.write("\033[F")  # Cursor up one line
        sys.stdout.write("\033[2K")  # Clear the line
        sys.stdout.flush()  # Flush the stdout buffer
        print(
            f"{Style.BRIGHT}{Fore.RED}"
            f"Total software upgrade waiting time of {max_refresh * refresh_timer}s exceeded"
        )


def cli_verify_switch_state(nr: Nornir, max_time: int) -> None:
    """
    This function runs the custom Nornir Scrapli task cli_verify_switch_state to get the switch stack state
    of each host.
    """

    # Printout sleep and refresh values
    std_out_print = []
    refresh_timer = 10
    max_refresh = max_time // refresh_timer  # double slash division is a int / single slash would be a float
    elapsed_time = 0
    # Stack reload and HA sync status list (except ready)
    show_switch_status_not_ready = ["Removed", "Initializing", "HA sync in progress", "V-Mismatch"]

    # Dict to track the host software upgrade status
    update_status = {}
    for host in nr.inventory.hosts:
        update_status[host] = f"{Fore.YELLOW}Not all switches are ready{Fore.RESET}"

    print(task_name("Verify switch stack state"))

    for _ in range(max_refresh):
        # Run the standard Scrapli task send_command to get the switch stack state
        task = nr.run(
            task=send_commands,
            commands=["show switch"],
            strip_prompt=False,
            on_failed=True,
        )
        # Close all Nornir connections to ensure a reconnect after the switch reload is possible
        nr.close_connections(on_failed=True)

        # If std_out_print is not empty remove the previous print
        # Cursor up the number of lines in std_out_print to overwrite/delete the previous print
        if len(std_out_print) > 0:
            sys.stdout.write("\033[F" * len(std_out_print))
            sys.stdout.flush()
            std_out_print = []

        # Update the host switch stack state and print the result
        for host in task:
            # Check if a reload or stack sync is in progress
            output = str(task[host].result).rstrip()
            if not any(status in output for status in show_switch_status_not_ready):
                update_status[host] = f"{Fore.GREEN}All switches are ready{Fore.RESET}"

            # Add the host software upgrade status result to the std_out_print list
            std_out_print.append(task_host(host=host, changed=False))
            std_out_print.append(f"Stack State: {update_status[host]}")

        # Print empty line
        std_out_print.append("")

        # Check if all hosts have upgraded successfull
        if not all(
            f"{Fore.GREEN}All switches are ready{Fore.RESET}" in value for value in update_status.values()
        ):
            # Continue the range loop to track to software upgrade status
            total_time = max_refresh * refresh_timer
            std_out_print.append(
                f"{Style.BRIGHT}{Fore.YELLOW}Elapsed waiting time: {elapsed_time}/{total_time}s"
            )
            std_out_print.append(f"{Style.DIM}(The task result will refresh in {refresh_timer}s)")
            # Print the loop result
            for line in std_out_print:
                print(line)
            # Wait for the refresh timer to continue the range loop
            elapsed_time += refresh_timer
            time.sleep(refresh_timer)

        else:
            # Print the loop result
            for line in std_out_print:
                print(line)
            # Return True if all switches in the stack are ready
            return True

    # If the range loop reached the end -> Not all switches in the stack are ready
    sys.stdout.write("\033[F")  # Cursor up one line
    sys.stdout.write("\033[2K")  # Clear the line
    sys.stdout.flush()  # Flush the stdout buffer
    print(f"{Style.BRIGHT}{Fore.RED}Total waiting time of {max_refresh * refresh_timer}s exceeded\n")

    # Return False if not all switches in the stack are ready
    return False


#### Nornir Helper Tasks #####################################################################################


def prepare_upgrade_data_task(task: Task, upgrade_type: Literal["http", "scp"]) -> Result:
    """
    This custom Nornir task verifies the source for the software upgrade which can be a http URL or a scp
    filepath. The source md5 hash, the filesize as well as the destination file will be written to the Nornir
    inventory for later usage. The task returns the Nornir Result object.
    """
    upgrade_type = upgrade_type.lower()

    try:
        desired_version = task.host["software"]["version"]

        if "http" in upgrade_type:
            http_url = task.host["software"]["http_url"]
            if "filepath" in task.host["software"]:
                source_file = task.host["software"]["filepath"]
            else:
                source_file = task.host["software"]["http_url"]
        elif "scp" in upgrade_type:
            source_file = task.host["software"]["filepath"]

    except KeyError as error:
        # KeyError exception handles not existing host inventory data keys
        result = f"'Key task.host[{error}] not found' -> NornirResponse: <Success: False>"
        # Return the Nornir result as error
        return Result(host=task.host, result=result, failed=True)

    # Compute the original md5 hash value
    source_md5 = compute_hash(source=source_file, algorithm="md5")
    # Extract only the filename and prepare the destination path
    dest_file = os.path.basename(source_file)

    if "http" in upgrade_type:
        # Get the filesize and format to GB
        # Bandit "B310: urllib_urlopen" if solved to raise a ValueError is the value starts not with http
        if http_url.lower().startswith("http"):
            response = urllib.request.Request(http_url, method="HEAD")
            with urllib.request.urlopen(response) as response:  # nosec
                file_size = "%.2f" % (int(response.headers["Content-Length"]) / (1024 * 1024 * 1024))
        else:
            raise ValueError from None

        result = (
            f"'{task.name}' -> OSResponse: <Success: True>\n"
            f"-> Desired version: {desired_version}\n"
            f"-> Source: {http_url}\n"
            f"-> Source MD5-Hash: {source_md5}"
        )

    elif "scp" in upgrade_type:
        # Verify that the software file exists
        if not os.path.exists(source_file):
            result = f"'File {source_file} not found' -> OSResponse: <Success: False>\n"
            # Return the Nornir result as error
            return Result(host=task.host, result=result, failed=True)

        # Get the filesize and format to GB
        file_size = "%.2f" % (os.path.getsize(source_file) / (1024 * 1024 * 1024))

        result = (
            f"'{task.name}' -> OSResponse: <Success: True>\n"
            f"-> Desired version: {desired_version}\n"
            f"-> Source: {source_file}\n"
            f"-> Source MD5-Hash: {source_md5}"
        )

    # Write the variables into the Nornir inventory
    task.host["software"]["source_md5"] = source_md5
    task.host["software"]["file_size"] = file_size
    task.host["software"]["dest_file"] = dest_file

    # Return the Nornir result as success
    return Result(host=task.host, result=result)


def scp_upload_software_file_task(task: Task) -> Result:
    """
    This custom Nornir task runs the netmiko_file_transfer task with the source and destination file loaded
    from the Nornir inventory to upload the software file to each host. The task returns the Nornir Result
    object.
    """

    # Run the standard Nornir task netmiko_file_transfer
    result = task.run(
        task=netmiko_file_transfer,
        source_file=task.host["software"]["filepath"],
        dest_file=task.host["software"]["dest_file"],
        direction="put",
    )

    # The netmiko_file_transfer result string is either True or False
    result = f"'NETMIKO execute software file upload with SCP' -> SCPResponse <Success: {result.result}>"

    return Result(host=task.host, result=result)


def cli_http_download_software_file_task(task: Task, verbose: bool = False) -> Result:
    """
    TBD
    """
    # Set the result_summary for a successful task
    result_summary = f"'{task.name}' -> CliResponse <Success: True>"

    # Get the host source http url and the destination file name from the Nornir inventory
    dest_file = task.host["software"]["dest_file"]
    http_url = task.host["software"]["http_url"]

    # Manually create Netmiko connection
    net_connect = task.host.get_connection("netmiko", task.nornir.config)

    # Execute send_multiline to expect and enter the destination file name to start the file copy
    output = net_connect.send_multiline(
        [
            [f"copy {http_url} flash:{dest_file}", r"Destination filename"],
            ["\n", ""],
        ],
        read_timeout=600,
    )

    if "copied in" in output:
        # Define the result variable for print_result
        result = result_summary + "\n\n" + output if verbose else result_summary

        # Return the custom Nornir result as success
        return Result(host=task.host, result=result)

    # Else the copy command failed without traceback exception
    result = f"'{task.name}' -> CliResponse <Success: False>\n\n{output}"
    # Return the Nornir result as failed
    return Result(host=task.host, result=result, failed=True)


def fping_task(task: Task) -> Result:
    """
    This custom Nornir task runs the linux command fping to the host IP-address. The returned result is a
    dictionary with the fping output and the retruncode.
    """

    # fmt: off
    fping = subprocess.run( # nosec
        ["fping", "-A", "-d", task.host.hostname,], check=False, capture_output=True
    )
    # fmt: on

    result = {"returncode": fping.returncode, "output": fping.stdout.decode("utf-8")}

    return Result(host=task.host, result=result)


def verify_issu_requirements_task(task: Task) -> Result:
    """
    TBD
    """
    # Get the current and the desired version from the Nornir inventory and slice the release to have
    # only the first two characters of the version number
    current_version = task.host["software"]["current_version"][:2]
    desired_version = task.host["software"]["version"][:2]

    # Verify that the desired version is greater or equal than the current version
    if int(desired_version) >= int(current_version):
        result = f"'{task.name}' -> NornirResponse <Success: True>\n-> ISSU upgrade is supported"
        # Return the Nornir result as success
        return Result(host=task.host, result=result)

    result = f"'{task.name}' -> NornirResponse <Success: False>\n-> ISSU downgrade is not supported"
    # Return the Nornir result as failed
    return Result(host=task.host, result=result, failed=True)


#### Nornir Helper tasks in regular Function #################################################################


def prepare_upgrade_data(nr: Nornir, upgrade_type: Literal["http", "scp"]) -> bool:
    """
    This function runs the custom Nornir task prepare_upgrade_data_task to verify the source for the software
    upgrade which can be a http URL or a scp filepath. The source md5 hash, the filesize as well as the
    destination file will be written to the Nornir inventory for later usage. The Nornir task result will be
    printed with print_result. In case of a source verification error a error message will be printed and the
    script terminates. The function return False if the task failed or True if the task was successful.
    """

    # Run the custom Nornir task prepare_upgrade_data_task
    task_result = nr.run(
        task=prepare_upgrade_data_task,
        name="NORNIR prepare upgrade data",
        upgrade_type=upgrade_type,
        on_failed=True,
    )

    # Print the Nornir task result
    print_result(task_result)

    # Return False if the task failed or True if the task was successful
    return not bool(task_result.failed)


def scp_upload_software_file(nr: Nornir) -> None:
    """
    TBD
    """

    print_task_name("NETMIKO prepare software file upload with SCP")
    # Print some info for each host
    for host in nr.inventory.hosts:
        dest_file = nr.inventory.hosts[host]["software"]["dest_file"]
        file_size = nr.inventory.hosts[host]["software"]["file_size"]
        print(task_host(host=host, changed=False))
        print("'NETMIKO prepare software file upload with SCP' -> SCPResponse <Success: True>")
        print(f"-> SCP copy {dest_file} ({file_size} GB) to flash:")

    print("")
    # Run the Nornir task scp_upload_software_file_task with a spinner
    spinner_text = f"{Style.BRIGHT}{Fore.YELLOW}NETMIKO execute software file upload with SCP in progress ..."
    with yaspin(Spinners.moon, text=spinner_text, side="right"):
        task_result = nr.run(
            task=scp_upload_software_file_task,
            name="NETMIKO execute software file upload with SCP",
            on_failed=True,
        )
    # Cursor up one line to overwrite/delete the spinner line
    sys.stdout.write("\033[F")

    print_result(task_result)

    # Return False if the task failed or True if the task was successful
    return not bool(task_result.failed)


def cli_http_download_software_file(nr: Nornir, verbose: bool = False) -> bool:
    """
    TBD
    """

    print_task_name("NETMIKO prepare software file download with HTTP")
    # Print some info for each host
    for host in nr.inventory.hosts:
        http_url = nr.inventory.hosts[host]["software"]["http_url"]
        file_size = nr.inventory.hosts[host]["software"]["file_size"]
        print(task_host(host=host, changed=False))
        print(task_info(text="NETMIKO prepare software file download with HTTP", changed=False))
        print("'NETMIKO prepare software file download with HTTP' -> SCPResponse <Success: True>")
        print(f"-> HTTP copy {http_url} ({file_size} GB) to flash:")

    print("")
    # Run the Nornir task cli_http_download_software_file_task with a spinner
    spinner_text = (
        f"{Style.BRIGHT}{Fore.YELLOW}NETMIKO execute software file download with HTTP in progress ..."
    )
    with yaspin(Spinners.moon, text=spinner_text, side="right"):
        task_result = nr.run(
            task=cli_http_download_software_file_task,
            name="NETMIKO execute software file download with HTTP",
            verbose=verbose,
            on_failed=True,
        )
    # Cursor up one line to overwrite/delete the spinner line
    sys.stdout.write("\033[F")

    # Print the Nornir task result
    print_result(task_result)

    # Return False if the task failed or True if the task was successful
    return not bool(task_result.failed)
