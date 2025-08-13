#!/usr/bin/env python3
"""
This module contains general functions and tasks related to Batfish.

The functions are ordered as followed:
- Batfish Initialize Function
- Batfish Helper Functions
"""

import logging
from io import StringIO
from typing import Literal
import requests
from pybatfish.client.session import Session
from pandas import DataFrame
from nornir.core.task import Task, AggregatedResult
from nornir_collection.utils import print_task_name, task_result, task_error, task_info, exit_error


#### Batfish Initialize Function #############################################################################


def init_batfish(bf_data: tuple, bf_log_lvl: Literal["WARN", "ERROR"] = "ERROR") -> Session:
    """
    TBD
    """

    # Extract the variables from the bf_data tuple
    bf_host, bf_network, SNAPSHOT_DIR, SNAPSHOT_NAME = bf_data

    task_text = "BATFISH initialize snapshot"
    print_task_name(task_text)

    # Replace logging.WARN with the preferred logging level
    logging_lvl = logging.WARN if bf_log_lvl == "WARN" else logging.ERROR
    logging.getLogger("pybatfish").setLevel(logging_lvl)  # Or WARN for more details

    try:
        # Connect to the batfish service docker container
        bf = Session(host=bf_host)
        # Set batfish network logical name
        bf.set_network(bf_network)
        # Initialize a snapshot
        bf.init_snapshot(SNAPSHOT_DIR, name=SNAPSHOT_NAME, overwrite=True)

    except requests.exceptions.ConnectionError as error:
        print(task_error(text=task_text, changed=False))
        print(f"'{task_text}' -> BatfishResponse <Success: False>")
        print(f"-> {error}")
        # Exit the script with a proper message
        exit_error(
            task_text=task_text,
            text=f"ALERT: {task_text.upper()} FAILED!",
            msg="-> Analyse the Batfish docker container and snapshot settings to identify the root cause",
        )

    # Print the result as successful
    print(task_info(text=task_text, changed=False))
    print(f"'{task_text}' -> BatfishResponse <Success: True>")
    print(f"-> Snapshot dir: {SNAPSHOT_DIR} / Snapshot name: {SNAPSHOT_NAME}")

    return bf


#### Batfish Helper Functions ################################################################################


def batfish_question_failed(task: Task, df: DataFrame, name_add: str = False) -> None:
    """
    TBD
    """

    # Set the name_add variable if exists, else an empty string
    name_add = name_add if name_add else ""

    # df.info() prints by default directly to sys.stdout and by using the writable buffer a StringIO
    # instance can be used to get the string and write it into a normal variable
    buf = StringIO()
    df.info(buf=buf)
    df_info = buf.getvalue()
    # Set the Nornir task failed and result variable
    failed = True
    result = (
        f"{task_result(text=f'{task.name} {name_add}', changed=False, level_name='ERROR')}\n"
        f"'{task.name}' -> BatfishResponse <Success: False>\n"
        f"-> Batfish question returned an empty pandas dataframe\n"
        f"-> Verify Batfish snapshot config hostname and Nornir hostname\n\n"
        f"{df_info}"
    )

    return result, failed


def batfish_assert_type_failed(task: Task, data: tuple, name_add: str = False) -> None:
    """
    Helper function to get the error result string in case the Batfish ref_prop is an unsupported data type.
    """
    # Extract the variables from the data tuple
    col_name, ref_prop, sup_type = data
    # Set the name_add variable if exists, else col_name
    name_add = name_add if name_add else col_name

    # Set the Nornir task failed and result variable
    failed = True
    result = (
        f"{task_result(text=f'{task.name} {name_add}', changed=False, level_name='ERROR')}\n"
        f"'{task.name} {col_name}' -> BatfishResponse <Success: False>\n"
        f"-> Unsupported 'ref_prop' argument type {type(ref_prop)}\n"
        f"-> Supported 'ref_prop' argument type is {sup_type}"
    )

    return result, failed


def batfish_exit_error(result: AggregatedResult, bf_question: str) -> None:
    """
    Helper function to exit the script is case of a Batfish assert error.
    """
    if "config" in bf_question:
        text = "Inconsistent configuration properties exists!"
        msg = "-> Verify the Nornir inventory for inconsistent configuration properties"

    exit_error(
        task_text=result.name,
        text=text,
        msg=msg,
    )
