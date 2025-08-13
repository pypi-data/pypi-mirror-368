#!/usr/bin/env python3
"""
This module contains functions to prepare Cisco Support API data to generate reports.

The functions are ordered as followed:
- Prepare Cisco Support API data for Pandas Dataframe
- Prepare IBM TSS data for Pandas Dataframe
- Create Pandas Dataframe with report data
- Excel Report Generation
"""

import argparse
import os
import json
from datetime import datetime, timedelta
import __main__
import pandas as pd
import numpy as np
from xlsxwriter.utility import xl_col_to_name
from nornir_collection.utils import (
    print_task_name,
    task_info,
    get_pandas_column_width,
)


#### Prepare Cisco Support API data for Pandas Dataframe #####################################################


def prepare_report_data_host(serials_dict: dict, nornir: bool = False) -> dict:
    """
    This function takes the serials_dict which has been filled with data by various functions and creates a
    host dict with the key "host" and a list of all hostnames as the value. The key will be the pandas
    dataframe column name and the value which is a list will be the colums cell content. The host dict will
    be returned.
    """
    # Define the host_data dict and its key value pairs
    columns = ["host"]
    # Create the dictionary
    host_data = {column: [] for column in columns}

    # Add all hostnames to the list
    host_data["host"] = [item["host"] for item in serials_dict.values()]

    # Return the host_data dict if Nornir is not used
    if not nornir:
        return host_data

    # Define dict keys for the Nornir data
    columns = ["switch_num", "desired_version", "current_version"]
    # Create the dictionary
    nr_data = {column: [] for column in columns}

    # Append the Nornir nr_data values for each defined dict key
    for header in nr_data:
        success = False
        for item in serials_dict.values():
            for key, value in item["nr_data"].items():
                if header == key:
                    if key in nr_data:
                        nr_data[key].append(value)
                        success = True
        # If nothing was appended to the nr_data dict, append an empty string
        if not success:
            nr_data[header].append("")

    # Merge the host data and the Nornir data dict together
    data = {**host_data, **nr_data}

    return data


def prepare_report_data_sni_owner_by_sn(serials_dict: dict) -> dict:
    """
    This function takes the serials_dict which has been filled with data by various functions and creates a
    dictionary with key-value pairs. The key will be the pandas dataframe column name and the value which
    is a list will be the colums cell content. The host dict will be returned.
    """
    # Define dict keys for SNIgetOwnerCoverageStatusBySerialNumbers
    columns = ["sr_no_owner", "coverage_end_date"]
    # Create the dictionary
    sni_owner_by_sn = {column: [] for column in columns}

    # Append the SNIgetOwnerCoverageStatusBySerialNumbers values for each defined dict key
    for header in sni_owner_by_sn:
        success = False
        for sr_no in serials_dict.values():
            for key, value in sr_no["SNIgetOwnerCoverageStatusBySerialNumbers"].items():
                if header == key:
                    if key in sni_owner_by_sn:
                        sni_owner_by_sn[key].append(value)
                        success = True
        # If nothing was appended to the sni_owner_by_sn dict, append an empty string
        if not success:
            sni_owner_by_sn[header].append("")

    return sni_owner_by_sn


def prepare_report_data_sni_summary_by_sn(serials_dict: dict) -> dict:
    """
    This function takes the serials_dict which has been filled with data by various functions and creates a
    dictionary with key-value pairs. The key will be the pandas dataframe column name and the value which
    is a list will be the colums cell content. The host dict will be returned.
    """
    # Define dict keys for SNIgetCoverageSummaryBySerialNumbers
    # fmt: off
    columns = [
        "sr_no", "is_covered", "contract_site_customer_name", "contract_site_address1", "contract_site_city",
        "contract_site_state_province", "contract_site_country", "covered_product_line_end_date",
        "service_contract_number", "service_line_descr", "warranty_end_date", "warranty_type",
        "warranty_type_description", "item_description", "item_type", "orderable_pid",
    ]
    # fmt: on
    # Create the dictionary
    sni_summary_by_sn = {column: [] for column in columns}

    # Append the SNIgetCoverageSummaryBySerialNumbers values for each defined dict key
    for header in sni_summary_by_sn:
        for sr_no in serials_dict.values():
            success = False
            # Append all general coverage details
            for key, value in sr_no["SNIgetCoverageSummaryBySerialNumbers"].items():
                if header == key:
                    if key in sni_summary_by_sn:
                        sni_summary_by_sn[key].append(value)
                        success = True
            # Append all the orderable pid details
            for key, value in sr_no["SNIgetCoverageSummaryBySerialNumbers"]["orderable_pid_list"][0].items():
                if header == key:
                    if key in sni_summary_by_sn:
                        sni_summary_by_sn[key].append(value)
                        success = True
            # If nothing was appended to the sni_summary_by_sn dict, append an empty string
            if not success:
                sni_summary_by_sn[header].append("")

    return sni_summary_by_sn


