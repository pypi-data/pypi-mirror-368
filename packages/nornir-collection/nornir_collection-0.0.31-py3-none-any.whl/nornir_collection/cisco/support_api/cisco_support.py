#!/usr/bin/env python3
"""
This module contains functions to get data from the Cisco Support APIs.

The functions are ordered as followed:
- Cisco Support API call functions
- Print functions for Cisco Support API call functions in Nornir style
"""

import json
import time
from typing import Any, Literal, Union
import requests
from nornir_collection.cisco.support_api.api_calls import get_cisco_support_token, SNI, EOX, SS
from nornir_collection.utils import task_name, task_host, task_info, task_error, iterate_all, exit_error


#### Cisco Support API Error Lists ##########################################################################


# fmt: off
SNI_ERRORS = [
    "EXCEEDED_OUTPUT", "API_MISSING_PARAMETERS", "API_INVALID_INPUT", "EXCEEDED_INPUTS",
    "API_NOTAUTHORIZED", "API_ERROR_01",
]
EOX_ERRORS = [
    "SSA_GENERIC_ERR", "SSA_ERR_001", "SSA_ERR_003", "SSA_ERR_007", "SSA_ERR_009", "SSA_ERR_010",
    "SSA_ERR_011", "SSA_ERR_012", "SSA_ERR_013", "SSA_ERR_014", "SSA_ERR_015", "SSA_ERR_016", "SSA_ERR_018",
    "SSA_ERR_022", "SSA_ERR_023", "SSA_ERR_024", "SSA_ERR_028", "SSA_ERR_030", "SSA_ERR_031", "SSA_ERR_032",
    "SSA_ERR_033", "SSA_ERR_034", "SSA_ERR_036", "SSA_ERR_037",
]
SS_ERRORS = [
    "S3_BASEPID_NO_SUPPORT", "S3_BASEPID_REQ", "S3_HW_INFORMATION_NOT_SUPPORTED", "S3_INV_BASEPID",
    "S3_INV_BASEPID", "S3_INV_CURR_IMG_REL", "S3_INV_IMAGE", "S3_INV_INPUT", "S3_INV_MDFID", "S3_INV_MDFID",
    "S3_INV_QUERY_PARAM", "S3_INV_QUERY_PARAM", "S3_INV_QUERY_PARAM", "S3_INV_QUERY_PARAM",
    "S3_INV_QUERY_PARAM", "S3_INV_QUERY_PARAM", "S3_INV_RELEASE", "S3_INV_RELEASE_IMAGE",
    "S3_MDFID_NO_SUPPORT", "S3_MDFID_REQ", "S3_NO_SOFT_AVL",
    "S3_SERVICE_EXCEPTION_OCCURED",
]
# fmt: on


#### Helper Functions #######################################################################################


def _success(value: bool) -> Literal["CISCOAPIResult <Success: True>", "CISCOAPIResult <Success: False>"]:
    """
    TBD
    """
    if value:
        return "CISCOAPIResult <Success: True>"
    return "CISCOAPIResult <Success: False>"


#### Cisco Support API Call Helper Functions ################################################################


def _get_total_num_pages(**kwargs) -> int:
    """
    Helper function to get the total number of pages for the Cisco Support API call
    """
    # Cisco Support API Object and API name as string
    api_obj = kwargs["api_obj"]
    api = kwargs["api_string"]
    chunk = kwargs["chunk"]
    sleep = kwargs["SLEEP"]

    # Get the total number of pages for the chunk list
    # Re-try the Cisco support API call with a backoff again in case of an error
    for _ in range(kwargs["RETRY_ATTEMPTS"]):
        # Call the Cisco support API for the chunk list to get the total number of pages
        # Use mapping with lambda to avoid long if elif else statements
        api_calls = {
            "sni": lambda: api_obj.getCoverageSummaryBySerialNumbers(sr_no=chunk, page_index=1),
            "eox": lambda: api_obj.getBySerialNumbers(serialNumber=chunk, pageIndex=1),
            "ss": lambda: api_obj.getSuggestedReleasesByProductIDs(productIds=chunk, pageIndex=1),
        }

        # Execute the correct lambda API call by the dictionary key which matches to api.lower()
        try:
            response = api_calls[api.lower()]()
        except requests.exceptions.JSONDecodeError:
            continue

        # Use mapping to avoid long if elif else statements
        keys = {
            "sni": ("pagination_response_record", "last_index"),
            "eox": ("PaginationResponseRecord", "LastIndex"),
            "ss": ("paginationResponseRecord", "lastIndex"),
        }

        # If the pagination details are present
        # Select the correct API response keys by the dictionary key which matches to api.lower()
        if keys[api.lower()][0] in response and response[keys[api.lower()][0]] is not None:
            # Return the total number of pages to create API calls for all pages
            return response[keys[api.lower()][0]][keys[api.lower()][1]]

        # SLEEP and continue with next range() loop attempt
        time.sleep(sleep)
        sleep = sleep * kwargs["SLEEP_MULTIPLIER"]

    # Ending for loop as iterable exhausted
    try:
        return verify_cisco_support_api_data(
            api=api.lower(), iterable=response, force_failed=True, verbose=True
        )
    except UnboundLocalError:
        return verify_cisco_support_api_data(api=api.lower(), iterable=None, force_failed=True, verbose=True)


