#!/usr/bin/env python3
"""
This module contains complete RESTCONF configuration workflows from multiple nornir_collection functions.

The functions are ordered as followed:
- Complete RESTCONF configuration workflows
"""

from nornir.core import Nornir
from nornir_collection.utils import print_task_title, exit_error
from nornir_collection.cisco.configuration_management.restconf.cisco_rpc import (
    rc_cisco_rpc_is_syncing,
    rc_cisco_rpc_rollback_config,
    rc_cisco_rpc_copy_file,
)


#### Complete RESTCONF Configuration Workflow 01 #############################################################


def rc_replace_config(
    nr: Nornir,
    rebuild: bool = False,
    cfg_status: bool = True,
    revert_timer: int = None,
    verbose: bool = False,
) -> bool:
    """
    Replace the current configuration with a specified configuration file.
    This function replaces the current configuration with the golden-config by default or the day0-config
    if the rebuild argument is set to True. It returns True if the operation was successful, otherwise False.
    """

    # Return False if cfg_status argument is False
    if not cfg_status:
        return False

    # Set rollback_config to day0-config if rebuild is True, else set it to golden-config
    rollback_config = "day0-config" if rebuild else "golden-config"
    # Calculate the revert-timer in minutes from the input revert-timer in seconds
    revert_timer = revert_timer // 60 if revert_timer else None

    # Print the task title if revert_timer is not set
    if not revert_timer:
        print_task_title(f"Replace current config with {rollback_config}")

    # Checks if an active datastore sync in ongoing and wait until is finish
    rc_cisco_rpc_is_syncing(nr=nr, verbose=verbose)

    # Replace the running-config with the rollback_config from the switch flash:
    cfg_status = rc_cisco_rpc_rollback_config(
        nr=nr,
        name=f"RESTCONF rollback {rollback_config}",
        target_url=f"flash:{rollback_config}",
        revert_timer=revert_timer,
        verbose=verbose,
    )

    return cfg_status


def rc_update_golden_config(nr: Nornir, verbose: bool = False) -> None:
    """
    Updates the golden configuration on Cisco devices using RESTCONF.
    This function performs the following steps:
    1. Prints the task title for updating the golden configuration.
    2. Checks if an active datastore synchronization is ongoing and waits until it finishes.
    3. Saves the current running configuration as the new golden configuration to the local device flash.
    4. Exits the script if the configuration update fails.
    """

    # Update golden config
    task_text = "RESTCONF update golden-config"
    print_task_title(title=task_text)

    # Checks if an active datastore sync in ongoing and wait until is finish
    rc_cisco_rpc_is_syncing(nr=nr, verbose=verbose)

    # Save the new config as the new golden config to the local device flash
    cfg_status = rc_cisco_rpc_copy_file(
        nr=nr,
        name=task_text,
        source="running-config",
        destination="flash:golden-config",
        verbose=verbose,
    )

    # Exit the script if the config status if False
    if not cfg_status:
        text = "ALERT: UPDATE GOLDEN-CONFIG HAVE FAILED!"
        msg = [
            "-> RESTCONF failed to update the golden configuration",
            "-> The remaining tasks have been omitted due to RESTCONF failed",
        ]
        exit_error(task_text=task_text, text=text, msg=msg)
