#!/usr/bin/env python3
"""
This module contains screen-scraping functions and tasks related to Nornir.

The functions are ordered as followed:
- Screen-Scraping Helper Functions
- Single Nornir Screen-Scraping Tasks
- Nornir Screen-Scraping Tasks in regular Functions
"""

import sys
import time
from typing import Literal
from colorama import Fore, Style, init
from nornir_scrapli.tasks import send_config, send_configs, send_command, send_commands
from nornir_netmiko.tasks import netmiko_save_config
from nornir.core import Nornir
from nornir.core.task import Task, Result, AggregatedResult
from nornir_collection.utils import (
    print_task_name,
    task_host,
    task_info,
    task_error,
)
from nornir_collection.cisco.configuration_management.utils import (
    create_tpl_int_list,
    create_single_interface_list,
    template_file_custom,
)

init(autoreset=True, strip=False)


#### Screen-Scraping Helper Functions ########################################################################


def create_tpl_int_config_content(task_obj: Task, tpl_int_group: str) -> list:
    """
    This is a helper function for scrapli_replace_tpl_int_config() and creates the interface config contect
    from the Nornir host inventory object which is then appended to the interface configuration
    """
    # Create an empty list to append with the config
    config = []
    base_config = []
    add_config = []

    # Iterate over all host inventory keys
    for key in task_obj.host.keys():
        # Match the interface template config prefix
        if key.startswith(f"cfg_{tpl_int_group}"):
            # Match the key cfg_{tpl_int_group}_base
            if key in f"cfg_{tpl_int_group}_base":
                # Add the interface base config list to base_config
                base_config = task_obj[key]

            # Match all keys except cfg_{tpl_int_group}_base
            if key not in f"cfg_{tpl_int_group}_base":
                # Add all other interface config lists to add_config
                add_config += task_obj[key]

    # Add the base_config first and then the add_config
    config += base_config
    config += add_config

    # Return the list of the interface template config content
    return config


#### Single Nornir Screen Scraping Tasks #####################################################################


def scrapli_apply_jinja2_config(task: Task, jinja2_result_obj: AggregatedResult) -> Result:
    """
    This function takes the Nornir AggregatedResult object from function jinja2_generate_config() and applies
    the Jinja2 rendered configuration to each host.
    """

    # Access the jinja2_result which is a AggregatedResult object and split the config into a list of strings.
    config_list = jinja2_result_obj[str(task.host)][1].result.splitlines()

    # Run the standard Nornir Scrapli task send_configs
    result = task.run(
        name="Scrapli apply Jinja2 rendered config",
        task=send_configs,
        configs=config_list,
        strip_prompt=False,
        timeout_ops=180,
    )

    return Result(host=task.host, result=result)


def scrapli_replace_tpl_int_config(task: Task, tpl_int_group: str) -> Result:
    """
    Sets each interface in the interface_group to default and applies then the config template to the
    specified interfaces defined in hosts.yaml
    """
    try:
        # Create an interface list with full interface names, Gi -> GigabitEthernet
        single_interface_list = create_single_interface_list(task.host[tpl_int_group])

        # Construct config for each interface and apply the config
        for interface in single_interface_list:
            # Empty the list to append with the interface config
            interface_config = []

            # Set the interface to default and then enter the interface config
            interface_config.append("!")
            interface_config.append(f"default interface {interface}")
            interface_config.append("!")
            interface_config.append(f"interface {interface}")

            # Create the interface template content
            config = create_tpl_int_config_content(task_obj=task, tpl_int_group=tpl_int_group)

            # Add the interface template content to the interface config
            for line in config:
                interface_config.append(line)

            # Exit the interface config mode back to the config mode
            interface_config.append("exit")
            interface_config.append("!")

            # Apply interface config
            task.run(
                name="Scrapli interface config",
                task=send_configs,
                configs=interface_config,
                strip_prompt=False,
                stop_on_failed=False,
                timeout_ops=180,
            )

        return Result(host=task.host)

    except TypeError:
        # TypeError Exception handles empty host inventory interface lists
        # Print the exception result to avoid that Nornir interrupts the script
        return Result(host=task.host, result=f"No interface in template group {tpl_int_group}")
        # No interfaces in tpl_int_group (emtpy list)
        # Return the Nornir result as True as no interface should be configured

    except KeyError:
        # KeyError exception handles not existing host inventory data keys
        return Result(host=task.host, result=f"No template group {tpl_int_group} associated")
        # No tpl_int_group (template group key not in host inventory)
        # Return the Nornir result as True as no interface should be configured


#### Nornir Task in regular Functions ########################################################################