def _get_data_all_pages(**kwargs) -> list[dict]:
    """
    TBD
    """
    # Cisco Support API Object and API name as string
    api_obj = kwargs["api_obj"]
    api = kwargs["api_string"]
    api_sub = kwargs["api_string_sub"] if "api_string_sub" in kwargs else api
    chunk = kwargs["chunk"]
    sleep = kwargs["SLEEP"]

    # Create a list to fill with the API response chunks
    api_data = []

    # Get the API data for each page of the chunk list
    # Call the Cisco support API for each page of the chunk list
    for page in range(1, int(kwargs["num_pages"]) + 1):
        # Re-try the Cisco support API call with a backoff again in case of an error
        for _ in range(kwargs["RETRY_ATTEMPTS"]):
            # Call the Cisco support API for the chunk list
            # Use mapping with lambda to avoid long if elif else statements
            api_calls = {
                "sni_owner": lambda: api_obj.getOwnerCoverageStatusBySerialNumbers(sr_no=chunk),
                "sni_summary": lambda: api_obj.getCoverageSummaryBySerialNumbers(
                    sr_no=chunk, page_index=page
                ),
                "eox": lambda: api_obj.getBySerialNumbers(serialNumber=chunk, pageIndex=page),
                "ss": lambda: api_obj.getSuggestedReleasesByProductIDs(productIds=chunk, pageIndex=page),
            }
            try:
                # Execute the correct lambda API call by the dictionary key which matches to api_sub.lower()
                response = api_calls[api_sub.lower()]()
            except requests.exceptions.JSONDecodeError:
                continue

            # Use mapping to avoid long if elif else statements
            keys = {
                "sni_owner": ("serial_numbers", "serial_numbers"),
                "sni_summary": ("pagination_response_record", "serial_numbers"),
                "eox": ("PaginationResponseRecord", "EOXRecord"),
                "ss": ("paginationResponseRecord", "productList"),
            }

            # If the pagination details are present
            # Select the correct API response keys by the dictionary key which matches to api_sub.lower()
            if keys[api_sub.lower()][0] in response and response[keys[api_sub.lower()][0]] is not None:
                # Update the api_data list
                for item in response[keys[api_sub.lower()][1]]:
                    api_data.append(item)

                # Check if the initial list and the response list have the same length. This verifies that
                # there is a response for each pid of the initial list
                if api_sub.lower() == "ss":
                    # Create a set without duplicated with set comprehension
                    chunk_response = list({item["product"]["basePID"] for item in response["productList"]})
                    # Exit the script if the length of both pid lists are not identical
                    if len(chunk) != len(chunk_response):
                        invalid_pid = [item for item in chunk if item not in chunk_response]
                        verify_cisco_support_api_data(
                            api=api.lower(),
                            iterable=response,
                            force_failed=True,
                            verbose=True,
                            add_info=f"-> Invalid PIDs: {invalid_pid}",
                        )

                # Break out of the for loop and continue with the next page
                break

            # SLEEP and continue with next range() loop attempt
            time.sleep(sleep)
            sleep = sleep * kwargs["SLEEP_MULTIPLIER"]

        else:  # no break
            # Ending for loop as iterable exhausted
            return verify_cisco_support_api_data(
                api=api.lower(), iterable=response, force_failed=True, verbose=True
            )

    # Return the API data list
    return api_data


#### Cisco Support API Response Verification #################################################################