def prepare_report_data_eox_by_sn(serials_dict: dict) -> dict:
    """
    This function takes the serials_dict which has been filled with data by various functions and creates a
    dictionary with key-value pairs. The key will be the pandas dataframe column name and the value which is
    a list will be the colums cell content. The host dict will be returned.
    """
    # Define dict keys for EOXgetBySerialNumbers
    # fmt: off
    columns = [
        "EOXExternalAnnouncementDate", "EndOfSaleDate", "EndOfSWMaintenanceReleases",
        "EndOfSecurityVulSupportDate", "EndOfRoutineFailureAnalysisDate", "EndOfServiceContractRenewal",
        "LastDateOfSupport", "EndOfSvcAttachDate", "UpdatedTimeStamp", "MigrationInformation",
        "MigrationProductId", "MigrationProductName", "MigrationStrategy", "MigrationProductInfoURL",
        "ErrorDescription", "ErrorDataType", "ErrorDataValue",
    ]
    # fmt: on
    # Create the dictionary
    eox_by_sn = {column: [] for column in columns}

    # Append the EOXgetBySerialNumbers values for each defined dict key
    for header in eox_by_sn:
        for sr_no in serials_dict.values():
            success = False
            # Append all end of life dates
            for key, value in sr_no["EOXgetBySerialNumbers"].items():
                if header == key:
                    if isinstance(value, dict):
                        if "value" in value:
                            eox_by_sn[key].append(value["value"])
                            success = True
            # Append all migration details
            for key, value in sr_no["EOXgetBySerialNumbers"]["EOXMigrationDetails"].items():
                if header == key:
                    if key in eox_by_sn:
                        eox_by_sn[key].append(value)
                        success = True
            # If EOXError exists append the error reason, else append an empty string
            if "EOXError" in sr_no["EOXgetBySerialNumbers"]:
                for key, value in sr_no["EOXgetBySerialNumbers"]["EOXError"].items():
                    if header == key:
                        if key in eox_by_sn:
                            eox_by_sn[key].append(value)
                            success = True
            # If nothing was appended to the eox_by_sn dict, append an empty string
            if not success:
                eox_by_sn[header].append("")

    return eox_by_sn


def prepare_report_data_ss_by_pid(serials_dict: dict) -> dict:
    """
    This function takes the serials_dict which has been filled with data by various functions and creates a
    dictionary with key-value pairs. The key will be the pandas dataframe column name and the value which is
    a list will be the colums cell content. The host dict will be returned.
    """
    # Create the dictionary to fill with all suggested release information
    ss_by_pid = {}
    ss_by_pid["recommended_version"] = []

    for records in serials_dict.values():
        # Empty string to fill with the recommended releases
        recommended_release = ""
        # As there can be multiple suggestions with the same ID and release, but only with different mdfId,
        # the no_duplicates list will be created to eliminate duplicate IDs and release information.
        no_duplicates = []
        for item in records["SSgetSuggestedReleasesByProductIDs"]:
            if isinstance(item, str):
                if item not in no_duplicates:
                    no_duplicates.append(item)
                    recommended_release += item
            elif isinstance(item, dict):
                for idx, suggestion in enumerate(item["suggestions"]):
                    idx = idx + 1
                    if suggestion["releaseFormat1"] and suggestion["releaseFormat1"] not in no_duplicates:
                        no_duplicates.append(suggestion["releaseFormat1"])
                        recommended_release += f"ID: {idx}, Release: {suggestion['releaseFormat1']} / "
                    elif (
                        suggestion["errorDetailsResponse"]
                        and suggestion["errorDetailsResponse"]["errorDescription"] not in no_duplicates
                    ):
                        error_description = suggestion["errorDetailsResponse"]["errorDescription"]
                        recommended_release += f"{error_description} / "

        # Remove the last two characters from the string to remove the trailing slash
        if recommended_release.endswith(" / "):
            recommended_release = recommended_release[:-2]

        ss_by_pid["recommended_version"].append(recommended_release)

    return ss_by_pid