def cli_confirm_or_revert_config(
    nr: Nornir, action: Literal["confirm", "revert"], cfg_status: bool = True, verbose: bool = False
) -> bool:
    """
    TBD
    """

    # Return False if cfg_status argument is False
    if not cfg_status:
        return False

    # Run the standard Nornir Scrapli task send_configs
    results = nr.run(
        name=f"SCRAPLI CLI {action} config",
        task=send_command,
        command="configure confirm" if action == "confirm" else "configure revert now",
        strip_prompt=True,
        on_failed=True,
    )

    # Define the custom result to print
    print_task_name(text=results.name)
    for host in results:
        # Print the base result
        if results[host].failed or "%No Rollback Confirmed Change pending" in results[host].result:
            cfg_status = False
            print(task_host(host=host, changed=False))
            print(task_error(text=results.name, changed=False))
            print(f"'{results.name}' -> CliResponse <Success: False>")
            print(f"-> Configure {action} failed")
            print(f"\nVerbose result:\n{results[host].result}")
        else:
            print(task_host(host=host, changed=True))
            print(task_info(text=results.name, changed=True))
            print(f"'{results.name}' -> CliResponse <Success: True>")
            print(f"-> Configure {action} successful")
            if verbose:
                print(f"\nVerbose result:\n{results[host].result}")

    # Return the cfg_status variable
    return cfg_status


def save_config_cli(nr: Nornir, name: str, verbose: bool = False) -> bool:
    """
    #### CODE REFACTORING NEEDED -> INTRODUCE print_result ####

    This function runs a Nornir task to execute with Netmiko netmiko_save_config a write memory on each device
    and prints the result to std-out
    """

    print_task_name(text=name)

    task = nr.run(task=netmiko_save_config, cmd="write memory", on_failed=True)

    for host in task:
        print(task_host(host=host, changed=task[host].changed))

        # If the host failed -> print the failed configuration
        if task[host].failed:
            print(task_error(text=name, changed=task[host].changed))
            print(task[host][0].result)

        # If verbose is True -> print all results
        elif verbose:
            print(task_info(text=name, changed=task[host].changed))
            print(task[host][0].result)

        # If the host succeeded and verbose is False -> print info
        else:
            print(task_info(text=name, changed=task[host].changed))
            print("Saved config to startup-config successfully")

    # Return True if the task were successful
    if not task.failed:
        return True
    return False


def cfg_eem_replace_config(nr: Nornir, name: str, eem_name: str, file: str, verbose: bool = False) -> bool:
    """
    #### CODE REFACTORING NEEDED -> INTRODUCE print_result ####

    This function uses Scrapli send_configs to configure a EEM applet which replace the config from a
    specified file path. After this config will be executed to replace the configuration. It's basically a
    rollback function.
    """

    print_task_name(text=name)

    # Load day0 EEM applet config
    # fmt: off
    config_list = [
        f'event manager applet {eem_name}',
        'event none maxrun 60',
        'action 1.0 cli command "enable"',
        f'action 2.0 syslog msg "{eem_name} -> Started"',
        f'action 2.1 cli command "{eem_name} -> Started"',
        f'action 3.0 cli command "configure replace {file} force"',
        f'action 4.0 syslog msg "{eem_name} -> Finish"',
        f'action 4.1 cli command "{eem_name} -> Finish"',
    ]
    # fmt: on

    # Execute the EEM applet configuration. Run the standard Nornir Scrapli task send_configs
    task1 = nr.run(
        name=f"Scrapli configure EEM applet {eem_name}",
        task=send_configs,
        configs=config_list,
        strip_prompt=False,
        timeout_ops=180,
    )

    # Execute the EEM applet to replace the config. Run the standard Nornir Scrapli task send_configs
    task2 = nr.run(
        name=f"Scrapli execute EEM applet {eem_name}",
        task=send_commands,
        commands=[f"event manager run {eem_name}"],
        strip_prompt=False,
        timeout_ops=180,
    )

    # Wait some seconds to allow the EEM applet to replace the config
    # Tested on a C9300 with 1700 lines of config to replace -> needs arround 25s
    time.sleep(40)

    # Delete the EEM applet after it have been executed. Run the standard Nornir Scrapli task send_configs
    task3 = nr.run(
        name=f"Scrapli delete EEM applet {eem_name}",
        task=send_configs,
        configs=[f"no event manager applet {eem_name}"],
        strip_prompt=False,
        timeout_ops=180,
    )

    task1_msg = "Scrapli configure EEM applet"
    task2_msg = "Scrapli execute EEM applet"
    task3_msg = "Scrapli delete EEM applet"

    for host in task1:
        print(task_host(host=host, changed=task1[host].changed))

        # If the host failed -> print the failed configuration
        if task1[host].failed:
            print(task_error(text=task1_msg, changed=task1[host].changed))
            print(f"'Configure {eem_name}' -> CliResponse <Success: False>\n")
            print(task1[host][0].result)
            print(task_error(text=task2_msg, changed=False))
            print(f"'Execute {eem_name}' -> CliResponse <Success: False>\n")
            print(task2[host][0].result)
            print(task_error(text=task3_msg, changed=False))
            print(f"'Delete {eem_name}' -> CliResponse <Success: False>\n")
            print(task3[host][0].result)

        # If verbose is True -> print all results
        elif verbose:
            print(task_info(text=task1_msg, changed=task1[host].changed))
            print(f"'Configure {eem_name}' -> CliResponse <Success: True>\n")
            print(task1[host][0].result)
            print(task_info(text=task2_msg, changed=True))
            print(f"'Execute {eem_name}' -> CliResponse <Success: True>\n")
            print(task2[host][0].result)
            print(task_info(text=task3_msg, changed=True))
            print(f"'Delete {eem_name}' -> CliResponse <Success: True>\n")
            print(task3[host][0].result)

        # If the host succeeded and verbose is False -> print info
        else:
            print(task_info(text=task1_msg, changed=task1[host].changed))
            print(f"'Configure {eem_name}' -> CliResponse <Success: True>")
            print(task_info(text=task2_msg, changed=True))
            print(f"'Execute {eem_name}' -> CliResponse <Success: True>")
            print(task_info(text=task3_msg, changed=True))
            print(f"'Delete {eem_name}' -> CliResponse <Success: True>")

    # Return True if both tasks were successful
    if not (task1.failed and task2.failed):
        return True
    return False