def verify_cisco_support_api_data(
    api: Literal["sni", "eox", "ss"],
    iterable: Union[dict, None],
    force_failed: bool = False,
    verbose: bool = False,
    add_info: Any = False,
) -> bool:
    """
    This function verifies the serials_dict which has been filled with data by various functions of these
    module like eox_by_serial_numbers, sni_get_coverage_summary_by_serial_numbers, etc. and verifies that
    there are no invalid serial numbers. In case of invalid serial numbers, the script quits with an error
    message.
    """
    if not force_failed:
        # Check if any value of the iterable is inside the API error lists
        no_error = True
        for value in iterate_all(iterable=iterable, returned="value"):
            if value is None:
                continue
            if any(value == error for error in (SNI_ERRORS + EOX_ERRORS + SS_ERRORS)):
                no_error = False
                break

        if no_error:
            print(task_name(text=f"Verify Cisco support {api.upper()} API data"))
            print(task_info(text=f"Verify Cisco support {api.upper()} API data", changed=False))
            print(f"'Verify Cisco support {api.upper()} API data' -> {_success(True)}")

            return True

    error = (
        f"{task_name(text=f'Verify Cisco support {api.upper()} API data')}\n"
        f"{task_error(text=f'Verify Cisco support {api.upper()} API data', changed=False)}\n"
        f"'Verify Cisco support {api.upper()} API data' -> {_success(False)}"
    )

    if isinstance(iterable, dict):
        # Print additional information depending which Cisco support API has been used
        for value in iterate_all(iterable=iterable, returned="value"):
            if value is None:
                continue
            if api.lower() in "sni" and any(value == error for error in SNI_ERRORS):
                print(error)
                print(f"-> {api.upper()} API-Error: {value}")
                if verbose:
                    print("\n" + json.dumps(iterable, indent=4))
                if add_info:
                    print(add_info)
                break
            if api.lower() in "eox" and any(value == error for error in EOX_ERRORS):
                print(error)
                if "ErrorResponse" in iterable:
                    print(f"-> {api.upper()} API-Error: {value}")
                    if verbose:
                        print("\n" + json.dumps(iterable, indent=4))
                    if add_info:
                        print(add_info)
                else:
                    print("-> The EOX API returned None. This could be a bug in the API.")
                    if add_info:
                        print("\n" + json.dumps(add_info, indent=4))
                break
            if api.lower() in "ss":
                print(error)
                if any(value == error for error in SS_ERRORS):
                    print(f"-> {api.upper()} API-Error: {value}")
                    if verbose:
                        print("\n" + json.dumps(iterable, indent=4))
                    if add_info:
                        print(add_info)
                else:
                    print(
                        "-> The initial PID list contains invalid PIDs. The returned list is not identical."
                    )
                    if add_info:
                        print(add_info)
                break
            if api.lower() not in ["sni", "eox", "ss"]:
                print(error)
                print(f"-> Unknown API: {api.upper()}")
                break
    else:
        # The Cisco support API response is invalid
        print(error)
        print("-> The API response is invalid. This could be a bug in the API.")
        print(add_info)

    # Exit the script with a proper message
    exit_error(
        task_text=f"CISCO-API get {api.upper()} data",
        text="ALERT: GET CISCO SUPPORT API DATA FAILED!",
        msg="-> Analyse the error message and identify the root cause",
    )


#### Cisco Support API call functions ########################################################################


def cisco_support_check_authentication(api_creds: tuple, verbose: bool = False, silent: bool = False) -> bool:
    """
    This function checks to Cisco support API authentication by generating an bearer access token. In case
    of an invalid API client key or secret a error message is printed and the script exits.
    """
    task_text = "CISCO-API check OAuth2 client credentials grant flow"

    try:
        # Try to generate an barer access token
        token = get_cisco_support_token(*api_creds, verify=None, proxies=None)

        if not silent:
            print(task_name(text=task_text))
            print(task_info(text=task_text, changed=False))
            print(f"'Bearer access token generation' -> {_success(True)}")
            if verbose:
                print(f"-> Bearer token: {token}")

        return True

    except KeyError:
        print(task_name(text=task_text))
        print(task_error(text=task_text, changed=False))
        print(f"'Bearer access token generation' -> {_success(False)}")
        print("-> Invalid API client key and/or secret provided")

        return False