#### Prepare action needed data for Pandas Dataframe #########################################################


def prepare_report_data_act_needed(serials_dict: dict) -> dict:
    """
    This function takes the serials_dict an argument and creates a dictionary named act_needed will be
    returned which contains the key value pairs "coverage_action_needed" and "api_action_needed" to create a
    Pandas dataframe later.
    """
    # Define the coverage_action_needed dict and its key value pairs to return as the end of the function
    columns = ["coverage_action_needed", "api_action_needed"]
    # Create the dictionary
    act_needed = {column: [] for column in columns}

    for records in serials_dict.values():
        # Verify if the user has the correct access rights to access the serial API data
        if "YES" in records["SNIgetOwnerCoverageStatusBySerialNumbers"]["sr_no_owner"]:
            act_needed["api_action_needed"].append(
                "No action needed (API user is associated with contract and device)"
            )
        else:
            act_needed["api_action_needed"].append(
                "Action needed (No association between api user, contract and device)"
            )

        # Verify if the serial is covered by Cisco add the coverage_action_needed variable to tss_info
        if "YES" in records["SNIgetCoverageSummaryBySerialNumbers"]["is_covered"]:
            act_needed["coverage_action_needed"].append(
                "No action needed (Device is covered by a maintenance contract)"
            )
        else:
            act_needed["coverage_action_needed"].append(
                "Action needed (Device is not covered by a maintenance contract)"
            )

    return act_needed


#### Prepare IBM TSS data for Pandas Dataframe ###############################################################


def prepare_report_data_tss(serials_dict: dict, file: str) -> dict:
    """
    This function takes the serials_dict and a source file which is the IBM TSS report as arguments. The only
    mandatory column is the "Serials" which will be normalized to tss_serial. All other columns can be
    specified with their order and the prefix "tss_" in the EXCEL_COLUMN_ORDER_WITH_TSS constant. A dictionary
    named tss_info will be returned which contains the key value pairs "coverage_action_needed",
    "api_action_needed" and all TSS data to create a Pandas dataframe later.
    """
    # Define the tss_info dict and its key value pairs to return as the end of the function
    columns = ["coverage_action_needed", "api_action_needed"]

    # Read the excel file into a pandas dataframe -> Row 0 is the title row
    df = pd.read_excel(rf"{file}", dtype=str, engine="openpyxl")

    # Make some data normalization of the TSS report file column headers
    # Make column written in lowercase letters
    df.columns = df.columns.str.lower()
    # Replace column name whitespace with underscore
    df.columns = df.columns.str.replace(" ", "_")
    # Add a prefix to the column name to identify the TSS report columns
    df = df.add_prefix("tss_")

    # Create the dictionary with the static defined columns and all IBM TSS columns from the dataframe
    tss_info = {column: [] for column in (columns + list(df.columns))}

    # Make all serial numbers written in uppercase letters
    df.tss_serial = df.tss_serial.str.upper()

    # The first fillna will replace all of (None, NAT, np.nan, etc) with Numpy's NaN, then replace
    # Numpy's NaN with python's None
    df = df.fillna(np.nan).replace([np.nan], [None])

    # Delete all rows which have not the value "Cisco" in the OEM column
    df = df[df.tss_oem == "Cisco"]

    # Create a list with all IBM TSS serial numbers
    tss_serial_list = df["tss_serial"].tolist()

    # Look for inventory serials which are covered by IBM TSS and add them to the serial_dict
    # It's important to match IBM TSS serials to inventory serials first for the correct order
    for sr_no, records in serials_dict.items():
        records["tss_info"] = {}

        # Covered by IBM TSS if inventory serial number is in all IBM TSS serial numbers
        if sr_no in tss_serial_list:
            # Verify if the user has the correct access rights to access the serial API data
            if "YES" in records["SNIgetOwnerCoverageStatusBySerialNumbers"]["sr_no_owner"]:
                tss_info["api_action_needed"].append(
                    "No action needed (API user is associated with contract and device)"
                )
            else:
                tss_info["api_action_needed"].append(
                    "Action needed (No association between api user, contract and device)"
                )

            # Verify if the inventory serial is covered by IBM TSS and is also covered by Cisco
            # Verify if the serial is covered by Cisco add the coverage_action_needed variable to tss_info
            if "YES" in records["SNIgetCoverageSummaryBySerialNumbers"]["is_covered"]:
                tss_info["coverage_action_needed"].append("No action needed (Covered by IBM TSS and Cisco)")
            else:
                tss_info["coverage_action_needed"].append(
                    "Action needed (Covered by IBM TSS, but Cisco coverage missing)"
                )

            # Get the index of the list item and assign the element from the TSS dataframe by its index
            index = tss_serial_list.index(sr_no)
            # Add the data from the TSS dataframe to tss_info
            for column, value in tss_info.items():
                if column.startswith("tss_"):
                    value.append(df[column].values[index])

        # Inventory serial number is not in all IBM TSS serial numbers
        else:
            # Verify if the user has the correct access rights to access the serial API data
            if "YES" in records["SNIgetOwnerCoverageStatusBySerialNumbers"]["sr_no_owner"]:
                tss_info["api_action_needed"].append(
                    "No action needed (API user is associated with contract and device)"
                )
            else:
                tss_info["api_action_needed"].append(
                    "Action needed (No association between api user, contract and device)"
                )

            # Verify if the inventory serial is covered by Cisco
            # Add the coverage_action_needed variable to tss_info
            if "YES" in records["SNIgetCoverageSummaryBySerialNumbers"]["is_covered"]:
                tss_info["coverage_action_needed"].append("No action needed (Covered by Cisco SmartNet)")
            else:
                tss_info["coverage_action_needed"].append(
                    "Action needed (Cisco SmartNet or IBM TSS coverage missing)"
                )

            # Add the empty strings for all additional IBM TSS serials to tss_info
            for column, value in tss_info.items():
                if column.startswith("tss_"):
                    value.append("")

    # After the inventory serials have been processed
    # Add IBM TSS serials to tss_info which are not part of the inventory serials
    for tss_serial in tss_serial_list:
        if tss_serial not in serials_dict.keys():
            # Add the coverage_action_needed variable to tss_info
            tss_info["coverage_action_needed"].append(
                "Action needed (Remove serial from IBM TSS inventory as device is decommissioned)"
            )
            tss_info["api_action_needed"].append("No Cisco API data as serial is not part of column sr_no")

            # Get the index of the list item and assign the element from the TSS dataframe by its index
            index = tss_serial_list.index(tss_serial)
            # Add the data from the TSS dataframe to tss_info
            for column, value in tss_info.items():
                if column.startswith("tss_"):
                    value.append(df[column].values[index])

    return tss_info


