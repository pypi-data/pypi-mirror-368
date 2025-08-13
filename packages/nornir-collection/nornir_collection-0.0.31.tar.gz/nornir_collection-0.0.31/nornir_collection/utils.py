#!/usr/bin/env python3
"""
This module contains general functions and tasks related to Nornir.

The functions are ordered as followed:
- Helper Functions
- Nornir print functions
- Nornir Helper Tasks
- Nornir print_result deviation
"""

import os
import sys
import argparse
import json
import hashlib
import logging
import pprint
import threading
import urllib
import operator
from functools import reduce
from typing import Generator, Tuple, List, NoReturn, Union
from collections import OrderedDict
from datetime import datetime
import yaml
import __main__
from colorama import Fore, Style, init
from pyfiglet import figlet_format
from pandas import DataFrame
from nornir.core import Nornir
from nornir.core.filter import F
from nornir.core.task import AggregatedResult, MultiResult, Result
from nornir_salt.plugins.functions import FFun


init(autoreset=True, strip=False)

#### Helper Functions ########################################################################################


class CustomArgParse(argparse.ArgumentParser):
    """
    This class takes the argparse.ArgumentParser function as a superclass and overwrites the argparse error
    function. Every time that argparse calls the error function the following error function will be executed.
    """

    def error(self, message):
        """
        This function overwrites the standard argparse error function
        """
        print(task_error(text="ARGPARSE verify arguments", changed=False))
        print("'ARGPARSE verify arguments' -> ArgparseResponse <Success: False>\n")
        print(f"error: {message}\n")
        self.print_help()
        print("\n")
        sys.exit(1)


class CustomArgParseWidthFormatter(argparse.RawTextHelpFormatter):
    """
    This class can be specified as formatter_class argument in argparse.ArgumentParser. This solution is
    preferred as formatter_class argument expects to use a class, not a class instance.
    """

    def __init__(self, prog) -> None:
        super().__init__(prog, width=100)


def get_env_vars(envs: List[str], task_text: str) -> Tuple:
    """
    This function loads the environment variables from a list and returns them as a Tuple. If an environment
    variable is not found, the script will exit with an error message.
    """
    # Initialize an empty dictionary
    env_vars = {}

    try:
        # Load the environment variables from the list
        for env in envs:
            env_vars[env] = os.environ[env]

    except KeyError as error:
        # Print the error message and exit the script
        print(task_error(text=task_text, changed=False))
        print(f"'Load environment variable {error}' -> OS.EnvironResponse <Success: False>")
        print(f"-> Environment variable {error} not found\n")
        sys.exit(1)

    # Return the environment variables as a dictionary
    return env_vars


def get_dict_value_by_path(data_dict, map_list):
    """
    Access a nested object in data_dict by map_list sequence.
    """
    return reduce(operator.getitem, map_list, data_dict)


def set_dict_value_by_path(data_dict, map_list, value):
    """
    Set a value in a nested object in data_dict by map_list sequence.
    """
    get_dict_value_by_path(data_dict, map_list[:-1])[map_list[-1]] = value


def del_dict_key_value_by_path(data_dict, map_list):
    """
    Delete a key-value in a nested object in data_dict by map_list sequence.
    """
    del get_dict_value_by_path(data_dict, map_list[:-1])[map_list[-1]]


def get_rel_path_from_cwd(path):
    """
    TBD
    """
    # Compute the absolute path if path is a relative path
    if not os.path.isabs(path):
        path = os.path.join(os.path.abspath(os.path.dirname(__main__.__file__)), path)

    # Get the relative path from the current working directory to to the end of the absolute path
    relative_path_from_cwd = os.path.relpath(path, os.getcwd())

    return relative_path_from_cwd