def jinja2_generate_config(
    nr: Nornir, name: str, path: str, template: str, verbose: bool = False
) -> AggregatedResult:
    """
    #### CODE REFACTORING NEEDED -> INTRODUCE print_result ####

    This function runs the standard Nornir task template_file and generates a config for each host. If one or
    more hosts failed the function print a error std-out message and terminates the script. Only when all
    hosts were successful the Nornir AggregatedResult object will be returned
    """
    print_task_name(text=name)

    # Run the Nornir Task template_file
    j2_config = nr.run(task=template_file_custom, task_msg=name, template=template, path=path)

    for host in j2_config:
        print(task_host(host=host, changed=False))

        if j2_config[host].failed:
            # If the subtask failed print its exception
            if j2_config[host].result.startswith("Subtask:"):
                print(task_error(text=name, changed=False))

                # If the Jinja2 template is not found by the template_file task
                if "TemplateNotFound" in j2_config[host][1].result:
                    file = j2_config[host][1].exception
                    print(f"Jinja2 template '{file}' not found")

                # If the Jinja2 templating rendering catches another exception
                else:
                    print(j2_config[host][1].result)

            # If the task fails print the returned result
            elif j2_config[host].failed:
                print(j2_config[host].result)

        # If no condition matched the task was successful
        else:
            print(task_info(text="Jinja2 template file", changed=False))
            # Read the template filename from the Nornir inventory
            file = nr.inventory.hosts[host][template]
            print(f"Jinja2 template '{file}' rendered successfully")

            if verbose:
                print(f"\n{j2_config[host][1].result}")

    if j2_config.failed_hosts:
        # If one or more of the Jinja2 template tasks failed
        print("\n")
        print(task_error(text=name, changed=False))
        print("\U0001f4a5 ALERT: JINJA2 CONFIG TEMPLATING FAILED! \U0001f4a5")
        print(
            f"\n{Style.BRIGHT}{Fore.RED}"
            "-> Analyse the Nornir output for failed Jinja2 tasks\n"
            "-> May apply Nornir inventory changes and run the script again\n\n"
            "No config changes has been made yet!\n"
        )
        # Terminate the script with successful exit code 0
        sys.exit(1)

    # If the task was successful return its result object
    return j2_config


def cfg_jinja2_config(nr: Nornir, name: str, jinja2_result: AggregatedResult, verbose: bool = False) -> bool:
    """
    #### CODE REFACTORING NEEDED -> INTRODUCE print_result ####

    This function takes a Nornir AggregatedResult object which contains the configuration that should be
    applied to each device. It can continue with the result of the function jinja2_generate_config to apply a
    Jinja2 config to devices and prints the result is the Nornir style.
    """

    print_task_name(text=name)

    # Run the custom nornir task scrapli_apply_jinja2_config
    task = nr.run(task=scrapli_apply_jinja2_config, jinja2_result_obj=jinja2_result, on_failed=True)

    for host in task:
        print(task_host(host=host, changed=task[host].changed))

        # If the host failed -> print the failed configuration
        if task[host].failed:
            print(task_error(text=name, changed=task[host].changed))

            # If verbose is True -> print all results
            if verbose:
                print(task[host][1].result)

            # If verbose is False -> print only failed results
            else:
                lines = task[host][1].result.splitlines()
                for index, line in enumerate(lines):
                    if "'^'" in line:
                        print(lines[index - 3])
                        print(lines[index - 2])
                        print(lines[index - 1])
                        print(line)

        # If the host succeeded and verbose is False -> print info
        else:
            print(task_info(text=name, changed=task[host].changed))

            # If verbose is True -> print all results
            if verbose:
                print(task[host][1].result)
            else:
                print("Configuration successful")

    return not task.failed


