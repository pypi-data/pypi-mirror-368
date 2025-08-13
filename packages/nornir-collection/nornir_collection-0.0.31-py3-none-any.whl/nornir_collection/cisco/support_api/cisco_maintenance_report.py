#!/usr/bin/env python3
"""
The main function will gather device serial numbers over different input options (argument list, Excel or
dynamically with Nornir) as well as the hostname. With the serial numbers the Cisco support APIs will be
called and the received information will be printed to stdout and optional processed into an Excel report.
Optionally a IBM TSS Maintenance Report can be added with an argument to compare and analyze the IBM TSS
information against the received data from the Cisco support APIs. Also these additional data will be
processed into an Excel report and saved to the local disk.
"""

import argparse
from nornir.core import Nornir
from nornir_collection.nornir_plugins.inventory.utils import init_nornir
from nornir_collection.cisco.support_api.utils import (
    init_args_for_cisco_maintenance,
    prepare_nornir_data,
    prepare_static_serials,
)
from nornir_collection.cisco.support_api.reports import (
    create_pandas_dataframe_for_report,
    generate_cisco_maintenance_report,
)
from nornir_collection.cisco.support_api.cisco_support import (
    cisco_support_check_authentication,
    get_sni_owner_coverage_by_serial_number,
    get_sni_coverage_summary_by_serial_numbers,
    get_eox_by_serial_numbers,
    get_ss_suggested_release_by_pid,
    print_sni_owner_coverage_by_serial_number,
    print_sni_coverage_summary_by_serial_numbers,
    print_eox_by_serial_numbers,
    print_get_ss_suggested_release_by_pid,
)
from nornir_collection.utils import (
    print_task_title,
    exit_info,
    exit_error,
    construct_filename_with_current_date,
    load_yaml_file,
)


#### Internal Use Functions #################################################################################


def _create_report_config(args: argparse.Namespace, nr: Nornir = False) -> dict:
    """
    TBD
    """

    # Create a dict for the report configuration specifications
    report_cfg = {}

    # Create the report configuration if Nornir is used for dynamically data gathering
    if nr:
        # Get the report_config string from the Nornir inventory for later YAML file load
        # Get the report_file string from the Nornir inventory for later destination file constructing
        if args.report:
            report_cfg["yaml_config"] = nr.inventory.defaults.data["cisco_maintenance_report"]["yaml_config"]
            report_cfg["yaml_config"] = nr.inventory.defaults.data["cisco_maintenance_report"]["yaml_config"]
            report_cfg["excel_file"] = nr.inventory.defaults.data["cisco_maintenance_report"]["excel_file"]
        # Get the ibm_tss_report file from the Nornir inventory
        if args.tss:
            report_cfg["tss_file"] = nr.inventory.defaults.data["cisco_maintenance_report"]["tss_file"]

        return report_cfg

    # Create the report configuration if static provided data with an Excel or the --serials argument is used
    # Create the report_config string for later YAML file load
    report_cfg["yaml_config"] = "reports/src/report_config.yaml"
    # Create the report_file string for later destination file constructing
    report_cfg["excel_file"] = (
        args.excel if hasattr(args, "excel") else "reports/cisco_maintenance_report.xlsx"
    )
    # Set the ibm_tss_report file
    if args.tss:
        report_cfg["tss_file"] = args.tss

    return report_cfg


def _load_report_yaml_config(report_cfg, args):
    """
    TBD
    """
    # If the report_config file string is available
    if "yaml_config" in report_cfg:
        # Load the report variables from the YAML config file as python dictionary
        config = load_yaml_file(
            file=report_cfg["yaml_config"], text="PYTHON load report yaml config file", verbose=args.verbose
        )
        # Update the report_cfg dict with the loaded yaml config
        report_cfg.update(**config)

    # Select the correct string order based on the TSS arguments
    if args.nornir:
        df_order = "nornir_column_order_with_tss" if args.tss else "nornir_column_order"
    else:
        df_order = "static_column_order_with_tss" if args.tss else "static_column_order"

    # Set the df_order to False if the key don't exist
    report_cfg["df_order"] = report_cfg[df_order] if df_order in report_cfg else False
    # Select the correct dataframe order for all dates regarding conditional formatting
    # Set the df_date_columns to False if the key don't exist
    report_cfg["df_date_columns"] = (
        report_cfg["grace_period_cols"] if "grace_period_cols" in report_cfg else False
    )

    return report_cfg


