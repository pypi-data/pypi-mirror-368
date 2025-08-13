#!/usr/bin/env python3
"""
This module contains functions regarding Nornir run with Processor.

The functions are ordered as followed:
- Nornir Processor Task in Functions
- Nornir Processor Print Functions
"""

from colorama import Style, init
from beautifultable import BeautifulTable
from nornir.core import Nornir
from nornir.core.task import AggregatedResult
from nornir_salt.plugins.processors import TestsProcessor
from nornir_salt.plugins.tasks import scrapli_send_commands
from nornir_collection.utils import (
    print_task_name,
    task_host,
    task_info,
    task_result,
    list_flatten,
    load_multiple_yaml_files_to_string,
    nr_filter_by_role_and_tag,
    print_result,
)

init(autoreset=True, strip=False)


#### Nornir Processor Task in Functions #####################################################################


def nr_testsprocessor(nr: Nornir, name: str, inv_key: str, role: str = None, tags: list[str] = None) -> bool:
    """
    This function filters the Nornir object by the string of the argument filter_tag and searches all values
    of the Nornir inventory which starts with the string of the argument inv_key. These values can be a
    string or a list of strings which are the TestProcessor test suite yaml files.
    As Nornir with processors works on the nr object level and not on the task level, it have to be ensured
    that all filtered hosts have access to all files or the TestsProcessor task will fail.
    The test suite yaml file supports all NornirSalt TestsProcessor values including Jinja2 host templating.
    """

    task_text = f"NORNIR prepare TestsProcessor '{name}'"
    print_task_name(task_text)

    # If filter_tag is True, filter the inventory based on the string from the argument filter_tag
    # If the filteres object have no hosts, exit with a error message
    if role or tags:
        nr = nr_filter_by_role_and_tag(nr=nr, role=role, tags=tags, silent=False)

    # Create a list with the values of all inventory keys starting with a specific string
    file_list = []
    for host in nr.inventory.hosts.values():
        file_list += [value for key, value in host.items() if key.startswith(inv_key)]

    # Flatten the file_list if it contains lists of lists
    file_list = list_flatten(file_list)
    # Create a union of the files in the file_list -> no duplicate items
    file_list = list(set().union(file_list))

    # Load the test suite yaml files from file_list as one string to render jinja2 host inventory data
    yaml_string = load_multiple_yaml_files_to_string(file_list=file_list, silent=False)
    # Return False if the yaml_string is empty
    if not yaml_string:
        return False

    task_text = f"NORNIR run TestsProcessor '{name}'"
    print_task_name(task_text)

    # Add the nornir salt TestsProcessor processor
    # TestsProcessor expects a list, therefor each yaml string needs to be packed into a list
    # TestsProcessor templates the yaml string with Jinja2 and loads the yaml string into a dict
    nr_with_testsprocessor = nr.with_processors(
        [TestsProcessor(tests=[yaml_string], build_per_host_tests=True)]
    )

    # Collect output from the devices using scrapli send_commands task plugin
    try:
        results = nr_with_testsprocessor.run(task=scrapli_send_commands, on_failed=True)
    except ValueError:
        print(task_info(text=task_text, changed=False))
        print(f"'{task_text}' -> NornirResponse <Success: True>")
        print("-> Test files have no tests or are empty")
        return True

    # Print the TestsProcessor results
    cfg_status = print_testsprocessor_results(nr_result=results, name=name)

    return cfg_status


#### Print Functions ########################################################################################


def print_testsprocessor_results(nr_result: AggregatedResult, name: str) -> None:
    """
    This function prints a NornirSalt TestsProcessor result in a nice table with the library rich
    """
    # Track if the overall task has failed
    cfg_status = True

    # Print for each host a table with the Nornir testsprocessor result
    for host, multiresult in nr_result.items():
        # Print the host
        print(task_host(host=str(host), changed=False))
        # Print the overal TestsProcessor task result as INFO is all tests are successful, else ERROR
        level_name = "INFO" if all("PASS" in result.result for result in multiresult) else "ERROR"
        print(task_result(text=f"NORNIR run TestsProcessor '{name}'", changed=False, level_name=level_name))
        # Update the overall task status if the level name if ERROR
        if level_name == "ERROR":
            cfg_status = False

        try:
            # Create a table with the Python library beautifultable
            table = BeautifulTable()
            table.set_style(BeautifulTable.STYLE_NONE)
            table.columns.width = [50, 25, 10]
            table.columns.header = [
                f"{Style.BRIGHT}Name / Task",
                f"{Style.BRIGHT}Criteria / Test",
                f"{Style.BRIGHT}Result",
            ]
            # Create a custom table styling
            table.columns.header.separator = "-"
            table.columns.separator = "|"
            table.rows.separator = "-"
            table.columns.alignment = BeautifulTable.ALIGN_LEFT
            # Add a row for each test result
            for result in multiresult:
                # Expression test using evan have an empty criteria in the Nornir result
                if result.criteria:
                    criteria = f"{Style.DIM}\x1b[3m({result.test})\n{result.criteria}"
                else:
                    criteria = f"{Style.DIM}\x1b[3mCritera not available\n"
                    criteria += f"{Style.DIM}\x1b[3mfor this test"
                table.rows.append(
                    [
                        f"{Style.DIM}\x1b[3m({result.task})\n{result.name}",
                        f"{criteria}",
                        f"{result.result} ✅" if result.result == "PASS" else f"{result.result} ❌",
                    ]
                )
            # Print the TestProcessor result as beautifultable
            print(f"\n{table}")
        except:  # noqa: E722
            # Print the Nornir result to stdout
            print_result(multiresult)

    # Return a config status boolian True if all tests were successful or False if not
    return cfg_status