def get_sni_owner_coverage_by_serial_number(serial_dict: dict, api_creds: tuple) -> dict:
    """
    This function takes the serial_dict which contains all serial numbers and the Cisco support API creds to
    get the owner coverage by serial number with the cisco-support library. The result of each serial will
    be added with a new key to the dict. The function returns the updated serials dict. The format of the
    serials_dict need to be as below.
    "<serial>": {
        "host": "<hostname>",
        ...
    },
    """

    # Maximum serial number API parameter value
    MAX_SR_NO = 75

    # Create the Cisco support API object
    sni = SNI(*api_creds)

    sni_vars = {
        # Backoff sleep and attempt values
        "RETRY_ATTEMPTS": 20,
        "SLEEP": 1,
        "SLEEP_MULTIPLIER": 1,
        # Cisco Support API Object and API name as string
        "api_obj": sni,
        "api_string": "sni",
        "api_string_sub": "sni_owner",
        # The SNI coverage owner API have only one page
        "num_pages": 1,
    }

    # API calls to the Cisco Support API coverage owner by serial number
    # Loop over a list with all serial numbers with a step incrementation of MAX_ITEM
    for index in range(0, len(list(serial_dict.keys())), MAX_SR_NO):
        # Create a chunk list with the maximum allowed elements specified by MAX_ITEM
        sni_vars["chunk"] = list(serial_dict.keys())[index : index + MAX_SR_NO]
        # Get the API data for each page of the chunk list
        api_data = _get_data_all_pages(**sni_vars)

        # Add all records to the serial_dict dictionary
        for record in api_data:
            serial_dict[record["sr_no"]]["SNIgetOwnerCoverageStatusBySerialNumbers"] = record

    return serial_dict


def get_sni_coverage_summary_by_serial_numbers(serial_dict: dict, api_creds: tuple) -> dict:
    """
    This function takes the serial_dict which contains all serial numbers and the Cisco support API creds to
    get the coverage summary by serial number with the cisco-support library. The result of each serial will
    be added with a new key to the dict. The function returns the updated serials dict. The format of the
    serials_dict need to be as below.
    "<serial>": {
        "host": "<hostname>",
        ...
    },
    """

    # Maximum serial number API parameter value
    MAX_SR_NO = 75

    # Create the Cisco support API object
    sni = SNI(*api_creds)

    sni_vars = {
        # Backoff sleep and attempt values
        "RETRY_ATTEMPTS": 20,
        "SLEEP": 1,
        "SLEEP_MULTIPLIER": 1,
        # Cisco Support API Object and API name as string
        "api_obj": sni,
        "api_string": "sni",
        "api_string_sub": "sni_summary",
    }

    # API calls to the Cisco Support API coverage summary by serial number
    # Loop over a list with all serial numbers with a step incrementation of MAX_ITEM
    for index in range(0, len(list(serial_dict.keys())), MAX_SR_NO):
        # Create a chunk list with the maximum allowed elements specified by MAX_ITEM
        sni_vars["chunk"] = list(serial_dict.keys())[index : index + MAX_SR_NO]
        # Part 1: Get the total number of pages for the API call of this index
        sni_vars["num_pages"] = _get_total_num_pages(**sni_vars)
        # Part 2: Get the API data for each page of the chunk list
        api_data = _get_data_all_pages(**sni_vars)

        # Add all records to the serial_dict dictionary
        for record in api_data:
            sr_no = record["sr_no"]
            serial_dict[sr_no]["SNIgetCoverageSummaryBySerialNumbers"] = record

    return serial_dict


