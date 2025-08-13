#!/usr/bin/env python3
"""
This module sets the device status in NetBox by running a custom script.
The Main function is intended to import and execute by other scripts.
"""

import sys
from nornir_collection.utils import exit_error, load_yaml_file
from nornir_collection.netbox.custom_script import run_nb_custom_script


__author__ = "Willi Kubny"
__maintainer__ = "Willi Kubny"
__version__ = "1.0"
__license__ = "MIT"
__email__ = "willi.kubny@dreyfusbank.ch"
__status__ = "Production"


def main(nr_config: str) -> None:
    """
    Main function is intended to import and execute by other scripts.
    It load Nornir configuration, retrieve NetBox URL, and run a custom NetBox script.

    * Args:
        * nr_config (str): Path to the Nornir configuration YAML file.

    * Steps:
        * Loads the Nornir configuration file.
        * Checks if the configuration file is loaded successfully; exits with code 1 if not.
        * Retrieves the NetBox URL from the configuration.
        * Runs the NetBox custom script 'set_device_status.SetDeviceStatus'.
        * Checks the result of the custom script execution.

    * Exits:
        * Exits with code 1 if the Nornir configuration file is empty or if any task fails.
    """

    # Load the Nornir yaml config file as dict and print a error message
    nr_config_dict = load_yaml_file(
        file=nr_config, text="Load Nornir Config File", silent=False, verbose=False
    )
    # Check the loaded config file and exit the script with exit code 1 if the dict is empty
    if not nr_config_dict:
        sys.exit(1)

    # Get the NetBox URL (Authentication token will be loaded as nb_token env variable)
    nb_url = nr_config_dict["inventory"]["options"]["nb_url"]

    # Run the NetBox custom script 'set_device_status.SetDeviceStatus'
    result_failed = run_nb_custom_script(
        name="set_device_status.SetDeviceStatus",
        url=f"{nb_url}/api/extras/scripts/set_device_status.SetDeviceStatus/",
        payload={"data": {}, "commit": True},
        verbose=False,
    )

    # Check the result and exit the script with exit code 1 and a error message
    if result_failed:
        exit_error(
            task_text="NetBox Custom Script Failed",
            msg=[
                "Check the result details in the pipeline log or directly in NetBox",
                "-> One or more device primary ip-address is not reachable by ping",
            ],
        )
