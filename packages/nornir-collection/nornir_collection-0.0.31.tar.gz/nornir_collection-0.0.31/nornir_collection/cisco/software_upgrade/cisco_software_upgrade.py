#!/usr/bin/env python3
"""
This module updates the software version on Cisco IOS-XE devices with Nornir.
The Main function is intended to import and execute by other scripts.
"""

import argparse
from nornir.core import Nornir
from nornir_collection.nornir_plugins.inventory.utils import init_nornir
from nornir_collection.cisco.configuration_management.cli.show_tasks import (
    cli_verify_destination_md5_hash,
    cli_install_remove_inactive_task,
)
from nornir_collection.cisco.configuration_management.restconf.tasks import (
    rc_verify_current_software_version_fallback_cli,
    rc_software_install_one_shot_fallback_cli,
    rc_install_remove_inactive_fallback_cli,
)
from nornir_collection.cisco.software_upgrade.utils import (
    prepare_upgrade_data,
    scp_upload_software_file,
    cli_http_download_software_file,
    verify_issu_requirements,
    cli_track_issu_upgrade_process,
    fping_track_upgrade_process,
    cli_verify_switch_state,
)
from nornir_collection.utils import (
    exit_info,
    print_result,
    exit_error,
    print_task_title,
    nr_filter_inventory_from_host_list,
)


def copy_software(nr: Nornir, args: bool) -> None:
    """
    Copy software package files to hosts. Verify destination md5 hash with cli and upload software file if
    needed with SCP or HTTP. The nornir inventory will be re-filtered if only some hosts needs a software
    upload and the upload method is SCP or HTTP depending on the args.local_upload argument.

    Args:
        nr (Nornir): The Nornir object containing the inventory of hosts.
        args (bool): The command line arguments.

    Returns:
        None
    """

    print_task_title("Verify destination software file md5 hash")
    # Verify if the destination file exists and verify the md5 hash.
    failed_hosts = cli_verify_destination_md5_hash(nr=nr)

    # If the failed_hosts list is empty -> Return None
    if not failed_hosts:
        return

    # If the failed_host list is not empty and not identical with the Nornir inventory
    if sorted(failed_hosts) != sorted(list(nr.inventory.hosts.keys())):
        print_task_title("Re-Filter nornir inventory")
        # Re-filter the Nornir inventory to the failed_hosts only
        nr = nr_filter_inventory_from_host_list(
            nr=nr,
            filter_reason="Exclude good hosts to copy the software file only to the following hosts:",
            host_list=failed_hosts,
        )

    if args.remove_inactive:
        # The failed_hosts list is not empty -> Clean-up all not needed software package files
        print_task_title("Remove inactive software package files for filesystem clean-up")
        # Run the custom Nornir task cli_install_remove_inactive_task
        cli_task_result = nr.run(
            task=cli_install_remove_inactive_task,
            name="CLI install remove inactive",
            verbose=args.verbose,
            on_failed=True,
        )
        # Print the Nornir cli_install_remove_inactive_task task result
        print_result(cli_task_result)
        # Exit the script is the task failed
        if cli_task_result.failed:
            exit_error(
                task_text="NORNIR software upgrade status",
                text="ALERT: NETMIKO install remove inactive failed!",
            )

    # If the failed_hosts are identical with the Nornir inventory -> All hosts need a software upload
    if sorted(failed_hosts) == sorted(list(nr.inventory.hosts.keys())):
        if args.local_upload:
            print_task_title("Upload software image file with SCP")
            if not scp_upload_software_file(nr=nr):
                exit_error(
                    task_text="NORNIR software upgrade status",
                    text="ALERT: NETMIKO upload file with SCP failed!",
                )
        else:
            print_task_title("Download software image file with HTTP")
            if not cli_http_download_software_file(nr=nr, verbose=args.verbose):
                exit_error(
                    task_text="NORNIR software upgrade status",
                    text="ALERT: NETMIKO download file with HTTP failed!",
                )

    # Elif the failed_hosts are not identical with the Nornir inventory -> Some hosts needs software upload
    elif sorted(failed_hosts) != sorted(list(nr.inventory.hosts.keys())):
        if args.local_upload:
            print_task_title("Upload software image file with SCP")
            # Re-filter the Nornir inventory to the failed_hosts only
            nr_obj_upload = nr_filter_inventory_from_host_list(
                nr=nr,
                filter_reason="Exclude good hosts to upload the software file only on the following hosts:",
                host_list=failed_hosts,
            )
            if not scp_upload_software_file(nr=nr_obj_upload):
                exit_error(
                    task_text="NORNIR software upgrade status",
                    text="ALERT: NETMIKO upload file with SCP failed!",
                )
        else:
            print_task_title("Download software image file with HTTP")
            # Re-filter the Nornir inventory to the failed_hosts only
            nr_obj_upload = nr_filter_inventory_from_host_list(
                nr=nr,
                filter_reason="Exclude good hosts to download the software file only on the following hosts:",
                host_list=failed_hosts,
            )
            if not cli_http_download_software_file(nr=nr_obj_upload, verbose=args.verbose):
                exit_error(
                    task_text="NORNIR software upgrade status",
                    text="ALERT: NETMIKO download file with HTTP failed!",
                )