def get_eox_by_serial_numbers(serial_dict: dict, api_creds: tuple) -> dict:
    """
    This function takes the serial_dict which contains all serial numbers and the Cisco support API creds to
    run get the end of life data by serial number with the cisco-support library. The result of each serial
    will be added with a new key to the dict. The function returns the updated serials dict. The format of
    the serials_dict need to be as below.
    "<serial>": {
        "host": "<hostname>",
        ...
    },
    """

    # Maximum serial number API parameter value
    MAX_SR_NO = 20

    # Create the Cisco support API objec
    eox = EOX(*api_creds)

    eox_vars = {
        # Backoff sleep and attempt values
        "RETRY_ATTEMPTS": 20,
        "SLEEP": 1,
        "SLEEP_MULTIPLIER": 1,
        # Cisco Support API Object and API name as string
        "api_obj": eox,
        "api_string": "eox",
    }

    # API calls to the Cisco Support API end of life by serial number
    # Loop over a list with all serial numbers with a step incrementation of MAX_ITEM
    for index in range(0, len(list(serial_dict.keys())), MAX_SR_NO):
        # Create a chunk list with the maximum allowed elements specified by MAX_ITEM
        eox_vars["chunk"] = list(serial_dict.keys())[index : index + MAX_SR_NO]
        # Part 1: Get the total number of pages for the API call of this index
        eox_vars["num_pages"] = _get_total_num_pages(**eox_vars)
        # Part 2: Get the API data for each page of the chunk list
        api_data = _get_data_all_pages(**eox_vars)

        for record in api_data:
            # The response value of "EOXInputValue" can be a single serial number or a comma separated
            # string of serial numbers as the API response can collect multiple same EoX response together
            for sr_no in record["EOXInputValue"].split(","):
                serial_dict[sr_no]["EOXgetBySerialNumbers"] = record

    return serial_dict


def get_ss_suggested_release_by_pid(serial_dict: dict, api_creds: tuple, pid_list: list = False) -> dict:
    """
    This function takes the serial_dict which contains all serial numbers and the Cisco support API creds to
    get the suggested software release by the PID with the cisco-support library. The result of each serial
    will be added with a new key to the dict. The function returns the updated serials dict. The format of
    the serials_dict need to be as below.
    "<serial>": {
        "host": "<hostname>",
        ...
    },
    """

    # Maximum PID API parameter value
    MAX_PID = 10

    # Create the Cisco support API objec
    ss = SS(*api_creds)

    ss_vars = {
        # Backoff sleep and attempt values
        "RETRY_ATTEMPTS": 20,
        "SLEEP": 1,
        "SLEEP_MULTIPLIER": 1,
        # Cisco Support API Object and API name as string
        "api_obj": ss,
        "api_string": "ss",
    }

    # Create a list with the PIDs of all devices from the serials dict if the argument pid_list if False
    if not pid_list:
        pid_list = [
            item[1]
            for item in iterate_all(iterable=serial_dict, returned="key-value")
            if item[0] == "base_pid" or item[0] == "orderable_pid"
        ]
    # Remove pids if the match the condition for startswith
    rm_prefixes = ["UCSC-C220-M5SX", "AIR-CAP"]
    pid_list = [pid for pid in pid_list if not any(pid.startswith(prefix) for prefix in rm_prefixes)]
    # Remove pids if the match the condition for endswith
    rm_suffixes = ["AXI-E", "AXI-A"]
    pid_list = [pid for pid in pid_list if not any(pid.endswith(suffix) for suffix in rm_suffixes)]
    # Modify known wrong basePIDs to match API requirements
    # The software package suffic -A or -E can be removed as the newer basePID don't have this anymore
    # -> Makes the API calls more stable
    chg_suffixes = ["-A", "-E"]
    pid_list = [pid[:-2] if any(pid.endswith(suffix) for suffix in chg_suffixes) else pid for pid in pid_list]
    # Remove duplicated and empty pids in the final pid_list
    pid_list = [pid for pid in list(set(pid_list)) if pid]

    # API calls to the Cisco Support API suggested release by PID
    # Loop over a list with all serial numbers with a step incrementation of MAX_ITEM
    api_data = []
    for index in range(0, len(list(pid_list)), MAX_PID):
        # Create a chunk list with the maximum allowed elements specified by MAX_ITEM
        ss_vars["chunk"] = list(pid_list)[index : index + MAX_PID]
        # Part 1: Get the total number of pages for the API call of this index
        ss_vars["num_pages"] = _get_total_num_pages(**ss_vars)
        # Part 2: Get the API data for each page of the chunk list
        api_data.extend(_get_data_all_pages(**ss_vars))

    # Add the suggested software responce for each device to the serial_dict dictionary
    for record in serial_dict.values():
        # Create a list with the product ids of all devices from the serials dict
        for item in iterate_all(iterable=record, returned="key-value"):
            # Skip empty PID values
            if not item[1]:
                continue
            if item[0] == "orderable_pid":
                pid = item[1]
            elif item[0] == "base_pid":
                pid = item[1]

        # Each pid can have multiple suggestion records as the mdfId can be different for the same release
        # Therefor a list will be created to fill with multiple dictionaries if needed
        record["SSgetSuggestedReleasesByProductIDs"] = []

        # Loop over the whole suggested software response and add the suggested releases
        for item in api_data:
            # If the pid match add the suggestion to the list
            if item["product"]["basePID"] in pid:
                record["SSgetSuggestedReleasesByProductIDs"].append(item)

        # If no suggested releases were added
        if not record["SSgetSuggestedReleasesByProductIDs"]:
            record["SSgetSuggestedReleasesByProductIDs"].append("PID without Cisco software")

    return serial_dict