#### Create Pandas Dataframe with report data ################################################################


def create_pandas_dataframe_for_report(
    serials_dict: dict, report_cfg: dict, args: argparse.Namespace
) -> pd.DataFrame:
    """
    Prepare the report data and create a pandas dataframe. The pandas dataframe will be returned
    """

    print_task_name(text="PYTHON prepare report data")

    # Create an empty dict and append the previous dicts to create later the pandas dataframe
    report_data = {}

    # Prepare the needed data for the report from the serials dict. The serials dict contains all data
    # that the Cisco support API sent. These functions return a dictionary with the needed data only
    host = prepare_report_data_host(serials_dict=serials_dict, nornir=args.nornir)
    sni_owner_by_sn = prepare_report_data_sni_owner_by_sn(serials_dict=serials_dict)
    sni_summary_by_sn = prepare_report_data_sni_summary_by_sn(serials_dict=serials_dict)
    eox_by_sn = prepare_report_data_eox_by_sn(serials_dict=serials_dict)
    ss_by_pid = prepare_report_data_ss_by_pid(serials_dict=serials_dict)

    # Update the report_data dict
    report_data.update(**host, **sni_owner_by_sn, **sni_summary_by_sn, **eox_by_sn, **ss_by_pid)

    if "tss_file" in report_cfg:
        # Analyze the IBM TSS report file and create the tss_info dict
        tss_info = prepare_report_data_tss(serials_dict=serials_dict, file=report_cfg["tss_file"])
        # The tss_info dict may have more list elements as TSS serials have been found which are not inside
        # the customer inventory -> Add the differente to all other lists as empty strings
        for _ in range(len(tss_info["tss_serial"]) - len(host["host"])):
            for column in report_data.values():
                column.append("")
        # Update the report_data dict
        report_data.update(**tss_info)
    else:
        # Analyze if actions are needed for serial number or user
        act_needed = prepare_report_data_act_needed(serials_dict=serials_dict)
        # Update the report_data dict with all prepared data dicts
        report_data.update(**act_needed)

    print(task_info(text="PYTHON prepare report data dict", changed=False))
    print("'PYTHON prepare report data dict' -> PythonResult <Success: True>")
    if args.verbose:
        print("\n" + json.dumps(report_data, indent=4))

    # Reorder the data dict according to the key_order list -> This needs Python >= 3.6
    if "df_order" in report_cfg:
        report_data = {key: report_data[key] for key in report_cfg["df_order"]}

    print(task_info(text="PYTHON order report data dict", changed=False))
    print("'PYTHON order report data dict' -> PythonResult <Success: True>")
    if args.verbose:
        print("\n" + json.dumps(report_data, indent=4))

    # Create a Pandas dataframe for the data dict
    df = pd.DataFrame(report_data)

    # Format each column in the list to a pandas date type for later conditional formatting
    if "df_date_columns" in report_cfg:
        for column in report_cfg["df_date_columns"]:
            df[column] = pd.to_datetime(df[column], format="%Y-%m-%d")

    print(task_info(text="PYTHON create pandas dataframe from dict", changed=False))
    print("'PANDAS create dataframe' -> PandasResult <Success: True>")
    if args.verbose:
        print(df)

    return df