def cfg_multiline_banner(nr: Nornir, name: str, multiline_banner: str, verbose: bool = False) -> bool:
    """
    #### CODE REFACTORING NEEDED -> INTRODUCE print_result ####

    This function takes a multiline string as variable multiline_banner and configures this banner with the
    help of Scrapli eager=True option. Because the banner "input mode" is basically like a text editor where
    we dont get the prompt printed out between sending lines of banner config we need to use the 'eager' mode
    to force scrapli to blindly send the banner/macro lines without looking for the prompt in between each
    line. You should *not* use eager unless you need to and know what you are doing as it basically disables
    one of the core features that makes scrapli reliable!
    """

    print_task_name(text=name)

    # Run the standard nornir task send_config
    task = nr.run(
        task=send_config,
        config=multiline_banner,
        strip_prompt=False,
        eager=True,
        on_failed=True,
        timeout_ops=180,
    )

    for host in task:
        print(task_host(host=host, changed=task[host].changed))

        # If the host failed -> print the failed configuration
        if task[host].failed:
            print(task_error(text=name, changed=task[host].changed))
            print(task[host][0].result)

        # If verbose is True -> print all results
        elif verbose:
            print(task_info(text=name, changed=task[host].changed))
            print(task[host][0].result)

        # If the host succeeded and verbose is False -> print info
        else:
            print(task_info(text=name, changed=task[host].changed))
            print("Configured multi-line banner successfully")

    # Return True if both tasks were successful
    if not task.failed:
        return True
    return False


def cfg_tpl_int_cli(nr: Nornir, name: str, verbose: bool = False) -> bool:
    """
    #### CODE REFACTORING NEEDED -> INTRODUCE print_result ####

    This function takes a Nornir object and a filter tag to execute all tasks within this function on the
    given inventory subset. Each interface group will be configured by Scrapli.
    """

    # Set the variable to return at the end of the function to True
    cfg_status = True

    # Gather the tpl_int template groups from all hosts
    result = nr.run(task=create_tpl_int_list)

    # Create a union of the results from all hosts -> no duplicate items
    tpl_int_groups = []
    for host in result:
        tpl_int_groups = list(set().union(tpl_int_groups, result[host].result))

    for group in tpl_int_groups:
        print_task_name(text=f"{name} {group}")

        # Run the custom nornir task scrapli_replace_tpl_int_config
        task = nr.run(task=scrapli_replace_tpl_int_config, tpl_int_group=group, on_failed=True)

        for host, multi_result in task.items():
            print(task_host(host=host, changed=task[host].changed))

            for result in multi_result:
                # Nornir result is None and therefor also the Scrapli result is None. If the result starts
                # with Subtask and configuration error has occured and the parent task error won't be printed
                if (result.result is None) or result.result.startswith("Subtask:"):
                    continue

                # Get the attribute scrapli_response from result into a variable. Return None if the attribute
                # scrapli_response is not existing
                scrapli_multi_result = getattr(result, "scrapli_response", None)

                # If the scrapli_multi_result is None but the result.result is present this means an TypeError
                # or KeyError handled inside the task is present
                if scrapli_multi_result is None:
                    print(task_info(text=result.name, changed=result.changed))
                    print(result.result)
                    continue

                # Find the interface from the Scrapli result
                for scrapli_result in scrapli_multi_result:
                    if scrapli_result.channel_input.startswith("interface"):
                        interface = scrapli_result.channel_input
                        # Remove the word interface and leading whitespaces
                        interface = interface.replace("interface", "").lstrip()

                # Print the result for a failed task
                if result.failed:
                    print(task_error(text=result.name, changed=result.changed))
                    print(f"{interface} -> {scrapli_multi_result}")
                    print(result.result)
                    cfg_status = False

                # Print the result for a successful task
                else:
                    print(task_info(text=result.name, changed=result.changed))
                    print(f"{interface} -> {scrapli_multi_result}")
                    if verbose:
                        # Print the whole CLI result
                        print(result.result)

    return cfg_status