#### Print functions for Cisco Support API call functions in Nornir style ###################################


def print_sni_owner_coverage_by_serial_number(serial_dict: dict, verbose: bool = False) -> None:
    """
    This function prints the result of get_sni_owner_coverage_by_serial_number() in Nornir style to stdout.
    """
    task_text = "CISCO-API get owner coverage status by serial number"
    print(task_name(text=task_text))

    for sr_no, records in serial_dict.items():
        record = records["SNIgetOwnerCoverageStatusBySerialNumbers"]
        host = records["host"] if records["host"] else sr_no
        print(task_host(host=host, changed=False))
        # Verify if the serial number is associated with the CCO ID
        if "YES" in record["sr_no_owner"]:
            print(task_info(text="Verify provided CCO ID", changed=False))
            print(f"'Verify provided CCO ID' -> {_success(True)}")
            print("-> Is associated to the provided CCO ID")
        else:
            print(task_error(text="Verify provided CCO ID", changed=False))
            print(f"'Verify provided CCO ID' -> {_success(False)}")
            print("-> Is not associated to the provided CCO ID")

        # Verify if the serial is covered by a service contract
        if "YES" in record["is_covered"]:
            print(task_info(text="Verify service contract", changed=False))
            print(f"'Verify service contract' -> {_success(True)}")
            print("-> Is covered by a service contract")
            # Verify the end date of the service contract coverage
            if record["coverage_end_date"]:
                print(task_info(text="Verify service contract end date", changed=False))
                print(f"'Verify service contract end date' -> {_success(True)}")
                print(f"-> Coverage end date is {record['coverage_end_date']}")
            else:
                print(task_error(text="Verify service contract end date", changed=False))
                print(f"'Verify service contract end date' -> {_success(False)}")
                print("-> Coverage end date not available")
        else:
            print(task_error(text="Verify service contract", changed=False))
            print(f"'Verify service contract' -> {_success(False)}")
            print("-> Is not covered by a service contract")

        if verbose:
            print("\n" + json.dumps(record, indent=4))

    # Verify the whole serial_dict and exit the script in case of an found error
    verify_cisco_support_api_data(api="sni", iterable=serial_dict, verbose=False)


def print_sni_coverage_summary_by_serial_numbers(serial_dict: dict, verbose: bool = False) -> None:
    """
    This function prints the result of get_sni_coverage_summary_by_serial_numbers() in Nornir style to stdout.
    """
    task_text = "CISCO-API get coverage summary data by serial number"
    print(task_name(text=task_text))

    for sr_no, records in serial_dict.items():
        record = records["SNIgetCoverageSummaryBySerialNumbers"]
        host = records["host"] if records["host"] else sr_no
        print(task_host(host=host, changed=False))
        if "ErrorResponse" in record:
            error_response = record["ErrorResponse"]["APIError"]
            print(task_error(text=task_text, changed=False))
            print(f"'Get SNI data' -> {_success(False)}")
            print(f"-> {error_response['ErrorDescription']} ({error_response['SuggestedAction']})")
        else:
            print(task_info(text=task_text, changed=False))
            print(f"'Get SNI data' -> {_success(True)}")
            print(f"-> Orderable pid: {record['orderable_pid_list'][0]['orderable_pid']}")
            print(f"-> Customer name: {record['contract_site_customer_name']}")
            print(f"-> Customer address: {record['contract_site_address1']}")
            print(f"-> Customer city: {record['contract_site_city']}")
            print(f"-> Customer province: {record['contract_site_state_province']}")
            print(f"-> Customer country: {record['contract_site_country']}")
            print(f"-> Is covered by service contract: {record['is_covered']}")
            print(f"-> Covered product line end date: {record['covered_product_line_end_date']}")
            print(f"-> Service contract number: {record['service_contract_number']}")
            print(f"-> Service contract description: {record['service_line_descr']}")
            print(f"-> Warranty end date: {record['warranty_end_date']}")
            print(f"-> Warranty type: {record['warranty_type']}")

        if verbose:
            print("\n" + json.dumps(record, indent=4))

    # Verify the whole serial_dict and exit the script in case of an found error
    verify_cisco_support_api_data(api="sni", iterable=serial_dict, verbose=False)