#### Excel Report Generation #################################################################################


def _worksheet_add_title_row(workbook, worksheet, config):
    """
    TBD
    """
    # Setting for the whole worksheet
    zoom = config["zoom"] if "zoom" in config else 110
    worksheet.set_zoom(zoom)
    # Specify how many columns should be frozen
    freeze_col = config["freeze_columns"] if "freeze_columns" in config else 0
    freeze_row = config["freeze_row"] if "freeze_row" in config else 2
    worksheet.freeze_panes(freeze_row, freeze_col)

    # Set the top row height
    worksheet.set_row(0, config["title_row_height"] if "title_row_height" in config else 60)
    # Create a format to use for the merged top row
    title_format = workbook.add_format(
        {
            "font_name": config["title_font_name"] if "title_font_name" in config else "Calibri",
            "font_size": config["title_font_size"] if "title_font_size" in config else 20,
            "font_color": config["title_font_color"] if "title_font_color" in config else "#FFFFFF",
            "bg_color": config["title_bg_color"] if "title_bg_color" in config else "#FF452C",
            "align": "left",
            "valign": "vcenter",
            "bold": 1,
            "bottom": 1,
        }
    )
    # Enable text wrap for the title format to enable custum newlines
    title_format.set_text_wrap()

    # Insert a logo to the top row
    if "title_logo" in config:
        # Merge the number of top row cells according to the frozen columns to insert a logo
        worksheet.merge_range(0, 0, 0, freeze_col - 1 if freeze_col != 0 else freeze_col, None, title_format)
        worksheet.insert_image(
            "A1",
            config["title_logo"],
            {
                "x_scale": config["title_logo_x_scale"],
                "y_scale": config["title_logo_y_scale"],
                "x_offset": config["title_logo_x_offset"],
                "y_offset": config["title_logo_y_offset"],
            },
        )
    # Specify the title text
    if "tss_report" in config:
        title_text = (
            config["title_text_tss"]
            if "title_text_tss" in config
            else "Cisco Maintenance Report incl. IBM TSS Analysis"
        )
    else:
        title_text = config["title_text"] if "title_text" in config else "Cisco Maintenance Report"
    # Merge from the cell 3 to the max_col and write a title
    title_text = f"{title_text}\n(generated by {os.path.basename(__main__.__file__)})"
    worksheet.merge_range(0, freeze_col, 0, config["max_col"], title_text, title_format)

    return worksheet


def _worksheet_add_table(df, workbook, worksheet, config):
    """
    TBD
    """

    # Create a list of column headers, to use in add_table().
    columns = [{"header": column} for column in df.columns]

    # Add the Excel table structure. Pandas will add the data.
    # fmt: off
    worksheet.add_table(1, 0, config["max_row"] - 1, config["max_col"],
        {
            "columns": columns,
            "style": config["table_style"] if "table_style" in config else "Table Style Medium 8",
        },
    )
    # fmt: on

    table_format = workbook.add_format(
        {
            "font_name": config["table_font_name"] if "table_font_name" in config else "Calibri",
            "font_size": config["table_font_size"] if "table_font_size" in config else 11,
            "align": "left",
            "valign": "vcenter",
        }
    )
    # Auto-adjust each column width -> +5 on the width makes space for the filter icon
    for index, width in enumerate(get_pandas_column_width(df)):
        # Set the minimum width of the column to 15 is the width is smaller than 15
        width = 15 if width < 15 else width
        worksheet.set_column(index, index - 1, width + 5, table_format)

    return worksheet


