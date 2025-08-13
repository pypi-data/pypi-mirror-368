#!/usr/bin/env python3
"""
This module sync a list of NetBox datasources and print the result.
The Main function is intended to import and execute by other scripts.
"""

import time
import json
import sys
from nornir_collection.utils import load_yaml_file, task_name, task_error, task_info, exit_error
from nornir_collection.netbox.utils import get_nb_resources, post_nb_resources

__author__ = "Willi Kubny"
__maintainer__ = "Willi Kubny"
__version__ = "1.0"
__license__ = "MIT"
__email__ = "willi.kubny@dreyfusbank.ch"
__status__ = "Production"


def main(nr_config: str, datasources: list[str]) -> None:
    """
    Main function is intended to import and execute by other scripts.
    It sync external data sources to NetBox.

    * Args:
        * nr_config (str): Path to the Nornir YAML configuration file.
        * datasources (list[str]): List of data source names to be synced.

    * Steps:
        * Loads the Nornir configuration from the specified YAML file.
        * Retrieves the NetBox URL from the configuration.
        * Iterates over the provided data sources and attempts to sync each one with NetBox.
        * For each data source, it checks if the data source exists in NetBox.
        * If the data source exists, it initiates a sync operation and monitors its status.
        * Logs the result of each sync operation.
        * If any data sources fail to sync, it exits with an error message and a list of failed data sources.

    * Exit:
        * Exits with code 1 if the Nornir configuration file is empty or if any task fails.
    """

    # Create a empty list to fill with all datasources that fail to sync
    failed_datasources = []

    # Load the Nornir yaml config file from the filepath
    nr_config = load_yaml_file(file=nr_config)
    # Check the loaded config file and exit the script with exit code 1 if the dict is empty
    if not nr_config:
        sys.exit(1)
    # Get the NetBox URL
    nb_url = nr_config["inventory"]["options"]["nb_url"]

    task_text = "NETBOX Sync External Git Datasource"
    print(task_name(text=task_text))

    # Loop over all datasources and sync the data into NetBox
    for datasource in datasources:
        # Get the NetBox datasource
        query = {"name": datasource, "enabled": True}
        response = get_nb_resources(url=f"{nb_url}/api/core/data-sources/", params=query)
        # Verify the result (list of dict)
        if not response:
            failed_datasources.append(datasource)
            print(task_error(text=task_text, changed=False))
            print(f"'{task_text} {datasource}' -> NetBoxResponse <Success: False>")
            print(f"-> Datasource '{datasource}' not found")
            # Continue because the datasource sync failed
            continue

        # Start the NetBox datasource sync
        ds_id = response[0]["id"]
        response = post_nb_resources(url=f"{nb_url}/api/core/data-sources/{ds_id}/sync/", payload=[])
        result = response.json()

        # Do thee GET request to verify the status of the running NetBox datasource sync
        # Terminate the while loop with a timeout of max 300s (5min)
        timeout_start = time.time()
        while time.time() < timeout_start + 300:
            # Verify the NetBox datasource status
            if result["status"]["value"] not in ("queued", "syncing"):
                # Break out of the loop as the datasource sync was successful
                break
            # Get the NetBox datasource
            response = get_nb_resources(url=f"{nb_url}/api/core/data-sources/", params=query)
            result = response[0]
            time.sleep(1)

        # Print the status after the datasource sync
        if result["status"]["value"] == "completed":
            print(task_info(text=f"{task_text} {datasource}", changed=True))
            print(f"'{task_text} {datasource}' -> NetBoxResponse <Success: True>")
            print(f"-> Completed {task_text} '{datasource}'")
        else:
            failed_datasources.append(datasource)
            print(task_error(text=f"{task_text} {datasource}", changed=False))
            print(f"'{task_text} {datasource}' -> NetBoxResponse <Success: False>")
            print(f"-> Failed {task_text} '{datasource}'")
            print(json.dumps(result, indent=4))

    # Check the result and exit the script with exit code 1 and a error message
    if failed_datasources:
        exit_error(
            task_text=f"{task_text} Failed",
            msg=[
                "Check the result details in the pipeline log or directly in NetBox",
                "-> The following datasources failed to sync:",
                failed_datasources,
            ],
        )
