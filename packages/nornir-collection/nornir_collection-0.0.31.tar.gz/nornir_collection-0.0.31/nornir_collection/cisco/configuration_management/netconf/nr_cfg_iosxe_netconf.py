#!/usr/bin/env python3
"""
This module is a complete config management inclusive testing and rollback in case of failures for
Cisco IOS-XE devices. The Main function is intended to import and execute by other scripts.
"""

import argparse
from nornir.core.filter import F
from nornir_collection.nornir_plugins.inventory.utils import init_nornir
from nornir_collection.cisco.configuration_management.cli.show_tasks import nr_pre_config_check
from nornir_collection.cisco.configuration_management.netconf.config_workflow import (
    nc_cfg_iosxe_netconf_config,
)
from nornir_collection.cisco.configuration_management.restconf.config_workflow import (
    rc_update_golden_config,
    rc_replace_config,
)
from nornir_collection.utils import print_task_title, task_name, task_info, task_error, exit_info, exit_error


__author__ = "Willi Kubny"
__maintainer__ = "Willi Kubny"
__version__ = "1.0"
__license__ = "MIT"
__email__ = "willi.kubny@dreyfusbank.ch"
__status__ = "Production"


def main(nr_config: str, args: argparse.Namespace) -> None:
    """
    Main function is intended to import and execute by other scripts.
    It initialize Nornir, configures and test the config on Cisco IOS-XE devices.

    * Args:
        * nr_config (str): Path to the Nornir config file.
        * args (argparse.Namespace): Command-line arguments parsed by argparse.

    * Steps:
        * Initialize Nornir
        * Verify that all filtered devices that have the tag slug 'cfg-mgmt'
        * Do a pre-config check to ensure the current config is in a clean state
        * Configure the network from code with NETCONF and RESTCONF
        * Set the config rebuild level (Day0-Config or Golden-Config)
        * Perform a RESTCONF config-rollback to the Day0-Config or Golden-Config
        * Verify that there is no NETCONF sync in progress
        * Lock the NETCONF datastore
        * Reset all interfaces to default config
        * Start NETCONF general system config
        * Continue NETCONF interface config
        * Validate NETCONF config
        * Abort the config if a dry-run is requested
        * Commit all changes on the NETCONF candidate datastore (default with commit-confirm)
        * Run testing if commit-confirm was requested
        * Commit again if testing was successful
        * Unlock the NETCONF datastore
        * Verify that there is no NETCONF sync in progress
        * Save the running-config to the startup-config using RESTCONF
        * Verify the status of the config results
        * Update the golden-config with RESTCONF

    * Exits:
        * It exits with appropriate messages and statuses based on the success or failure of each step.
    """

    #### Initialize Script and Nornir #######################################################################

    # Initialize, transform and filter the Nornir inventory are return the filtered Nornir object
    # Define data to load from NetBox in addition to the base Nornir inventory plugin
    add_netbox_data = {"load_virtual_chassis_data": True, "load_interface_data": True, "load_vlan_data": True}
    nr = init_nornir(config_file=nr_config, args=args, add_netbox_data=add_netbox_data)

    # Filter the Nornir inventory again only with devices that have the tag name 'CFG-MGMT' and compare the
    # filtered inventory with the original inventory to prevent the script from running on devices that are
    # not intended for config management
    print_task_title(title="Verify Nornir inventory filter for CFG-MGMT")
    task_text = "NORNIR verify inventory filter for CFG-MGMT"
    print(task_name(text=task_text))
    # Filter the Nornir inventory with devices that have the tag 'CFG-MGMT'
    nr_cfg_mgmt = nr.filter(F(tags__contains="CFG-MGMT"))
    # Exit the script if the filtered inventory does not match the original inventory
    if len(nr.inventory.hosts) != len(nr_cfg_mgmt.inventory.hosts):
        print(task_error(text=task_text, changed=False))
        print(f"'{task_text}' -> NornirResult <Success: False>")
        exit_error(
            task_text=task_text,
            text="ALERT: INVENTORY FILTER MISMATCH FOR CFG-MGMT!",
            msg=[
                "-> The filtered inventory does not match the original inventory",
                "-> Ensure all devices intended for config management are tagged with 'CFG-MGMT'",
            ],
        )
    print(task_info(text=task_text, changed=False))
    print(f"'{task_text}' -> NornirResponse <Success: True>")
    print("-> All filtered devices are tagged with 'CFG-MGMT'")

    #### Run Nornir Tasks to Verify the config State ########################################################

    # If the pre-check arg is True, do a pre-config check to ensure the current config is in a clean state
    if not args.rebuild and args.pre_check:
        cfg_status = nr_pre_config_check(nr=nr)
        # Exit the script if the config status is not clean
        if not cfg_status:
            task_text = "Verify pre-config check results"
            print_task_title(title=task_text)
            print(f"{task_name(text=task_text)}")
            exit_error(
                task_text=task_text,
                text="BAD NEWS! THE RUNNING-CONFIG IS NOT CLEAN!",
                msg=[
                    "-> Bring the running-config into a clean state with the golden-config",
                    "-> Or skip the pre-config check",
                ],
            )

    #### Run Nornir Tasks to Replace the config #############################################################

    # If its not a NETCONF dry-run, replace the current config with the golden-config or day0-config
    if not args.dryrun:
        # Replace the config with a Cisco specific RESTCONF RPC. Default cfg_status argument is True
        cfg_status = rc_replace_config(nr=nr, rebuild=args.rebuild, verbose=args.verbose, revert_timer=None)

        # Exit the script if the RESTCONF replace-config failed
        if not cfg_status:
            task_text = "Verify RESTCONF replace-config results"
            print_task_title(title=task_text)
            print(f"{task_name(text=task_text)}")
            exit_error(
                task_text=task_text,
                text="ALERT: REPLACE-CONFIG HAVE FAILED!",
                msg=[
                    "-> RESTCONF failed to replace the current config",
                    "-> The remaining tasks have been omitted due to RESTCONF failed",
                ],
            )

    #### Run Nornir Tasks to Configure IOS-XE device from Code with NETCONF #################################

    # The IOS-XE device will be reconfigured to the desired state and return a boolian (True == Successful)
    cfg_status = nc_cfg_iosxe_netconf_config(
        nr=nr,
        rebuild=args.rebuild,
        disable_commit_confirm=args.disable_commit_confirm,
        confirm_timeout=args.confirm_timeout,
        dry_run=args.dryrun,
        verbose=args.verbose,
    )

    # Exit the script if the NETCONF config failed
    if not cfg_status:
        # Replace the config with a Cisco specific RESTCONF RPC. Default cfg_status argument is True
        # This ensures that the golden-config is not updated if the NETCONF config failed
        rc_replace_config(nr=nr, rebuild=args.rebuild, verbose=args.verbose, revert_timer=None)

        # Verify status of the config results
        task_text = "Verify NETCONF config results"
        print_task_title(title=task_text)
        print(f"{task_name(text=task_text)}")
        exit_error(
            task_text=task_text,
            text="ALERT: ONE OR MORE CONFIGS HAVE FAILED!",
            msg=[
                "-> NETCONF failed to apply the desired config",
                "-> The remaining tasks have been omitted due to NETCONF failed",
                "-> The current config is unchanged and the golden-config have not been updated yet",
            ],
        )

    #### Run Nornir Tasks to Update the Golden-config #######################################################

    # Update the golden config with RESTCONF or exit the script if RESTCONF failed
    rc_update_golden_config(nr=nr, verbose=args.verbose)

    # If rc_update_golden_config didn't exit the script, everything was successful
    task_text = "Verify config results"
    print_task_title(title=task_text)
    print(f"{task_name(text=task_text)}")
    exit_info(
        task_text=task_text,
        text="GOOD NEWS! ALL CONFIGS HAVE BEEN APPLIED SUCCESSFUL!",
        msg=[
            "-> The desired NETCONF config have been activated and saved",
            "-> The golden-config have been updated",
        ],
    )