def main(nr_config: str, args: argparse.Namespace) -> None:
    """
    Main function is intended to import and execute by other scripts.
    It initialize Nornir and execute a software upgrade on Cisco IOS-XE devices.

    * Args:
        * nr_config (str): Path to the Nornir configuration file.
        * args (argparse.Namespace): Command-line arguments parsed by argparse.

    * Steps:
        * Initializes the Nornir inventory and filters it based on the provided configuration.
        * Prepares software upgrade details and verifies the current software version.
        * Re-filters the Nornir inventory to include only hosts that need a software upgrade.
        * Verifies the destination software file and uploads it if necessary.
        * Starts the software installation process.
        * Monitors and verifies the software upgrade progress.
        * Cleans up old version files.

    * Exits:
        * It exits with appropriate messages and statuses based on the success or failure of each step.
    """

    #### Initialize Script and Nornir ######################################################################

    # Initialize, transform and filter the Nornir inventory are return the filtered Nornir object
    nr = init_nornir(config_file=nr_config, args=args, add_netbox_data=None)

    #### Prepare software upgrade details and verify current version #######################################

    print_task_title("Prepare software version upgrade details")
    # Get the desired version from the Nornir inventory and verify the software file from the inventory in
    # case local image upload is enabled. The inventory will be filled later with more data
    upgrade_type = "scp" if args.local_upload else "http"
    if not prepare_upgrade_data(nr=nr, upgrade_type=upgrade_type):
        exit_error(
            task_text="NORNIR software upgrade status", text="ALERT: NORNIR prepare upgrade data failed!"
        )

    print_task_title("Verify current software version")
    # Verify the desired software version against the installed software version with RESTCONF and a fallback
    # with CLI in case the RESTCONF task would fail. Returns a list of hosts which needs a software upgrade
    failed_hosts = rc_verify_current_software_version_fallback_cli(nr=nr, verbose=args.verbose)

    # If the failed_host list is empty, all hosts match the desired software version and exit the script
    if not failed_hosts:
        exit_info(
            task_text="NORNIR software upgrade status",
            text="The desired software version is up to date on all hosts",
            changed=False,
        )

    # If the failed_host list is not empty and not identical with the Nornir inventory
    if sorted(failed_hosts) != sorted(list(nr.inventory.hosts.keys())):
        print_task_title("Re-Filter nornir inventory")
        # Re-filter the Nornir inventory to the failed_hosts only
        nr = nr_filter_inventory_from_host_list(
            nr=nr,
            filter_reason="Exclude good hosts to run the software upgrade only on the following hosts:",
            host_list=failed_hosts,
        )

    #### Verify destination software file / Upload software file only if not already exists ##################

    # Verify destination md5 hash with cli and upload software file if needed with SCP or HTTP
    # The nornir inventory will be re-filtered if only some hosts needs a software upload and the upload
    # method is SCP or HTTP depending on the args.local_upload argument
    copy_software(nr=nr, args=args)

    #### Start software installation process ###############################################################

    print_task_title("Execute software version upgrade")

    # If the argparse commit_reload argument is False -> Exit the script with exit code 0
    if args.commit_reload is False:
        exit_info(
            task_text="NORNIR software upgrade status",
            text="The software upgrade process is ready for install, but has not been started yet",
            changed=False,
        )

    # Verify that there is no downgrade with ISSU argument set to True or exit the script
    if args.issu is True:
        if not verify_issu_requirements(nr=nr):
            exit_error(
                task_text="NORNIR software upgrade status",
                text="ALERT: ISSU requirements failed!",
            )

    # Install the new software RESTCONF in a one-shot process and a fallback with CLI in case the RESTCONF
    # task would fail. Returns True or False weather the task was successfull or not.
    if not rc_software_install_one_shot_fallback_cli(nr=nr, issu=args.issu, verbose=args.verbose):
        exit_error(
            task_text="NORNIR software upgrade status",
            text="ALERT: RESTCONF and CLI one-shot install failed!",
        )

    #### Monitor and verify version update status ##########################################################

    task_title = "Track ISSU software upgrade progress" if args.issu else "Track software upgrade progress"
    print_task_title(task_title)

    if args.issu:
        # Software upgrade tracking loop for ISSU upgrade with show commands as connectivity should never
        # be lost. The max_time defines the maximum time the script should run until the upgrade process
        # should be finished and acts as a timeout.
        cli_track_issu_upgrade_process(nr=nr, max_time=2400)  # 40 minutes timeout
    else:
        # Software upgrade tracking loop with fping until all hosts are upgraded with a max_time timeout.
        # The max_time defines how long fping track until the IP connectivity should be back again.
        fping_track_upgrade_process(nr=nr, max_time=2400)  # 40 minutes timeout

    # Verify that all switches in the show switch command output are in state "Ready"
    if not cli_verify_switch_state(nr=nr, max_time=600):  # 10 minutes timeout
        exit_error(
            task_text="NORNIR software upgrade status",
            text="ALERT: Not all switches in the stack are ready after software upgrade!",
        )

    print_task_title("Verify current software version")
    # Verify the desired software version against the installed software version with RESTCONF and a fallback
    # with CLI in case the RESTCONF task would fail. Returns a list of hosts which needs a software upgrade
    failed_hosts = rc_verify_current_software_version_fallback_cli(nr=nr, verbose=args.verbose)

    # If the failed_hosts list is not empty
    if failed_hosts:
        exit_error(
            task_text="NORNIR software upgrade status",
            text="ALERT: RESTCONF and CLI software upgrade failed!",
        )

    #### Cleanup old version files ##########################################################################

    # Remove all not needed software package files on the filesystem with RESTCONF and a fallback with CLI in
    # case the RESTCONF task would fail. Returns a list of hosts which needs a software upgrade
    if not rc_install_remove_inactive_fallback_cli(nr=nr, verbose=args.verbose):
        exit_error(
            task_text="NORNIR software upgrade status",
            text="ALERT: RESTCONF and CLI install remove inactive failed!",
        )

    # The software upgrade was successful on all hosts
    exit_info(
        task_text="NORNIR software upgrade status",
        text="The software upgrade was successful on all hosts",
        changed=True,
    )