def main(nr_config: str = "inventory/nr_config.yaml") -> None:
    """Main function is executed when the file is directly executed."""

    #### Initialize Script and Nornir #######################################################################

    # Initialize the script arguments with ArgParse to define the further script execution
    args = init_args_for_cisco_maintenance()

    if args.nornir:
        # Initialize, transform and filter the Nornir inventory are return the filtered Nornir object
        nr = init_nornir(
            config_file=nr_config,
            env_mandatory={
                "env_client_key": "CISCO_SUPPORT_API_KEY",
                "env_client_secret": "CISCO_SUPPORT_API_SECRET",
            },
            args=args,
            add_netbox_data=None,
        )

        print_task_title("Prepare Nornir Data")
        # Prepare the serials dict for later processing
        serials = prepare_nornir_data(nr=nr, verbose=args.verbose)

        # Prepare the Cisco support API key and the secret in a tuple
        api_creds = (
            nr.inventory.defaults.data["cisco_support_api_creds"]["env_client_key"],
            nr.inventory.defaults.data["cisco_support_api_creds"]["env_client_secret"],
        )
        # Create a dict for the report configuration specifications
        report_cfg = _create_report_config(nr=nr, args=args)

    else:
        print_task_title("Prepare Static Data")
        # Prepare the serials dict for later processing
        serials = prepare_static_serials(args=args)

        # Prepare the Cisco support API key and the secret in a tuple
        api_creds = (args.api_key, args.api_secret)
        # Create a dict for the report configuration specifications
        report_cfg = _create_report_config(args=args)

    #### Get Cisco Support-API Data ##########################################################################

    print_task_title("Check Cisco support API OAuth2 client credentials grant flow")

    # Check the API authentication with the client key and secret to get an access token
    # The script will exit with an error message in case the authentication fails
    if not cisco_support_check_authentication(api_creds=api_creds, verbose=args.verbose, silent=False):
        exit_error(task_text="NORNIR cisco maintenance status", text="Bad news! The script failed!")

    print_task_title("Gather Cisco support API data for serial numbers")

    # Cisco Support API Call SNIgetOwnerCoverageStatusBySerialNumbers and update the serials dictionary
    serials = get_sni_owner_coverage_by_serial_number(serial_dict=serials, api_creds=api_creds)
    # Print the results of get_sni_owner_coverage_by_serial_number()
    print_sni_owner_coverage_by_serial_number(serial_dict=serials, verbose=args.verbose)

    # Cisco Support API Call SNIgetCoverageSummaryBySerialNumbers and update the serials dictionary
    serials = get_sni_coverage_summary_by_serial_numbers(serial_dict=serials, api_creds=api_creds)
    # Print the results of get_sni_coverage_summary_by_serial_numbers()
    print_sni_coverage_summary_by_serial_numbers(serial_dict=serials, verbose=args.verbose)

    # Cisco Support API Call EOXgetBySerialNumbers and update the serials dictionary
    serials = get_eox_by_serial_numbers(serial_dict=serials, api_creds=api_creds)
    # Print the results of get_eox_by_serial_numbers()
    print_eox_by_serial_numbers(serial_dict=serials, verbose=args.verbose)

    # Cisco Support API Call getSuggestedReleasesByProductIDs and update the serials dictionary
    serials = get_ss_suggested_release_by_pid(serial_dict=serials, api_creds=api_creds)
    # Print the results of get_ss_suggested_release_by_pid()
    print_get_ss_suggested_release_by_pid(serial_dict=serials, verbose=args.verbose)

    #### Prepate the Pandas report data ######################################################################

    # Exit the script if the args.report argument is not set
    if not args.report:
        exit_info(
            task_text="NORNIR cisco maintenance status", text="Good news! The Script successfully finished!"
        )

    print_task_title("Prepare Cisco maintenance report")

    # Load the yaml report config file
    report_cfg = _load_report_yaml_config(report_cfg=report_cfg, args=args)
    # Prepare the report data and create a pandas dataframe
    df = create_pandas_dataframe_for_report(serials_dict=serials, report_cfg=report_cfg, args=args)

    #### Generate Cisco maintenance report Excel #############################################################

    print_task_title("Generate Cisco maintenance report")

    # Construct the new destination path and filename from the report_file string variable
    report_cfg["excel_file"] = construct_filename_with_current_date(
        name="PYTHON construct destination file",
        filename=report_cfg["excel_file"],
        silent=False,
    )
    # Generate the Cisco Maintenance report Excel file specified by the report_file with the pandas dataframe
    generate_cisco_maintenance_report(df=df, report_cfg=report_cfg)

    exit_info(
        task_text="NORNIR cisco maintenance status", text="Good news! The Script successfully finished!"
    )


if __name__ == "__main__":
    main()