def load_multiple_yaml_files_to_string(file_list: list, silent: bool = False) -> str:
    """
    This function loads multiple yaml files into a string
    """

    task_text = "Load multiple yaml files to string"
    yaml_string = str()

    # Exit the function if the file_list is empty
    if not file_list:
        print(task_error(text=task_text, changed=False))
        print(f"'{task_text}' -> NornirResponse <Success: False>")
        print("-> No files provided for yaml string loading ('file_list' is empty)")
        return yaml_string

    # Load the yaml files from file_list and concatinate them to one string
    # TestsProcessor templates the yaml string with Jinja2 and loads the yaml string into a dict
    try:
        for file in file_list:
            with open(file, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    yaml_string += line if "---" not in line else ""
                yaml_string += "\n"

        if not silent:
            print(task_info(text=task_text, changed=False))
            print(f"'{task_text}' -> NornirResponse <Success: True>")
            for file in file_list:
                print(f"-> {file}")

    except FileNotFoundError as error:
        print(task_error(text=task_text, changed=False))
        print(f"'{task_text}' -> NornirResponse <Success: False>")
        print(f"-> {error}")

    return yaml_string


def load_yaml_file(file: str, text: str = False, silent: bool = False, verbose: bool = False):
    """
    Load the yaml file into a variable.
    """
    text = text if text else "YAML Load File"
    success_message = (
        f"{task_name(text=text)}\n"
        f"{task_info(text=text, changed=False)}\n"
        f"'{text}' -> PythonResult <Success: True>"
    )
    error_message = (
        f"{task_name(text=text)}\n"
        f"{task_error(text=text, changed=False)}\n"
        f"'{text}' -> PythonResult <Success: False>"
    )

    try:
        with open(file, "r", encoding="utf-8") as stream:
            yaml_dict = yaml.safe_load(stream)

        if not silent:
            print(success_message)
            print(f"-> Loaded YAML file: {file}")
            if verbose:
                print("\n" + json.dumps(yaml_dict, indent=4))

        # Return the loaded yaml file as python dictionary
        return yaml_dict

    except (TypeError, FileNotFoundError, yaml.parser.ParserError) as yaml_error:
        print(error_message)
        print(f"\n{yaml_error}")

    # Return an empty python dictionary
    return {}


def construct_filename_with_current_date(filename: str, name: Union[str, None], silent: bool = False) -> str:
    """
    Construct the new path and filename from the filename argument string variable. The current date will be
    added at the end of the filename. The function returns the new constructed filename.
    """
    # Set a custom name for stdout print if name is set
    name = name if name else "PYTHON construct file path with current date"

    # Create some variables to construct the destination path and filename
    # Get the path and the filename from file variable string
    path, filename = os.path.split(filename)

    # Create the path folder if it don't exists
    if not os.path.exists(path):
        os.makedirs(path)

    # Get the filename and the extension from the filename variable
    filename, file_extension = os.path.splitext(filename)

    # Destination filename with current date time in format YYYY-mm-dd
    filename = f"{path}/{filename}_{datetime.today().date()}{file_extension}"

    if not silent:
        print_task_name(text=name)
        print(task_info(text=name, changed=False))
        print(f"'{name}' -> PythonResult <Success: True>")
        print(f"-> Constructed {filename}")

    return filename


def get_pandas_column_width(df: DataFrame) -> List[int]:
    """
    Helper function to get the width of each pandas dataframe column.
    """
    # Find the maximum length of the index column
    idx_max = max([len(str(s)) for s in df.index.values] + [len(str(df.index.name))])

    # Concatenate this to the max of the lengths of column name and its values for each column, left to right
    return [idx_max] + [max([len(str(s)) for s in df[col].values] + [len(col)]) for col in df.columns]


def list_flatten(original_list: list) -> list:
    """
    This function creates with recursion a flat list from a list of lists and strings or other data types.
    """
    new_list = []
    for item in original_list:
        if isinstance(item, list):
            new_list.extend(list_flatten(item))
        else:
            new_list.append(item)

    return new_list


def compute_hash(source: str, algorithm: str = "md5") -> str:
    """
    This is a helper function which takes a file path or a http url as argument and computes a md5 hash which
    is the return of the function. Additionally the default hash algorithm can be changed from md5 to sha1,
    sha265, sha384 or sha512.
    """
    # Use mapping with lambda to avoid long if elif else statements
    algorithms = {
        "md5": hashlib.md5,  # nosec
        "sha1": hashlib.sha1,  # nosec
        "sha256": hashlib.sha256,  # nosec
        "sha384": hashlib.sha384,  # nosec
        "sha512": hashlib.sha512,  # nosec
    }
    # Execute the correct lambda hash function by the dictionary key which matches the algorithm argument
    hash_obj = algorithms[algorithm]()

    if source.lower().startswith("http"):
        # Bandit "B310: urllib_urlopen" if solved to raise a ValueError is the value starts not with http
        if source.lower().startswith("http"):
            response = urllib.request.Request(source)
            with urllib.request.urlopen(response) as response:  # nosec
                for chunk in iter(lambda: response.read(4096), b""):
                    hash_obj.update(chunk)
        else:
            raise ValueError from None
    else:
        with open(source, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_obj.update(chunk)

    return hash_obj.hexdigest()


def iterate_all(iterable: Union[list, dict], returned: str = "key") -> Generator:
    """Returns an iterator that returns all keys or values of a (nested) iterable.
    Arguments:
        - iterable: <list> or <dictionary>
        - returned: <string> "key" or "value" or <tuple of strings> "key-value"
    Returns:
        - <Generator>
    """
    if isinstance(iterable, dict):
        for key, value in iterable.items():
            if returned == "key":
                yield key
            elif returned == "value":
                if not isinstance(value, dict) or isinstance(value, list):
                    yield value
            elif returned == "key-value":
                if not isinstance(value, dict) or isinstance(value, list):
                    yield key, value
            else:
                raise ValueError("'returned' keyword only accepts 'key' or 'value' or 'key-value'.")
            for ret in iterate_all(value, returned=returned):
                yield ret
    elif isinstance(iterable, list):
        for item in iterable:
            for ret in iterate_all(item, returned=returned):
                yield ret


def transform_env(iterable: dict, startswith: str = "env_") -> dict:
    """
    This function loops over a nested dictionary and if the key startswith the specific string and the value
    is a string, it loads the environment variable specified by the value and replace the value with the
    environment variable.
    """
    for key, value in iterable.copy().items():
        # If Value == DICT -> Continue with nested dict
        if isinstance(value, dict):
            iterable[key] = transform_env(value, startswith)
        # If Value == LIST -> Replace the value of each list item with the env variable
        elif isinstance(value, list):
            if key.startswith(startswith):
                for index, item in enumerate(value.copy()):
                    iterable[key][index] = os.environ[item]
        # If Value == STR -> Replace the value with the env variable
        elif isinstance(value, str):
            if key.startswith(startswith):
                iterable[key] = os.environ[value]

    return iterable


#### Nornir Helper Functions #################################################################################


def nr_filter_by_role_and_tag(
    nr: Nornir, task_text: str = None, role: str = None, tags: list[str] = None, silent: bool = False
):
    """
    TBD
    """

    if not task_text:
        task_text = "NORNIR filter inventory"
    provided_filters = ""

    if role:
        # Filter by device role (A device can have only one role)
        nr = nr.filter(F(role__slug__contains=role))
        provided_filters += f"-> Provided role: '{role}'\n"

    if tags:
        # Loop over all provided tags and filter by each tag
        for tag in tags:
            nr = nr.filter(F(tags__contains=tag))
        provided_filters += f"-> Provided tags: {tags}\n"

    # If the filteres object have no hosts, exit with a error message
    if not nr.inventory.hosts.keys():
        print(task_error(text=task_text, changed=False))
        print(f"'{task_text} by role and/or tags' -> NornirResult <Success: False>")
        exit_error(
            task_text=task_text,
            text="ALERT: NO HOST WITH ROLE AND/OR TAGS IN NORNIR INVENTORY",
            msg=[
                "-> Analyse the Nornir inventory and filter for a role and/or tags assigned to hosts",
                f"{provided_filters}",
            ],
        )

    if not silent:
        print(task_info(text=task_text, changed=False))
        print(
            f"'{task_text} by role and/or tags' -> NornirResult <Success: True>\n" + f"{provided_filters}",
        )

    return nr


def nr_filter_by_hosts(nr: Nornir, hosts: Union[str, list], task_text: str = None, silent: bool = False):
    """
    TBD
    """

    if not task_text:
        task_text = "NORNIR filter inventory"

    if isinstance(hosts, str):
        # Create a list from the comma separated hosts argument
        hosts = hosts.split(",")

    # Use NornirSalt FFun Filter-List option to filter on a list of hosts
    nr_filtered = FFun(nr, FL=hosts)

    # Create a list with all filtered Nornir hosts for verification
    nr_hosts = list(nr_filtered.inventory.hosts.keys())

    # Verify that each host in from the hosts argument is part of the filtered Nornir inventory, else
    # the diff host will be in the list host_diff list
    host_diff = [host for host in hosts if host not in nr_hosts]
    if host_diff:
        print(task_error(text=task_text, changed=False))
        print(f"'{task_text} by hosts' -> NornirResponse <Success: False>")
        for host in host_diff:
            print(f"-> {host}")
        exit_error(
            task_text=task_text,
            text="ALERT: ONE OR MORE HOSTS ARE NOT PART OF THE NORNIR INVENTORY",
            msg="-> Analyse the Nornir inventory and filter for an existing host",
        )

    if not silent:
        print(task_info(text=task_text, changed=False))
        print(f"'{task_text} by hosts' -> NornirResponse <Success: True>")
        for host in nr_hosts:
            print(f"-> {host}")

    return nr_filtered


def nr_filter_args(nr: Nornir, args: argparse.Namespace, silent: bool = False) -> Nornir:
    """
    This function filters the Nornir inventory with a tag or a host argument provided by argparse. Prior
    Argparse validation needs to ensure that only one argument is present and that the tag or host argument
    creates a correct inventory filtering will be verified. The new filtered Nornir object will be returned
    or the script terminates with an error message.
    """
    if not silent:
        task_text = "NORNIR filter inventory"
        print_task_name(task_text)

    # If the --hosts argument is set, verify that the host exist
    if hasattr(args, "hosts"):
        nr = nr_filter_by_hosts(nr=nr, hosts=args.hosts, silent=silent)

        return nr

    # If the --role and/or --tags argument is set, verify that the tag has hosts assigned to
    if hasattr(args, "role") or hasattr(args, "tags"):
        role = args.role if hasattr(args, "role") else None
        tags = args.tags.split(",") if hasattr(args, "tags") else None
        nr = nr_filter_by_role_and_tag(nr=nr, role=role, tags=tags, silent=silent)

        return nr

    exit_error(
        task_text=task_text,
        text="ALERT: NOT SUPPORTET ARGPARSE ARGUMENT FOR NORNIR INVENTORY FILTERING!",
        msg="-> Analyse the python function for missing Argparse filtering",
    )


def nr_filter_inventory_from_host_list(nr: Nornir, filter_reason: str, host_list: List[str]) -> Nornir:
    """
    This function takes a Nornir object, a filter reason to print in Nornir style to std-out and a list of
    hosts. It can be a list of hosts or a list of strings where the hostname is part of the string, as the
    function checks if the hostname from the Nornir object is in that host list or list of strings. Every host
    that matches will be added to the new filter target and the new filtered Nornir object will be returned.
    """

    task_text = "NORNIR re-filter inventory"
    print_task_name(task_text)

    # Re-filter the Nornir inventory only on hosts that need to be reconfigured.
    # Create an empty list to fill with all hosts that need reconfiguration.
    filter_target = []

    # Iterate over all diff files and add the host to the filter_target list if the Nornir inventory host is
    # in the diff file name
    for item in host_list:
        for host in nr.inventory.hosts.keys():
            if host == item:
                filter_target.append(host)
                break

    # Remove possible duplicate hosts in the list
    filter_target = list(set(filter_target))

    # Use Nornir-Salt FFun Filter-List option to filter on a list of hosts
    nr = FFun(nr, FL=filter_target)

    print(task_info(text=task_text, changed=False))
    print(f"'{task_text} for hosts' -> NornirResponse <Success: True>")
    print(f"{filter_reason}")
    for host in nr.inventory.hosts.keys():
        print(f"-> {host}")

    return nr


#### Nornir Print Functions ##################################################################################


def print_script_banner(title: str, font: str = "small", text: str = None) -> None:
    """
    Print a custom script banner with pyfiglet.
    """
    banner = figlet_format(title, font, width=110)
    print("\n")
    for line in banner.splitlines():  # Workaround to print in Azure DevOps all lines in color
        print(f"{Style.BRIGHT}{Fore.GREEN}{line}")
    if text:
        print(f"{Style.BRIGHT}{Fore.GREEN}{text}")


def print_task_title(title: str) -> None:
    """
    Prints a Nornir style title.
    """
    msg = f"**** {title} "
    print(f"\n{Style.BRIGHT}{Fore.GREEN}{msg}{'*' * (90 - len(msg))}{Fore.RESET}{Style.RESET_ALL}")


def print_task_name(text: str) -> None:
    """
    Prints a Nornir style host task title.
    """
    msg = f"{text} "
    print(f"\n{Style.BRIGHT}{Fore.CYAN}{msg}{'*' * (90 - len(msg))}{Fore.RESET}{Style.RESET_ALL}")


def task_name(text: str) -> None:
    """
    Prints a Nornir style host task title.
    """
    msg = f"{text} "
    return f"\n{Style.BRIGHT}{Fore.CYAN}{msg}{'*' * (90 - len(msg))}{Fore.RESET}{Style.RESET_ALL}"


def task_host(host: str, changed: bool) -> str:
    """
    Returns a Nornir style host task name.
    """
    msg = f"* {host} ** changed : {str(changed)} "
    return f"{Style.BRIGHT}{Fore.BLUE}{msg}{'*' * (90 - len(msg))}{Fore.RESET}{Style.RESET_ALL}"


def task_result(text: str, changed: bool, level_name, failed: bool = False) -> str:
    """
    Returns a Nornir style task info or error message based on the arguments.
    This function should be the successor of task_info and task_error.
    """
    if failed or level_name == "ERROR":
        color = Fore.RED
    elif changed:
        color = Fore.YELLOW
    else:
        color = Fore.GREEN

    msg = f"---- {text} ** changed : {str(changed)} "
    return f"{Style.BRIGHT}{color}{msg}{'-' * (90 - len(msg))} {level_name}{Fore.RESET}{Style.RESET_ALL}"


def task_info(text: str, changed: bool) -> str:
    """
    Returns a Nornir style task info message.
    """
    color = Fore.YELLOW if changed else Fore.GREEN
    msg = f"---- {text} ** changed : {str(changed)} "
    return f"{Style.BRIGHT}{color}{msg}{'-' * (90 - len(msg))} INFO{Fore.RESET}{Style.RESET_ALL}"


def task_error(text: str, changed: bool) -> str:
    """
    Returns a Nornir style task error message.
    """
    msg = f"---- {text} ** changed : {str(changed)} "
    return f"{Style.BRIGHT}{Fore.RED}{msg}{'-' * (90 - len(msg))} ERROR{Fore.RESET}{Style.RESET_ALL}"


def exit_info(
    task_text: str, text: str = False, msg: Union[list[str], str] = False, changed: bool = False
) -> NoReturn:
    """
    TBD
    """
    # Set text to task_text if text if False
    text = text if text else task_text

    # Print the info and exit the script with exit code 0
    print(task_info(text=task_text, changed=changed))
    print(f"\u2728 {text.upper()} \u2728")
    if isinstance(msg, list):
        for line in msg:
            print(f"{Style.BRIGHT}{Fore.GREEN}{line}")
    elif isinstance(msg, str):
        print(f"{Style.BRIGHT}{Fore.GREEN}{msg}")
    print("\n")
    sys.exit(0)


def exit_error(task_text: str, text: str = False, msg: Union[list[str], str, None] = "default") -> NoReturn:
    """
    TBD
    """
    # Set text to task_text if text if False
    text = text if text else task_text

    # Print the error and exit the script with exit code 1
    print(task_error(text=task_text, changed=False))
    print(f"\U0001f4a5 {text.upper()} \U0001f4a5")
    if isinstance(msg, list):
        for line in msg:
            print(f"{Style.BRIGHT}{Fore.RED}{line}")
    elif isinstance(msg, str) and "default" not in msg:
        print(f"{Style.BRIGHT}{Fore.RED}{msg}")
    elif "default" in msg:
        print(
            f"{Style.BRIGHT}{Fore.RED}-> Analyse the Nornir output for failed task results\n"
            "-> May apply Nornir inventory changes and run the script again"
        )
    print("\n")
    sys.exit(1)


#### Nornir print_result Deviation ###########################################################################


def _print_individual_result(
    result: Result, result_sub_list: bool, attrs: List[str], failed: bool, severity_level: int
) -> None:
    """
    This function is part of the deviation of the official Nornir print_result function.
    """

    if result.severity_level < severity_level:
        return

    # Get the task level INFO or ERROR, the colorama color and the changed boolian
    level_name = logging.getLevelName(result.severity_level)
    changed = "" if result.changed is None else result.changed

    for attribute in attrs:
        item = getattr(result, attribute, "")
        if isinstance(item, BaseException):
            # Deviation to print the nornir_collection task_result function
            print(task_result(text=result.name, changed=changed, level_name=level_name, failed=failed))
            # for consistency between py3.6 and py3.7
            print(f"{item.__class__.__name__}{item.args}")

        # Deviation to print the nornir_collection task_result function
        elif item and result_sub_list and isinstance(item, list):
            for list_item in item:
                print(list_item)

        elif item and not isinstance(item, str):
            if isinstance(item, OrderedDict):
                # Deviation to print the nornir_collection task_result function
                print(task_result(text=result.name, changed=changed, level_name=level_name, failed=failed))
                print(json.dumps(item, indent=4))
            else:
                # Deviation to print the nornir_collection task_result function
                print(task_result(text=result.name, changed=changed, level_name=level_name, failed=failed))
                pprint.pprint(item, indent=4)
        elif item:
            # Deviation to print the nornir_collection task_result function
            print(task_result(text=result.name, changed=changed, level_name=level_name, failed=failed))
            print(item)


def _print_result(
    result: Result,
    result_sub_list: bool = False,
    attrs: List[str] = None,
    failed: bool = False,
    severity_level: int = logging.INFO,
) -> None:
    """
    This function is part of the deviation of the official Nornir print_result function.
    """

    # If attrs is not None use attrs else use the list below
    attrs = attrs or ["diff", "result", "stdout"]
    if isinstance(attrs, str):
        attrs = [attrs]

    if isinstance(result, AggregatedResult):
        # Deviation to print the nornir_collection print_task_name function
        print_task_name(text=result.name)

        for host, host_data in sorted(result.items()):
            changed = "" if host_data.changed is None else host_data.changed
            # Deviation to print the nornir_collection task_host function
            print(task_host(host=host, changed=changed))
            # Recursion to print all MultiResult objects of the Nornir AggregatedResult object
            _print_result(host_data, result_sub_list, attrs, failed, severity_level)

    elif isinstance(result, MultiResult):
        # Deviation to not print the task MultiResult or Subtask failed result
        if not (str(result[0]).startswith("MultiResult") or str(result[0]).startswith("Subtask")):
            _print_individual_result(result[0], result_sub_list, attrs, failed, severity_level)
        # Recursion to print all results of the Nornir MultiResult object
        for result_item in result[1:]:
            _print_result(result_item, result_sub_list, attrs, failed, severity_level)

    elif isinstance(result, Result):
        # Print the Nornir Result object
        _print_individual_result(result, result_sub_list, attrs, failed, severity_level)


def print_result(
    result: Result,
    result_sub_list: bool = False,
    attrs: List[str] = None,
    failed: bool = False,
    severity_level: int = logging.INFO,
) -> None:
    """
    This function is a deviation of the official Nornir print_result function.
    Prints an object of type `nornir.core.task.Result`
    Arguments:
      result: from a previous task
      attrs: Which attributes you want to print
      failed: if ``True`` assume the task failed
      severity_level: Print only errors with this severity level or higher
    """

    lock = threading.Lock()
    lock.acquire()
    try:
        _print_result(result, result_sub_list, attrs, failed, severity_level)
    finally:
        lock.release()