def print_eox_by_serial_numbers(serial_dict: dict, verbose: bool = False) -> None:
    """
    This function prints the result of get_eox_by_serial_numbers() in Nornir style to stdout.
    """
    task_text = "CISCO-API get EoX data by serial number"
    print(task_name(text=task_text))

    for sr_no, records in serial_dict.items():
        record = records["EOXgetBySerialNumbers"]
        host = records["host"] if records["host"] else sr_no
        print(task_host(host=host, changed=False))
        if "EOXError" in record:
            if "No product IDs were found" in record["EOXError"]["ErrorDescription"]:
                print(task_error(text=task_text, changed=False))
                print(f"'Get EoX data' -> {_success(False)}")
                print(f"-> {record['EOXError']['ErrorDescription']} (Serial number does not exist)")
            elif "EOX information does not exist" in record["EOXError"]["ErrorDescription"]:
                print(task_info(text=task_text, changed=False))
                print(f"'Get EoX data' -> {_success(True)}")
                print(f"-> {record['EOXError']['ErrorDescription']}")
        else:
            print(task_info(text=task_text, changed=False))
            print(f"'Get EoX data (Last updated {record['UpdatedTimeStamp']['value']})' -> {_success(True)}")
            print(f"-> EoL product ID: {record['EOLProductID']}")
            print(f"-> Product ID description: {record['ProductIDDescription']}")
            print(f"-> EoL announcement date: {record['EOXExternalAnnouncementDate']['value']}")
            print(f"-> End of sale date: {record['EndOfSaleDate']['value']}")
            print(f"-> End of maintenance release: {record['EndOfSWMaintenanceReleases']['value']}")
            print(f"-> End of vulnerability support: {record['EndOfSecurityVulSupportDate']['value']}")
            print(f"-> Last day of support: {record['LastDateOfSupport']['value']}")

        if verbose:
            print("\n" + json.dumps(record, indent=4))

    # Verify the whole serial_dict and exit the script in case of an found error
    verify_cisco_support_api_data(api="eox", iterable=serial_dict, verbose=False)


def print_get_ss_suggested_release_by_pid(serial_dict: dict, verbose: bool = False) -> None:
    """
    This function prints the result of get_ss_suggested_release_by_pid() in Nornir style to stdout.
    """
    task_text = "CISCO-API get suggested release data by pid"
    print(task_name(text=task_text))

    for sr_no, records in serial_dict.items():
        host = records["host"] if records["host"] else sr_no
        # A Task error should not be possible as get_ss_suggested_release_by_pid() have error verification
        # and exits the script in case of an error
        print(task_host(host=host, changed=False))
        print(task_info(text=task_text, changed=False))
        print(f"'Get SS data' -> {_success(True)}")
        # As there can be multiple suggestions with the same ID and release, but only with different mdfId,
        # the no_duplicates list will be created to eliminate printing duplicate ID and release information.
        no_duplicates = []
        for item in records["SSgetSuggestedReleasesByProductIDs"]:
            if isinstance(item, str):
                if item not in no_duplicates:
                    no_duplicates.append(item)
                    print(f"-> {item}")
            elif isinstance(item, dict):
                for idx, suggestion in enumerate(item["suggestions"]):
                    idx = idx + 1
                    if suggestion["releaseFormat1"] and suggestion["releaseFormat1"] not in no_duplicates:
                        no_duplicates.append(suggestion["releaseFormat1"])
                        print(f"-> ID: {idx}, Release: {suggestion['releaseFormat1']}")
                    elif (
                        suggestion["errorDetailsResponse"]
                        and suggestion["errorDetailsResponse"]["errorDescription"] not in no_duplicates
                    ):
                        no_duplicates.append(suggestion["errorDetailsResponse"]["errorDescription"])
                        print(f"-> {suggestion['errorDetailsResponse']['errorDescription']}")
                if verbose:
                    print("\n" + json.dumps(item, indent=4))

    # Verify the whole serial_dict and exit the script in case of an found error
    verify_cisco_support_api_data(api="ss", iterable=serial_dict, verbose=False)