def _worksheet_add_conditional_formatting(df, workbook, worksheet, config):
    """
    TBD
    """

    # Specify the table start row where conditional formatting should start
    startrow = 3
    # Create a red background format for the conditional formatting
    format_red = workbook.add_format({"bg_color": "#C0504D", "align": "left", "valign": "vcenter"})
    # Create a orange background format for the conditional formatting
    format_orange = workbook.add_format({"bg_color": "#F79646", "align": "left", "valign": "vcenter"})
    # Create a green background format for the conditional formatting
    format_green = workbook.add_format({"bg_color": "#9BBB59", "align": "left", "valign": "vcenter"})

    # Create a conditional formatting for each column in the list.
    column_list = ["sr_no_owner", "is_covered", "coverage_action_needed", "api_action_needed"]
    # Create a conditional formatting for each column in the list.
    column_list = ["sr_no_owner", "is_covered", "coverage_action_needed", "api_action_needed"]
    column_list = [column for column in column_list if column in df.columns]
    for column in column_list:
        # Get the column letter by the column name
        target_col = xl_col_to_name(df.columns.get_loc(column))
        # -> Excel requires the value for type cell to be double quoted
        worksheet.conditional_format(
            f"{target_col}{startrow}:{target_col}{config['max_row']}",
            {"type": "cell", "criteria": "equal to", "value": '"NO"', "format": format_red},
        )
        worksheet.conditional_format(
            f"{target_col}{startrow}:{target_col}{config['max_row']}",
            {"type": "cell", "criteria": "equal to", "value": '"YES"', "format": format_green},
        )
        worksheet.conditional_format(
            f"{target_col}{startrow}:{target_col}{config['max_row']}",
            {"type": "text", "criteria": "containing", "value": "No action needed", "format": format_green},
        )
        worksheet.conditional_format(
            f"{target_col}{startrow}:{target_col}{config['max_row']}",
            {"type": "text", "criteria": "containing", "value": "Action needed", "format": format_red},
        )

    # Create a conditional formatting for each column with a date. Get the column letter by the column name
    if "grace_period_cols" in config:
        grace_period = config["grace_period_days"] if "grace_period_days" in config else 90
        for column in config["grace_period_cols"]:
            target_col = xl_col_to_name(df.columns.get_loc(column))
            worksheet.conditional_format(
                f"{target_col}{startrow}:{target_col}{config['max_row']}",
                {
                    "type": "date",
                    "criteria": "between",
                    "minimum": datetime.today().date() + timedelta(days=grace_period),
                    "maximum": datetime.strptime("2999-01-01", "%Y-%m-%d"),
                    "format": format_green,
                },
            )
            worksheet.conditional_format(
                f"{target_col}{startrow}:{target_col}{config['max_row']}",
                {
                    "type": "date",
                    "criteria": "between",
                    "minimum": datetime.today().date(),
                    "maximum": datetime.today().date() + timedelta(days=grace_period),
                    "format": format_orange,
                },
            )
            worksheet.conditional_format(
                f"{target_col}{startrow}:{target_col}{config['max_row']}",
                {
                    "type": "date",
                    "criteria": "between",
                    "minimum": datetime.strptime("1999-01-01", "%Y-%m-%d"),
                    "maximum": datetime.today().date() - timedelta(days=1),
                    "format": format_red,
                },
            )

    # Create a conditional formatting for the current_version compared with the desired_version
    if "current_version" in df.columns and "desired_version" in df.columns:
        # Get the column letter by the column name
        version_col = xl_col_to_name(df.columns.get_loc("current_version"))
        # Iterate over all cells in current_version and compare the string against the desired_version
        for idx, version in enumerate(df["current_version"].values):
            # If the current_version is in with the desired_version
            if version and version in df["desired_version"][idx]:
                # enumerate start with 0, but the cell start with 3 -> +3 to match idx with starting cell
                worksheet.write(f"{version_col}{idx + startrow}", version, format_green)
            elif version:
                # enumerate start with 0, but the cell start with 3 -> +3 to match idx with starting cell
                worksheet.write(f"{version_col}{idx + startrow}", version, format_red)

    # Create a conditional formatting for the desired_version compared with the recommended_version
    if "desired_version" in df.columns and "recommended_version" in df.columns:
        # Get the column letter by the column name
        version_col = xl_col_to_name(df.columns.get_loc("desired_version"))
        # Iterate over all cells in desired_version and compare the string against the recommended_version
        for idx, version in enumerate(df["desired_version"].values):
            # If the desired_version is in with the recommended_version
            if version and version in df["recommended_version"][idx]:
                # enumerate start with 0, but the cell startrow is different -> +startrow to match start cell
                worksheet.write(f"{version_col}{idx + startrow}", version, format_green)
            elif version:
                # enumerate start with 0, but the cell startrow is different -> +startrow to match start cell
                worksheet.write(f"{version_col}{idx + startrow}", version, format_orange)

    return worksheet


def generate_cisco_maintenance_report(df: pd.DataFrame, report_cfg: dict) -> None:
    """
    Generate the Cisco Maintenance report Excel file specified by the report_file with the pandas dataframe.
    The function returns None, but saves the Excel file to the local disk.
    """

    # Disable Pandas SettingWithCopyWarning for "chained" assignments
    # -> Error-Message: A value is trying to be set on a copy of a slice from a DataFrame
    # -> https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
    pd.options.mode.chained_assignment = None  # default='warn'

    print_task_name(text="PYTHON create Pandas writer object using XlsxWriter engine")

    #### Create the xlsx writer, workbook and worksheet objects #############################################

    # Get the dimensions of the dataframe.
    (max_row, max_col) = df.shape
    # Max_row + 2 because the first two rows are used for title and header
    report_cfg["max_row"] = max_row + 2
    # Max_com -1 otherwise would be one column to much
    report_cfg["max_col"] = max_col - 1

    # Create a Pandas excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(
        path=report_cfg["excel_file"],
        engine="xlsxwriter",
        date_format="yyyy-mm-dd",
        datetime_format="yyyy-mm-dd",
    )

    # Get the xlsxwriter workbook object
    workbook = writer.book
    # Write the dataframe data to XlsxWriter. Turn off the default header and index and skip one row to allow
    # us to insert a user defined header.
    sheet_name = report_cfg["sheet_name"] if "sheet_name" in report_cfg else "Cisco_Maintenance_Report"
    df.to_excel(writer, sheet_name=sheet_name, startrow=2, header=False, index=False)
    # Get the xlsxwriter worksheet object
    worksheet = writer.sheets[sheet_name]

    print(task_info(text="PYTHON create XlsxWriter workbook and worksheet", changed=False))
    print("'PYTHON create pandas writer object using XlsxWriter engine' -> PythonResult <Success: True>")

    #### Add content and condidional formatting to the xlsx writer worksheet ################################

    # Add the top title row
    worksheet = _worksheet_add_title_row(workbook=workbook, worksheet=worksheet, config=report_cfg)
    print(task_info(text="PYTHON create XlsxWriter title row", changed=False))
    print("'PYTHON create XlsxWriter title row' -> PythonResult <Success: True>")

    # Add a Excel table structure and add the Pandas dataframe
    worksheet = _worksheet_add_table(df=df, workbook=workbook, worksheet=worksheet, config=report_cfg)
    print(task_info(text="PYTHON create XlsxWriter table and add pandas dataframe", changed=False))
    print("'PYTHON create XlsxWriter table and add pandas dataframe' -> PythonResult <Success: True>")

    # Create conditional formating
    worksheet = _worksheet_add_conditional_formatting(
        df=df, workbook=workbook, worksheet=worksheet, config=report_cfg
    )
    print(task_info(text="PYTHON create XlsxWriter conditional formating", changed=False))
    print("'PYTHON create XlsxWriter conditional formating' -> PythonResult <Success: True>")

    #### Save the Excel report file to disk ##################################################################

    print_task_name(text="PYTHON generate report Excel file")

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()

    print(task_info(text="PYTHON generate report Excel file", changed=False))
    print("'PYTHON generate report Excel file' -> PythonResult <Success: True>")
    print(f"-> Saved information about {df.shape[0]} serials to {report_cfg['excel_file']}")
