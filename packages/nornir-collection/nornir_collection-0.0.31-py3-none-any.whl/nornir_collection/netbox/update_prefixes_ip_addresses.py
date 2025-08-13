#!/usr/bin/env python3
"""
This module interacts with the NetBox API to scan active network prefixes with Nmap and update
IP address, and vlan information.
The Main function is intended to import and execute by other scripts.
"""

import os
import ipaddress
import urllib.parse
from typing import Callable, Literal, Union
from concurrent.futures import ThreadPoolExecutor
import requests
import nmap
from ipfabric import IPFClient
from nornir_salt.plugins.processors import TestsProcessor
from nornir_salt.plugins.functions import FFun
from nornir_salt.plugins.tasks import scrapli_send_commands
from nornir_collection.nornir_plugins.inventory.utils import init_nornir
from nornir_collection.netbox.utils import (
    get_nb_resources,
    post_nb_resources,
    patch_nb_resources,
    delete_nb_resources,
)
from nornir_collection.utils import print_task_title, task_name, exit_error, task_result


__author__ = "Willi Kubny"
__maintainer__ = "Willi Kubny"
__version__ = "1.0"
__license__ = "MIT"
__email__ = "willi.kubny@dreyfusbank.ch"
__status__ = "Production"


def nr_ping_test(nr, hosts: list[str], ip_list: list[str], criteria: Literal["PASS", "FAIL"]) -> list[str]:
    """
    TBD
    """
    # Create the test suite list for each ip-address to ping
    tests_suite = [
        {
            "name": ip["address"],
            "task": f"ping {ipaddress.ip_interface(ip['address']).ip}",
            "test": "!contains_lines",
            "pattern": ["Success rate is 0", "VRF Mgmt-vrf does not have a usable source address"],
        }
        for ip in ip_list
    ]
    # Use NornirSalt FFun Filter-List option to filter on a list of hosts
    nr_filtered = FFun(nr, FL=hosts)
    # Add the nornir salt TestsProcessor processor
    nr_with_testsprocessor = nr_filtered.with_processors(
        [TestsProcessor(tests=tests_suite, build_per_host_tests=True)]
    )
    # Run the TestsProcessor task
    results = nr_with_testsprocessor.run(task=scrapli_send_commands, on_failed=True)
    # Create a list of the ip-addresses based on the required criteria
    result_list = [result.name for host in results for result in results[host] if result.result == criteria]
    # Create a list of ip-addresses that are part of the result_list -> This matchs the criteria PASS/FAIL
    verified_ip_list = [ip for ip in ip_list if ip["address"] in result_list]

    return verified_ip_list


def load_netbox_data(task_text: str, nb_api_url: str, query: dict) -> list[dict]:
    """
    Load NetBox data using the provided task text, NetBox API URL, and query parameters.
    If no data is returned, the script will exit with an error message.

    Args:
        task_text (str): The task text to be printed.
        nb_api_url (str): The URL of the NetBox API.
        query (dict): The query parameters to be passed to the NetBox API.

    Returns:
        list[dict]: A list of dictionaries containing the NetBox API data.
    """
    # Print the task name
    print(task_name(text=task_text))

    # Get all NetBox API data
    nb_data = get_nb_resources(url=nb_api_url, params=query)

    # Exit the script if the nb_data list is empty
    if not nb_data:
        exit_error(task_text=f"{task_text} Failed", msg=["-> No Data returned from NetBox API"])

    # Print the task result
    print(task_result(text=task_text, changed=False, level_name="INFO"))
    print(f"'{task_text}' -> NetBoxResponse <Success: True>")
    print(f"-> NetBox API response count: {len(nb_data)}")

    return nb_data


def base_url(url: str, with_path: bool = False) -> str:
    """
    Returns the base URL of a given URL.

    Args:
        url (str): The input URL.
        with_path (bool, optional): Whether to include the path in the base URL. Defaults to False.

    Returns:
        str: The base URL of the input URL.
    """
    parsed = urllib.parse.urlparse(url)
    path = "/".join(parsed.path.split("/")[:-1]) if with_path else ""
    parsed = parsed._replace(path=path)
    parsed = parsed._replace(params="")
    parsed = parsed._replace(query="")
    parsed = parsed._replace(fragment="")

    return parsed.geturl()


def make_markdown_table(array: list[list[str]]) -> str:
    """
    Create a markdown table from a 2D array.

    Args:
        array (list[list[str]]): The 2D array containing the table data.

    Returns:
        str: The generated markdown table.
    """
    nl = "\n"
    markdown = f"| {' | '.join(array[0])} |"
    markdown += nl
    markdown += f"| {' | '.join(['---'] * len(array[0]))} |"
    markdown += nl
    for entry in array[1:]:
        markdown += f"| {' | '.join(entry)} |{nl}"

    return markdown


def create_nb_response_result(
    resp: requests.Response,
    nb_type: Literal["ip", "vlan"],
    data: Union[dict, list],
    task_text: str,
    text: str,
    ds: Literal["nmap", "ip-fabric"] = None,
) -> tuple:
    """
    Verify the NetBox response and return the result.
    For active scanned IP addresses of a prefixthe following fields are updated:
        * Status, DNS Name, Ports
    For all ip addresses  of a prefix the following fields are updated:
        * VRF, Tenant, Tags, Location
    For a VLAN associated to a prefix the following fields are updated:
        * Status, Tenant, Tags, Location
    For a VLAN not associated to a prefix the following fields are updated:
        * Tags

    Args:
        resp (requests.Response): The response object from the NetBox API.
        data Union[dict, list]: A list of ip addresses or a dictionary containing the prefix information.
        task_text (str): The task text.
        text (str): The additional task text for the first line of the task result.

    Returns:
        tuple: A tuple containing the results and a boolean indicating success or failure.
    """
    # Create list to collect the results
    result = []

    # Verify the response code and print the result
    if resp.status_code in [200, 201, 204]:
        # Create a list of fields that have been updated
        updated_fields = []

        # If data is a list of ip addresses from a active scanned prefix of IP-Fabric
        if nb_type in "ip" and isinstance(data, list):
            # Create a list of ip addresses that have been updated
            for ip in data:
                address = ip["address"]
                dns_name = ip["dns_name"] if "dns_name" in ip and ip["dns_name"] else "None"
                if ds == "nmap":
                    ports = (
                        ", ".join([str(p) for p in ip["ports"]]) if "ports" in ip and ip["ports"] else "None"
                    )
                    updated_fields.append(f"  - {address} (DNS: {dns_name}, Ports: {ports})")
                else:
                    updated_fields.append(f"  - {address} (DNS: {dns_name})")
        # If data is a dictionary containing the prefix or information vlan associated with a prefix
        elif nb_type in ("ip", "vlan") and isinstance(data, dict):
            # If the response json contains the key 'vid' the response is from a vlan and has no VRF
            if "vid" in resp.json():
                updated_fields.append(f"  - Status: {data['status']['label']}")
            # It's the response from a ip-address and ha a VRF
            else:
                updated_fields.append(f"  - VRF: {data['vrf'] if data['vrf'] else 'Global'}")
            updated_fields.extend(
                [
                    f"  - Tenant: {data['tenant']['name'] if data['tenant'] else 'None'}",
                    f"  - Tags: {(', '.join([i['name'] for i in data['tags']])) or 'None'}",
                    f"  - Location: {', '.join(list(data['custom_fields']['ipam_location'])).upper() or 'None'}",  # noqa: E501
                ]
            )
        # If the type is 'vlan' and data is empty
        elif nb_type == "vlan" and not data:
            updated_fields.append("  - Tags: L2 Only")
        else:
            result = [
                f"{task_result(text=task_text, changed=True, level_name='ERROR')}\n"
                + f"'{task_text}' -> NetBoxResponse <Success: False>\n-> {text}\n"
                + "Check the source code as the data parameter is neither a list nor a dictionary!"
            ]
            return result, True

        # Add the result to the list
        updated_fields = "\n".join(updated_fields)
        result = [
            f"{task_result(text=task_text, changed=True, level_name='INFO')}\n"
            + f"'{task_text}' -> NetBoxResponse <Success: True>\n-> {text}\n"
            + f"{updated_fields}"
        ]
        return result, False

    result = [
        f"{task_result(text=task_text, changed=False, level_name='ERROR')}\n"
        + f"'{task_text}' -> NetBoxResponse <Success: False>\n"
        + f"-> Response Status Code: {resp.status_code}\n"
        + f"-> Response Json:\n{resp.json()}"
    ]
    return result, True


def create_nb_ip_payload(
    parent_prefix: dict, data: list, ds: Literal["nmap", "ip-fabric"] = None, desired_status: str = None
) -> dict:
    """
    Create a NetBox REST API payload.
    To add or delete IP addresses of an active scanned prefix or update the following fields:
        * Status, DNS Name, Open Ports
    To update all IP addresses or the vlan associated with a prefix with the following information:
        * VRF, Tenant, Tags, Location

    Args:
        parent_prefix (dict): The parent prefix information.
        data (list[dict]): The list of IP addresses information.
        desired_status (str): The desired status for the IP addresses.

    Returns:
        dict: The NetBox payload for the REST API.
    """
    # Create the payload list of dicts
    payload = []

    for ip in data:
        # Create an empty dict for the payload item
        item = {}
        # Add the 'id' if it exists (not needed for post requests)
        if "id" in ip:
            item["id"] = ip["id"]
        # If desired_status is not None, the payload is for active scanned ip addresses or IP-Fabric
        if desired_status:
            # Add the 'address' and 'status' to the payload
            item["address"] = ip["address"]
            item["status"] = desired_status
            # If the ip address exists in the datasource_ips list
            datasource_ip = [x for x in parent_prefix["datasource_ips"] if x["address"] == ip["address"]]
            # Add the 'dns_name'
            item["dns_name"] = datasource_ip[0]["dns_name"] if datasource_ip else ""
            # If it's a nmap scan format the 'ports' as a Markdown table and add the 'ports'
            if ds == "nmap":
                if datasource_ip and datasource_ip[0]["ports"]:
                    md = [["Port", "State", "Service"]]
                    md.extend(
                        [[f"{k}/tcp", v["state"], v["name"]] for k, v in datasource_ip[0]["ports"].items()]
                    )
                    item["custom_fields"] = {"ipam_ports": make_markdown_table(md)}
                else:
                    item["custom_fields"] = {"ipam_ports": None}
        # If the desired_status is None, the payload is for all ip addresses of a prefix
        else:
            # Add the 'vrf' to the payload
            item["vrf"] = parent_prefix["vrf"]["id"] if parent_prefix["vrf"] is not None else None
            # Add the 'tenant' to the payload
            item["tenant"] = parent_prefix["tenant"]["id"] if parent_prefix["tenant"] is not None else None
            # Add the 'tags' of the parent prefix to the payload
            item["tags"] = [tag["id"] for tag in parent_prefix["tags"]]
            # Add the custom field 'ipam_location' of the parent prefix to the payload
            item["custom_fields"] = {"ipam_location": parent_prefix["custom_fields"]["ipam_location"]}

        # Add the item to the payload list
        payload.append(item)

    return payload


def nmap_scan_host_ip_or_subnet(hosts: str) -> list:
    """
    TBD
    """
    # Create an ip-interface object from the hosts argument.
    # Can be a host ip-address with CIDR netmask or a network prefix with CIDR netmask
    ip_iface = ipaddress.ip_interface(hosts)
    # Get the prefix length from the prefix
    prefixlen = ip_iface.network.prefixlen
    # Set the nmap scan arguments
    arguments = "-PE -PP -PA21 -PS80,443,3389 -PU161,40125 --source-port 53"

    # If the ip-address is the network address of the prefix, then it's a whole prefix to scan
    if ip_iface.ip == ip_iface.network.network_address:
        # Add the the nmap arguments that the network and broadcast address should be excluded from the scan
        arguments += f" --exclude {ip_iface.network.network_address},{ip_iface.network.broadcast_address}"
        # Scan the whole prefix
        scan_target = str(ip_iface.network)
    else:
        # Scan only the host ip-address
        scan_target = str(ip_iface.ip)

    # Nmap ARP scan and add a list of active ip-addresses and other details to the list
    nm = nmap.PortScanner()
    nm.scan(hosts=scan_target, arguments=arguments, sudo=True)
    if nm.all_hosts():
        nmap_scan_result = [
            {
                "address": f"{nm[host]['addresses']['ipv4']}/{prefixlen}",
                "dns_name": nm[host]["hostnames"][0]["name"],
                "ports": nm[host]["tcp"] if "tcp" in nm[host] else {},
            }
            for host in nm.all_hosts()
        ]
    else:
        nmap_scan_result = []

    return nmap_scan_result


def nmap_double_check_ips(ip_list: dict, criteria: Literal["PASS", "FAIL"]) -> list:
    """
    TBD
    """
    verified_ips = []
    # Nmap scan ip-addresses of the ip list
    for ip in ip_list:
        # Scan the prefix with nmap
        scan_result = nmap_scan_host_ip_or_subnet(hosts=ip["address"])
        # Add the nmap scan result to the inactive_ips list with the ID of the ip-address
        if scan_result and criteria == "PASS":
            # As a single ip-address is scanned the scan_result can have only one list item
            verified_ips.append({"id": ip["id"], **scan_result[0]})
        elif not scan_result and criteria == "FAIL":
            # As the single ip-address is not reachable, add the ip-address to the verified_ips list
            verified_ips.append(ip)

    # Return the active ip-addresses list
    return verified_ips


def get_ipfabric_ip_addresses_for_prefix(prefix: dict) -> tuple:
    """
    TBD
    """
    # Connect to IP-Fabric
    ipf = IPFClient(
        base_url=os.environ["IPF_URL"], auth=os.environ["IPF_TOKEN"], snapshot_id="$last", verify=False
    )
    # Get the prefix length from the prefix
    prefixlen = ipaddress.ip_network(prefix["prefix"]).prefixlen
    # Get all ip-addresses of the prefix from the IP-Fabric technology arp table
    # Remove duplicate ip-addresses as the arp table can contain multiple entries for the same ip-address
    filters = {"ip": ["cidr", prefix["prefix"]], "proxy": ["eq", False]}
    arp_ip_list = list(set([x["ip"] for x in ipf.technology.addressing.arp_table.all(filters=filters)]))
    # Get all ip-addresses of the prefix from the IP-Fabric inventory managed ipv4 table
    filters = {"ip": ["cidr", prefix["prefix"]]}
    managed_ipv4_ip_list = list(
        set([x["ip"] for x in ipf.technology.addressing.managed_ip_ipv4.all(filters=filters, columns=["ip"])])
    )
    # Get all ip-addresses of the prefix from the IP-Fabric inventory interface table
    filters = {"loginIp": ["cidr", prefix["prefix"]]}
    interface_ip_list = list(
        set([x["loginIp"] for x in ipf.inventory.interfaces.all(filters=filters, columns=["loginIp"])])
    )
    # Get all ip-addresses of the prefix from the IP-Fabric inventory hosts table
    # Set the ip-address as key to access the dict easier later
    filters = {"ip": ["cidr", prefix["prefix"]]}
    columns = ["ip", "dnsName"]
    host_ip_dict = {
        x["ip"]: x["dnsName"] or "" for x in ipf.inventory.hosts.all(filters=filters, columns=columns)
    }
    host_ip_list = list(host_ip_dict.keys())
    # Combine all ip-addresses lists and remove duplicates
    all_ips = list(set(arp_ip_list + managed_ipv4_ip_list + interface_ip_list + host_ip_list))
    # Add a list of all ip-addresses and other details to prefix
    ipf_ip_address_result = [
        {
            "address": f"{ip}/{prefixlen}",
            "dns_name": host_ip_dict[ip] if ip in host_ip_dict.keys() else "",
            "ports": {},
        }
        for ip in all_ips
    ]

    return ipf_ip_address_result


def get_nb_ips_and_external_datasource(nb_url: str, prefix: dict, ds: Literal["nmap", "ip-fabric"]) -> tuple:
    """
    Get NetBox IP addresses and scan a prefix with nmap or get the data from IP-Fabric.
    This function can be used within a ThreadPoolExecutor.

    Args:
        nb_url (str): The URL of the NetBox instance.
        prefix (dict): The prefix to scan and retrieve IP addresses for.
        ds (Literal["nmap", "ip-fabric"]): The datasource to use for the IP addresses.

    Returns:
        tuple: A tuple containing the result list and the updated prefix dictionary.
    """
    # Create list to collect the results
    failed = False
    result = []

    # Get the ip-addresses of the prefix from the datasource
    if ds == "nmap":
        # Scan the prefix with nmap
        prefix["datasource_ips"] = nmap_scan_host_ip_or_subnet(hosts=prefix["prefix"])

        # Print the task result
        text = f"Nmap Scan Prefix {prefix['prefix']} for active IP-Addresses"
        result.append(
            f"{task_result(text=text, changed=False, level_name='INFO')}\n"
            + f"'{text}' -> NetBoxResponse <Success: True>\n"
            + f"-> Nmap prefix scan ip-address count: {len(prefix['datasource_ips'])}"
        )
    elif ds == "ip-fabric":
        # Get the ip-addresses from the IP-Fabric
        prefix["datasource_ips"] = get_ipfabric_ip_addresses_for_prefix(prefix=prefix)

        # Print the task result
        text = f"IP-Fabric Get Data for Prefix {prefix['prefix']} IP-Addresses"
        result.append(
            f"{task_result(text=text, changed=False, level_name='INFO')}\n"
            + f"'{text}' -> IPFResponse <Success: True>\n"
            + f"-> IP-Fabric prefix ip-address count: {len(prefix['datasource_ips'])}"
        )
    else:
        # Invalid datasource
        failed = True
        text = f"Get NetBox IP-Addresses of Prefix {prefix['prefix']}"
        result.append(
            f"{task_result(text=text, changed=False, level_name='ERROR')}\n"
            + f"'{text}' -> NetBoxResponse <Success: True>\n"
            + f"-> Invalid Datasource '{ds}'\n"
        )
        return result, prefix, failed

    #### Get NetBox ip-addresses ############################################################################

    # Add a list of dicts (id & address) of all NetBox ip-addresses for prefix
    query = {"parent": prefix["prefix"]}
    resp = get_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", params=query)
    prefix["all_ips"] = [{"id": i["id"], "address": i["address"]} for i in resp] if resp else []

    # Add a list of dicts (id & address) of NetBox ip-addresses with the status 'auto_discovered' for prefix
    query = {"parent": prefix["prefix"], "status": "auto_discovered"}
    resp = get_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", params=query)
    prefix["discovered_ips"] = [{"id": i["id"], "address": i["address"]} for i in resp] if resp else []

    # Add a list of dicts (id & address) of NetBox ip-addresses with the status 'reserved' for prefix
    query = {"parent": prefix["prefix"], "status": "reserved"}
    resp = get_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", params=query)
    prefix["reserved_ips"] = [{"id": i["id"], "address": i["address"]} for i in resp] if resp else []

    # Add a list of dicts (id & address) of NetBox ip-addresses with the status 'active' for prefix
    query = {"parent": prefix["prefix"], "status": "active"}
    resp = get_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", params=query)
    prefix["active_ips"] = [{"id": i["id"], "address": i["address"]} for i in resp] if resp else []

    # Add a list of dicts (id & address) of NetBox ip-addresses with the status 'inactive' for prefix
    query = {"parent": prefix["prefix"], "status": "inactive"}
    resp = get_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", params=query)
    prefix["inactive_ips"] = [{"id": i["id"], "address": i["address"]} for i in resp] if resp else []

    # Add a list of dicts (id & address) of NetBox ip-addresses with the status 'deprecated' for prefix
    query = {"parent": prefix["prefix"], "status": "deprecated"}
    resp = get_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", params=query)
    prefix["deprecated_ips"] = [{"id": i["id"], "address": i["address"]} for i in resp] if resp else []

    # Print the task result
    text = f"Get NetBox IP-Addresses of Prefix {prefix['prefix']}"
    result.append(
        f"{task_result(text=text, changed=False, level_name='INFO')}\n"
        + f"'{text}' -> NetBoxResponse <Success: True>\n"
        + f"-> All ip-address count: {len(prefix['all_ips'])}\n"
        + f"-> Auto-Discovered ip-address count: {len(prefix['discovered_ips'])}\n"
        + f"-> Reserved ip-address count: {len(prefix['reserved_ips'])}\n"
        + f"-> Active ip-address count: {len(prefix['active_ips'])}\n"
        + f"-> Inactive ip-address count: {len(prefix['inactive_ips'])}\n"
        + f"-> Deprecated ip-address count: {len(prefix['deprecated_ips'])}",
    )

    return result, prefix, failed


def create_ip_list(loop_list: list[dict], check_list: list[dict], is_in_both: bool) -> list[dict]:
    """
    Create a list of IP addresses with additional information based on the verification list and Nmap list.

    Args:
        loop_list (list[dict]): The list of IP addresses dicts to verify.
        check_list (list[dict]): The list of IP addresses dicts from Nmap scan.
        is_in_both (bool): Flag indicating whether the IP addresses should be in the Nmap list.

    Returns:
        list[dict]: The updated list of IP addresses with additional information.

    """
    # Create a list to collect the ip-addresses
    ip_list = []
    # Loop through the loop_list and check if the ip-address is in the check_list
    if is_in_both:
        for ip in loop_list:
            for x in check_list:
                if ip["address"] == x["address"]:
                    ip_list.append({**ip, "dns_name": x["dns_name"], "ports": x["ports"]})
    # Loop through the loop_list and check if the ip-address is not in the check_list
    else:
        for ip in loop_list:
            if ip["address"] not in [x["address"] for x in check_list]:
                ip_list.append(ip)

    return ip_list


def update_discovered_ip_addresses(nb_url: str, prefix: dict, ds: Literal["nmap", "ip-fabric"]) -> tuple:
    """
    Posts new auto-discovered IP addresses to NetBox.

    Args:
        nb_url (str): The URL of the NetBox instance.
        prefix (dict): The prefix dictionary containing the IP addresses.

    Returns:
        tuple: A tuple containing the result and the status (True if IPs were added, False otherwise).
    """
    # Set the default result and failed boolian
    result = []
    failed = False
    task_text = "Add Auto-Discovered IP-Addresses"

    # Add nmap scan ip-addresses that are not in the existing ip-addresses dict
    add_ips = create_ip_list(
        loop_list=prefix["datasource_ips"], check_list=prefix["all_ips"], is_in_both=False
    )

    # If ip-addresses have been found
    if add_ips:
        # Create the payload to create the ip-addresses
        payload = create_nb_ip_payload(
            parent_prefix=prefix, data=add_ips, ds=ds, desired_status="auto_discovered"
        )
        # POST request to update the ip-addresses
        resp = post_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", payload=payload)

        # Verify the response code and print the result
        text = "The following 'Auto-Discovered' ip-addresses had been added:"
        # The function returns the result list and True if the response is successful else False
        sub_result, sub_failed = create_nb_response_result(
            resp=resp, nb_type="ip", data=add_ips, ds=ds, task_text=task_text, text=text
        )
        if "Response Json:" in sub_result[0]:
            sub_result[0] += f"\n** DEBUG **\nPayload:\n{payload}\nResponse:\n{resp.json()}\n** DEBUG **\n"
        result.extend(sub_result)
        failed = True if sub_failed else failed

    # Update the ip-addresses with the status 'auto_discovered' that are part of the datasource list
    update_ips = create_ip_list(
        loop_list=prefix["discovered_ips"], check_list=prefix["datasource_ips"], is_in_both=True
    )

    # If ip-addresses have been found
    if update_ips:
        # Create the payload to create the ip-addresses
        payload = create_nb_ip_payload(
            parent_prefix=prefix, data=update_ips, ds=ds, desired_status="auto_discovered"
        )
        # PATCH request to update the ip-addresses
        resp = patch_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", payload=payload)

        # Verify the response code and print the result
        text = "The following 'Auto-Discovered' ip-addresses had been updated:"
        # The function returns the result list and True if the response is successful else False
        sub_result, sub_failed = create_nb_response_result(
            resp=resp, nb_type="ip", data=update_ips, ds=ds, task_text=task_text, text=text
        )
        result.extend(sub_result)
        failed = True if sub_failed else failed

    return result, failed


def delete_inactive_auto_discovered_ip_addresses(
    nb_url: str, prefix: dict, ds: Literal["nmap", "ip-fabric"]
) -> tuple:
    """
    Deletes inactive auto-discovered IP addresses from NetBox.

    Args:
        nb_url (str): The URL of the NetBox instance.
        prefix (dict): The prefix dictionary containing the IP addresses.

    Returns:
        tuple: A tuple containing the result and the status (True if IPs were deleted, False otherwise).
    """
    # Set the default result and failed status
    result = []
    failed = False
    task_text = "Delete Auto-Discovered IP-Addresses"

    # Delete the ip-addresses with the status 'auto_discovered' that are not in the datasource list
    delete_ips = create_ip_list(
        loop_list=prefix["discovered_ips"], check_list=prefix["datasource_ips"], is_in_both=False
    )

    # If ip-addresses have been found
    if delete_ips:
        # PATCH request to delete the ip-addresses
        # The delete_ips list contains already 'id' and 'address' and can be used as payload
        resp = delete_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", payload=delete_ips)

        # Verify the response code and print the result
        text = "The following 'Auto-Discovered' ip-addresses had been deleted:"
        # The function returns the result list and True if the response is successful else False
        result, failed = create_nb_response_result(
            resp=resp, nb_type="ip", data=delete_ips, ds=ds, task_text=task_text, text=text
        )

    return result, failed


def update_reserved_ip_addresses(nb_url: str, prefix: dict, ds: Literal["nmap", "ip-fabric"]) -> tuple:
    """
    Updates the status of reserved IP addresses in NetBox if they are reachable by nmap.

    Args:
        nb_url (str): The URL of the NetBox instance.
        prefix (dict): The prefix dictionary containing the IP addresses.

    Returns:
        tuple: A tuple containing the result and the status (True if IPs were updated, False otherwise).
    """
    # Set the default result and failed status
    result = []
    failed = False
    task_text = "Update Reserved IP-Addresses Status"

    # Update the ip-addresses with the status 'reserved' that are part of the datacenter list
    update_ips = create_ip_list(
        loop_list=prefix["reserved_ips"], check_list=prefix["datasource_ips"], is_in_both=True
    )

    # If ip-addresses have been found
    if update_ips:
        # Create the payload to update the ip-addresses
        payload = create_nb_ip_payload(parent_prefix=prefix, data=update_ips, ds=ds, desired_status="active")
        # PATCH request to update the ip-addresses
        resp = patch_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", payload=payload)

        # Verify the response code and print the result
        text = "The following 'Reserved' ip-addresses had been set to status 'Active':"
        # The function returns the result list and True if the response is successful else False
        result, failed = create_nb_response_result(
            resp=resp, nb_type="ip", data=update_ips, ds=ds, task_text=task_text, text=text
        )

    return result, failed


def update_inactive_ip_addresses(nr, nb_url: str, prefix: dict, ds: Literal["nmap", "ip-fabric"]) -> tuple:
    """
    Updates the status of inactive IP addresses in NetBox if they are reachable by nmap.

    Args:
        nb_url (str): The URL of the NetBox instance.
        prefix (dict): The prefix dictionary containing the IP addresses.

    Returns:
        tuple: A tuple containing the result and the status (True if IPs were updated, False otherwise).
    """
    # Set the default result and failed status
    result = []
    failed = False
    task_text = "Update Inactive IP-Addresses Status"

    # Update the ip-addresses with the status 'inactive' that are part of the datasource list
    active_ips = create_ip_list(
        loop_list=prefix["inactive_ips"], check_list=prefix["datasource_ips"], is_in_both=True
    )
    # Double-check ip-addresses with the status 'inactive' that are not part of the datasource list
    may_active_ips = create_ip_list(
        loop_list=prefix["inactive_ips"], check_list=prefix["datasource_ips"], is_in_both=False
    )
    if may_active_ips and ds == "ip-fabric":
        # Double-check ip-addresses which can be scanned with nmap (all except Tier-3 and Tier-4)
        if ds == "ip-fabric" and (prefix["tenant"]["slug"] not in ("tier-3", "tier-4")):
            # Nmap scan ip-addresses of the may_active_ips list and add the result to the active_ips list
            active_ips.extend(nmap_double_check_ips(ip_list=may_active_ips, criteria="PASS"))
        # Double-check ip-addresses with a Ping from the core-switch (Tier-3 and Tier-4)
        elif ds == "ip-fabric" and (prefix["tenant"]["slug"] in ("tier-3", "tier-4")):
            t3_core_sw = ["T3-AES99-SWRSU1"]
            active_ips.extend(nr_ping_test(nr=nr, hosts=t3_core_sw, ip_list=may_active_ips, criteria="PASS"))

    # If ip-addresses have been found
    if active_ips:
        # Create the payload to update the ip-addresses
        payload = create_nb_ip_payload(parent_prefix=prefix, data=active_ips, ds=ds, desired_status="active")
        # PATCH request to update the ip-addresses
        resp = patch_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", payload=payload)

        # Verify the response code and print the result
        text = "The following 'Inactive' ip-addresses had been set to status 'Active':"
        # The function returns the result list and True if the response is successful else False
        result, failed = create_nb_response_result(
            resp=resp, nb_type="ip", data=active_ips, ds=ds, task_text=task_text, text=text
        )

    return result, failed


def update_active_ip_addresses(
    nr, nb_url: str, prefix: dict, overwrite_active: list[str], ds: Literal["nmap", "ip-fabric"]
) -> tuple:
    """
    Updates the status of active IP addresses in NetBox if they are not reachable by nmap.

    Args:
        nb_url (str): The URL of the NetBox instance.
        prefix (dict): The prefix dictionary containing the IP addresses.

    Returns:
        tuple: A tuple containing the result and the status (True if IPs were updated, False otherwise).
    """
    # Set the default result and failed status
    result = []
    failed = False
    task_text = "Update Active IP-Addresses Status"

    # Update the ip-addresses with the status 'active' that are part of the datacenter list
    active_ips = create_ip_list(
        loop_list=prefix["active_ips"], check_list=prefix["datasource_ips"], is_in_both=True
    )

    # If ip-addresses have been found
    if active_ips:
        # Create the payload to update the ip-addresses
        payload = create_nb_ip_payload(parent_prefix=prefix, data=active_ips, ds=ds, desired_status="active")
        # PATCH request to update the ip-addresses
        resp = patch_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", payload=payload)

        # Verify the response code and print the result
        text = "The following 'Active' ip-addresses had been updated:"
        # The function returns the result list and True if the response is successful else False
        sub_result, sub_failed = create_nb_response_result(
            resp=resp, nb_type="ip", data=active_ips, ds=ds, task_text=task_text, text=text
        )
        result.extend(sub_result)
        if sub_failed:
            failed = True
            result.append(f"-> Data for Payload:\n{active_ips}")
            result.append(f"-> Payload:\n{payload}")

    # Update the ip-addresses with the status 'active' that are not part of the datacenter list
    may_inactive = create_ip_list(
        loop_list=prefix["active_ips"], check_list=prefix["datasource_ips"], is_in_both=False
    )
    if may_inactive and ds == "ip-fabric":
        # Double-check ip-addresses which can be scanned with nmap (all except Tier-3 and Tier-4)
        if prefix["tenant"]["slug"] not in ("tier-3", "tier-4"):
            # Nmap scan ip-addresses of the may_inactive list
            may_inactive = nmap_double_check_ips(ip_list=may_inactive, criteria="FAIL")
        # Double-check ip-addresses with a Ping from the core-switch (Tier-3 and Tier-4)
        elif prefix["tenant"]["slug"] in ("tier-3", "tier-4"):
            t3_core_sw = ["T3-AES99-SWRSU1"]
            may_inactive = nr_ping_test(nr=nr, hosts=t3_core_sw, ip_list=may_inactive, criteria="FAIL")

    # Create a new list to exclude the overwrite_active ip-addresses
    inactive_ips = [ip for ip in may_inactive if ip["address"] not in overwrite_active]

    # If ip-addresses have been found
    if inactive_ips:
        # Create the payload to update the ip-addresses
        payload = create_nb_ip_payload(
            parent_prefix=prefix, data=inactive_ips, ds=ds, desired_status="inactive"
        )
        # PATCH request to update the ip-addresses
        resp = patch_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", payload=payload)

        # Verify the response code and print the result
        text = "The following 'Active' ip-addresses had been set to status 'Inactive':"
        # The function returns the result list and True if the response is successful else False
        sub_result, sub_failed = create_nb_response_result(
            resp=resp, nb_type="ip", data=inactive_ips, ds=ds, task_text=task_text, text=text
        )
        result.extend(sub_result)
        if sub_failed:
            failed = True
            result.append(f"-> Data for Payload:\n{inactive_ips}")
            result.append(f"-> Payload:\n{payload}")

    return result, failed


def set_results_changed_failed(results, result, changed, sub_failed, failed) -> tuple:
    """
    Sets the values of 'changed' and 'failed' based on the given 'result' and 'sub_failed' values.

    Parameters:
        results (list): The list of results to be extended with the 'result'.
        result (list): The result to be added to the 'results' list.
        changed (bool): The current value of 'changed'.
        sub_failed (bool): The value indicating if a sub-task has failed.
        failed (bool): The current value of 'failed'.

    Returns:
        tuple: A tuple containing the updated 'results', 'changed', and 'failed' values.
    """
    results.extend(result)
    changed = True if result else changed
    failed = True if sub_failed else failed

    return results, changed, failed


def update_netbox_prefix_ip_addresses(prefix: list, *args) -> tuple:
    """
    This function can be used within a ThreadPoolExecutor. Update the IP addresses of a active NetBox prefix
    with the following information:
    - Status
    - DNS-Name
    - Open Ports

    Args:
        prefix (dict): The prefix to update, containing information about the prefix.
        nb_url (str): The URL of the NetBox instance.

    Returns:
        list: A tuple of results from the update tasks and a boolean indicating if the task failed.
    """
    # Create a list to collect the task results
    results = []
    # Set the datasource by the first arg ('namp' or 'ip-fabric') and make sure its a string
    ds = str(args[0])
    # Set the ip-address list to overwrite the status as active by the second arg and make sure its a list
    overwrite_active = list(args[1])
    # Set the Nornir config file by the third arg
    nr_config = args[2]
    # Boolian to check if any ip-addresses have been changed and the overall failed status
    changed = False
    failed = False

    # Print the task title
    results.append(task_name(text=f"Update NetBox IP-Addresses of Prefix {prefix['prefix']}"))

    # Initialize, transform and filter the Nornir inventory are return the filtered Nornir object
    # Define data to load from NetBox in addition to the base Nornir inventory plugin
    add_netbox_data = {"load_virtual_chassis_data": True}
    nr = init_nornir(config_file=nr_config, add_netbox_data=add_netbox_data, silent=True)
    # Get the NetBox url from the inventory options
    nb_url = nr.config.inventory.options["nb_url"]

    # Scan the prefix with nmap and add the list to the prefix dict or get the ip-addresses from IP-Fabric
    result, prefix, failed = get_nb_ips_and_external_datasource(nb_url=nb_url, prefix=prefix, ds=ds)
    results.extend(result)
    if failed:
        return results, failed

    # Add new 'auto-discovered' ip-addresses
    result, sub_failed = update_discovered_ip_addresses(nb_url=nb_url, prefix=prefix, ds=ds)
    results, changed, failed = set_results_changed_failed(results, result, changed, sub_failed, failed)

    # Delete inactive 'auto-discovered' ip-addresses
    result, sub_failed = delete_inactive_auto_discovered_ip_addresses(nb_url=nb_url, prefix=prefix, ds=ds)
    results, changed, failed = set_results_changed_failed(results, result, changed, sub_failed, failed)

    # Update 'reserved' ip-addresses -> set status to 'active'
    result, sub_failed = update_reserved_ip_addresses(nb_url=nb_url, prefix=prefix, ds=ds)
    results, changed, failed = set_results_changed_failed(results, result, changed, sub_failed, failed)

    # Update 'inactive' ip-addresses -> set status to 'active' (with partial double-check)
    result, sub_failed = update_inactive_ip_addresses(nr=nr, nb_url=nb_url, prefix=prefix, ds=ds)
    results, changed, failed = set_results_changed_failed(results, result, changed, sub_failed, failed)

    # Update 'active' ip-addresses -> set status to 'active' or 'inactive' (with partial double-check)
    result, sub_failed = update_active_ip_addresses(
        nr=nr, nb_url=nb_url, prefix=prefix, overwrite_active=overwrite_active, ds=ds
    )
    results, changed, failed = set_results_changed_failed(results, result, changed, sub_failed, failed)

    # Print a message if no ip-addresses have been changed
    if not changed:
        text = f"No IP-Address to update for Prefix {prefix['prefix']}"
        results.append(
            f"{task_result(text=text, changed=False, level_name='INFO')}\n"
            + f"'{text}' -> NetBoxResponse <Success: True>\n"
            + f"-> {prefix['prefix']} have no ip-addresses to add, update or delete"
        )

    return results, failed


def update_netbox_ip_address_switchport(prefix: list, *args) -> tuple:
    """
    This function can be used within a ThreadPoolExecutor. Update additional the IP addresses of a active
    NetBox Prefix with the following information about where this IP-Address is activ in the network:
    - Switch
    - Switchport
    - Switchport Config-Mode

    Args:
        prefix (dict): The prefix to update, containing information about the prefix.
        nb_url (str): The URL of the NetBox instance.

    Returns:
        list: A tuple of results from the update tasks and a boolean indicating if the task failed.
    """
    # Create a list to collect the task results
    results = []
    # Boolian to check if any ip-addresses have been changed and the overall failed status
    failed = False
    # Set the IP-Fabric MAC addresses by the first arg
    ipf_edge_mac_dict = args[0]
    # Set the Nornir object by the second arg
    nr = args[1]

    # Print the task title
    results.append(task_name(text=f"Update NetBox IP-Addresses of Prefix {prefix['prefix']}"))

    # Get the base url of the NetBox instance
    nb_url = base_url(url=prefix["url"], with_path=False)

    # Add a list of dicts (id & address) of NetBox ip-addresses with the status 'active' for prefix
    query = {"parent": prefix["prefix"], "status": "active"}
    resp = get_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", params=query)
    prefix["active_ips"] = [{"id": i["id"], "address": i["address"]} for i in resp] if resp else []

    # Print the task result
    text = f"Get NetBox IP-Addresses of Prefix {prefix['prefix']}"
    if len(prefix["active_ips"]) == 0:
        results.append(
            f"{task_result(text=text, changed=False, level_name='INFO')}\n"
            + f"'{text}' -> NetBoxResponse <Success: True>\n"
            + f"-> Prefix {prefix['prefix']} have no ip-addresses to update"
        )
        # Return the results and status
        return results, failed
    results.append(
        f"{task_result(text=text, changed=False, level_name='INFO')}\n"
        + f"'{text}' -> NetBoxResponse <Success: True>\n"
        + f"-> NetBox active ip-address count: {len(prefix['active_ips'])}"
    )

    # Connect to IP-Fabric
    ipf = IPFClient(
        base_url=os.environ["IPF_URL"], auth=os.environ["IPF_TOKEN"], snapshot_id="$last", verify=False
    )

    # Get the prefix length from the prefix
    prefixlen = ipaddress.ip_network(prefix["prefix"]).prefixlen

    # Create some variables to store the data later
    ip_detail_dict = {}
    updated_fields = []
    # Get all ip-addresses and mac-addresses of the prefix from the IP-Fabric technology arp table
    filters = {"ip": ["cidr", prefix["prefix"]], "proxy": ["eq", False]}
    columns = ["ip", "mac"]
    ipf_arp_table = ipf.technology.addressing.arp_table.all(filters=filters, columns=columns)
    # Create a mac-address dict only for the ip-addresses that are in the ipf_arp_table for the prefix
    ipf_arp_table = [x for x in ipf_arp_table if x["mac"] in ipf_edge_mac_dict.keys()]
    results.append(f"-> IP-Fabric edge ip-address count: {len(ipf_arp_table)}")

    for x in ipf_arp_table:
        # Set some variables for easier code reading
        switch = ipf_edge_mac_dict[x["mac"]]["hostname"]
        switch_id = nr.inventory.hosts[switch].get("id")
        switchport = ipf_edge_mac_dict[x["mac"]]["intName"]
        # Get the switchport information from IPF
        ipf_switchport = ipf.technology.interfaces.switchport.all(
            filters={"hostname": ["eq", switch], "intName": ["eq", switchport]}
        )
        if ipf_switchport[0]["mode"] == "static access":
            config_mode = "Access-Port"
        elif ipf_switchport[0]["mode"] == "trunk":
            config_mode = "Trunk-Port"
        else:
            config_mode = ipf_switchport[0]["mode"]
        nw_team_needed = True if config_mode == "Access-Port" else False
        # Create the ip-detail dict with the infos to ceate the payload
        ip_detail_dict[f"{x['ip']}/{prefixlen}"] = {
            "ipam_1_switch": switch_id,
            "ipam_2_switchport": switchport,
            "ipam_3_switchport_config_mode": config_mode,
            "ipam_4_mac": x["mac"],
            "p0_4_nws_team_needed": nw_team_needed,
        }
        updated_fields.append(
            f"  - {x['ip']}/{prefixlen} (Switch ID: {switch_id}, Switchport: {switchport}, "
            f"Config-Mode: {config_mode}, MAC: {x['mac']}, NWS-Team: {nw_team_needed})"
        )

    # Create the payload to update the ip-addresses
    payload = []
    for ip in prefix["active_ips"]:
        # Check if the IP address is in the ip_detail_dict
        if ip["address"] in ip_detail_dict.keys():
            payload.append({"id": ip["id"], "custom_fields": {**ip_detail_dict[ip["address"]]}})

    # PATCH request to update the ip-addresses
    resp = patch_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", payload=payload)

    # Verify the response code and print the result
    if resp.status_code in [200, 201, 204]:
        task_text = "Update Edge IP-Addresses Fields"
        text = "The following edge ip-addresses fields had been updated:"
        updated_fields = "\n".join(updated_fields)
        results.append(
            f"{task_result(text=task_text, changed=False, level_name='INFO')}\n"
            + f"'{task_text}' -> NetBoxResponse <Success: True>\n"
            + "-> The following edge ip-addresses fields had been updated:\n"
            + f"{updated_fields}"
        )
    else:
        results.append(
            [
                f"{task_result(text=task_text, changed=False, level_name='ERROR')}\n"
                + f"'{task_text}' -> NetBoxResponse <Success: False>\n"
                + f"-> Response Status Code: {resp.status_code}\n"
                + f"-> Response Json:\n{resp.json()}"
            ]
        )

    return results, failed


def update_all_netbox_ip_addresses(prefix: dict) -> tuple:
    """
    Update all NetBox IP addresses VRF, Tenant, Tags and Location of a given prefix.

    Args:
        prefix (dict): The NetBox prefix for which the IP addresses need to be updated.
        nb_url (str): The URL of the NetBox instance.

    Returns:
        list: A tuple of results from the update tasks and a boolean indicating if the task failed.
    """
    # Create a list to collect the task results
    results = []
    # Boolian to check if any ip-addresses have been changed and the overall failed status
    changed = False
    failed = False

    # Print the task title
    results.append(task_name(text=f"Update NetBox IP-Addresses of Prefix {prefix['prefix']}"))

    # Get the base url of the NetBox instance
    nb_url = base_url(url=prefix["url"], with_path=False)
    # Get all ip-addresses of the parent prefix
    query = {"parent": prefix["prefix"]}
    ip_addresses = get_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", params=query)
    # Create the payload to update all the ip-addresses
    payload = create_nb_ip_payload(parent_prefix=prefix, data=ip_addresses)
    # PATCH request to update the ip-addresses tags
    resp = patch_nb_resources(url=f"{nb_url}/api/ipam/ip-addresses/", payload=payload)

    # If the response json is not empty
    if resp.json():
        # Verify the response code and print the result
        task_text = "Update IP-Addresses Fields"
        text = "The following ip-addresses fields had been updated:"
        # The function returns the result list and True if the response is successful else False
        result, sub_failed = create_nb_response_result(
            resp=resp, nb_type="ip", data=prefix, task_text=task_text, text=text
        )
        results, changed, failed = set_results_changed_failed(results, result, changed, sub_failed, failed)

    # Print a message if no ip-addresses have been updated
    if not changed:
        text = f"No IP-Address to update for Prefix {prefix['prefix']}"
        results.append(
            f"{task_result(text=text, changed=False, level_name='INFO')}\n"
            + f"'{text}' -> NetBoxResponse <Success: True>\n"
            + f"-> Prefix {prefix['prefix']} have no ip-addresses to update"
        )

    return results, failed


def update_all_netbox_vlans(vlan: dict) -> tuple:
    """
    Update NetBox VLANs.
    To update a VLAN associated to a prefix with the following information:
        * Status, Tenant, Tags, Location
    To update a VLAN without associated to a prefix with the following information:
        * Tags

    Args:
        prefix (dict): The prefix to get the vlan from to update.

    Returns:
        tuple: A tuple containing the results of the update and the overall failed status.

    """
    # Create a list to collect the task results
    results = []
    # Boolian to check if any ip-addresses have been changed and the overall failed status
    changed = False
    failed = False

    # Print the task title
    results.append(task_name(text=f"Update NetBox VLAN {vlan['name']} (VLAN {vlan['vid']})"))

    # Get the base url of the NetBox instance
    nb_url = base_url(url=vlan["url"], with_path=False)
    # Get the prefix assigned to the vlan
    query = {"vlan_id": vlan["id"]}
    prefix = get_nb_resources(url=f"{nb_url}/api/ipam/prefixes/", params=query)
    prefix = prefix[0] if prefix else None
    # Create the payload to update the vlan
    if prefix:
        payload = {
            "id": vlan["id"],
            "status": prefix["status"]["value"],
            "tenant": prefix["tenant"]["id"] if prefix["tenant"] is not None else None,
            "tags": [tag["id"] for tag in prefix["tags"]],
            "custom_fields": {"ipam_location": prefix["custom_fields"]["ipam_location"]},
        }
    else:
        payload = {"id": vlan["id"], "tags": [{"slug": "l2-only"}]}
    # PATCH request to update the vlan
    resp = patch_nb_resources(url=f"{nb_url}/api/ipam/vlans/{vlan['id']}/", payload=payload)

    # Verify the response code and print the result
    task_text = "Update VLAN Fields"
    text = "The following VLAN fields had been updated:"
    # The function returns the result list and True if the response is successful else False
    result, sub_failed = create_nb_response_result(
        resp=resp, nb_type="vlan", data=prefix, task_text=task_text, text=text
    )
    results, changed, failed = set_results_changed_failed(results, result, changed, sub_failed, failed)

    return results, failed


def run_thread_pool(
    title: str, task: Callable, thread_list: list[dict], max_workers: int = 50, args: tuple = ()
) -> list:
    """
    Runs a thread pool with a given task for each item in the thread list.

    Args:
        title (str): The title of the task.
        task (Callable): The task to be executed for each item in the thread list.
        thread_list (list[dict]): The list of items to be processed by the task.
        args (tuple, optional): Additional arguments to be passed to the task. Defaults to ().

    Returns:
        list: A list of threads representing the submitted tasks.
    """
    # Print the task title
    print_task_title(title=title)

    # If the thread list is empty return the result list
    if not thread_list:
        print(
            f"{task_name(text=title)}\n"
            f"{task_result(text=title, changed=False, level_name='INFO')}\n"
            + f"'{title}' -> NetBoxResponse <Success: True>\n"
            + "-> No items to process in the thread list"
        )
        return []

    # Create a ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit a new task for each prefix to update and collect the tasks results
        threads = [executor.submit(task, item, *args) for item in thread_list]

    return threads


def print_thread_pool_results(title: str, thread_result, fail_hard: bool = False) -> bool:
    """
    Print the results of a ThreadPoolExecutor.

    Args:
        threads (list): The list of threads to print the results for.

    Returns:
        bool: The overall failed status. True if any of the threads failed, False otherwise.
    """
    # Overal failed status
    failed_task = False

    # Interate over threads and print the result for each thread
    for thread in thread_result:
        # Get the results and failed status from the thread
        results, failed = thread.result()
        # Print the results
        for result in results:
            print(result)
        # If failed is True set the overall failed status to True
        failed_task = True if failed else failed_task

    # Print a message if any task has failed and exit the script
    if fail_hard and failed_task:
        print("\n")
        exit_error(task_text=title, msg=["-> Verify the result for failes tasks"])

    return failed_task


def main(nr_config: str, nmap_scan: bool = False, overwrite_active: list[str] = None) -> None:
    """
    Main function is intended to import and execute by other scripts.
    It loads NetBox inventory, scan active prefixes, and update IP addresses and VLANs.

    * Args:
        * nr_config (str): Path to the Nornir configuration YAML file.
        * overwrite_active (list[str], optional): List of active IP addresses to overwrite. Defaults to None.

    * Steps:
        * Load the Nornir configuration file.
        * Load active NetBox prefixes.
        * Load all non-container NetBox prefixes.
        * Load NetBox VLANs.
        * Update OOB/T1/T2 prefixes IP-addresses status, DNS names, and ports with a Nmap scan
        * Update all prefixes IP-addresses status and DNS names from IP-Fabric
        * Update all active IP-addresses switch/switchport info from IP-Fabric
        * Update all prefixes IP-addresses vrf, tenant, tags, and location
        * Update all VLANs status, tenant, tags, and location

    * Exits:
        * Exits with code 1 if the Nornir configuration file is empty or if any task fails.
    """

    #### Initialize Nornir ##################################################################################

    # Initialize, transform and filter the Nornir inventory are return the filtered Nornir object
    # Define data to load from NetBox in addition to the base Nornir inventory plugin
    add_netbox_data = {"load_virtual_chassis_data": True}
    nr = init_nornir(config_file=nr_config, add_netbox_data=add_netbox_data)
    # Get the NetBox url from the inventory options
    nb_url = nr.config.inventory.options["nb_url"]

    #### Load NetBox IPAM Data ##############################################################################

    task_text = "Load NetBox IPAM Data"
    print_task_title(title=task_text)

    # Load Active NetBox Prefixes from Tenant 'none', 'oob', 'tier-1' and 'tier-2' (except marked utilized)
    # These prefixes will be scanned with nmap and updated
    nb_active_oob_t1_t2_prefixes = load_netbox_data(
        task_text="Load Active OOB/T1/T2 NetBox Prefixes",
        nb_api_url=f"{nb_url}/api/ipam/prefixes/",
        query={"status": "active", "tenant": ["none", "oob", "tier-1", "tier-2"], "mark_utilized": "false"},
    )

    # Load Active and NetBox Prefixes from all Tenants (except marked utilized)
    # These prefixes will be updated with input from IP-Fabric
    nb_active_all_prefixes = load_netbox_data(
        task_text="Load Active OOB/T1/T2/T3/T4 NetBox Prefixes",
        nb_api_url=f"{nb_url}/api/ipam/prefixes/",
        query={
            "status": "active",
            "tenant": ["none", "oob", "tier-1", "tier-2", "tier-3", "tier-4"],
            "mark_utilized": "false",
        },
    )

    # Load NetBox Non-Container Prefixes
    nb_subnet_prefixes = load_netbox_data(
        task_text="Load All Non-Container NetBox Prefixes",
        nb_api_url=f"{nb_url}/api/ipam/prefixes/",
        query={"status": ["active", "reserved", "deprecated", "inventory"]},
    )

    # Load NetBox VLANs
    nb_vlans = load_netbox_data(
        task_text="Load NetBox VLANs",
        nb_api_url=f"{nb_url}/api/ipam/vlans/",
        query={},
    )

    #### Nmap Scan Active NetBox Prefixes and Update IP-Addresses ###########################################

    if nmap_scan:
        # Set the task title
        title = "Nmap Scan and Update Active OOB/T1/T2 NetBox Prefixes IP-Addresses"

        # Run the thread pool to update all NetBox IP-Addresses Status, DNS-Name and Open Ports
        # 1. arg is the input type ('nmap' or 'ip-fabric')
        # 2. arg is the list of active IP addresses to overwrite
        thread_result = run_thread_pool(
            title=title,
            task=update_netbox_prefix_ip_addresses,
            thread_list=nb_active_oob_t1_t2_prefixes,
            max_workers=50,  # NetBox have no rate limit, but 50 threads are a good tested value with Nmap
            args=("nmap", overwrite_active, nr_config),
        )
        # Print the thread pool results and exit the script if any task has failed
        print_thread_pool_results(title=title, thread_result=thread_result, fail_hard=True)

    #### IP-Fabric Update Active NetBox Prefixes IP-Addresses ###############################################

    # Set the task title
    title = "IP-Fabric Update All Active NetBox Prefixes IP-Addresses"

    # Run the thread pool to update all NetBox IP-Addresses Status and DNS-Name
    # 1. arg is the input type ('nmap' or 'ip-fabric')
    # 2. arg is the list of active IP addresses to overwrite
    thread_result = run_thread_pool(
        title=title,
        task=update_netbox_prefix_ip_addresses,
        thread_list=nb_active_all_prefixes,
        max_workers=5,  # Each thread will create the own Nornir object == Max. 5 concurrent Nornir logins
        args=("ip-fabric", overwrite_active, nr_config),
    )
    # Print the thread pool results and exit the script if any task has failed
    print_thread_pool_results(title=title, thread_result=thread_result, fail_hard=True)

    #### IP-Fabric Update Switch & Switchport Info for IP-Addresses #########################################

    # Set the task title
    title = "IP-Fabric Update All Active NetBox IP-Addresses Switch/Switchport Info"

    # Connect to IP-Fabric
    ipf = IPFClient(
        base_url=os.environ["IPF_URL"], auth=os.environ["IPF_TOKEN"], snapshot_id="$last", verify=False
    )
    # Get all mac-addresses on edge ports from the IP-Fabric technology mac table
    filters = {"edge": ["eq", True]}
    columns = ["hostname", "intName", "mac", "vendor"]
    ipf_mac_table = ipf.technology.addressing.mac_table.all(filters=filters, columns=columns)
    ipf_edge_mac_dict = {str(x["mac"]): x for x in ipf_mac_table}

    # Run the thread pool to update all NetBox IP-Addresses Switch and Switchport Info
    thread_result = run_thread_pool(
        title=title,
        task=update_netbox_ip_address_switchport,
        thread_list=nb_active_all_prefixes,
        max_workers=3,  # More then 3 threads will run into rate limit errors of IP-Fabric
        args=(ipf_edge_mac_dict, nr),
    )
    # Print the thread pool results and exit the script if any task has failed
    print_thread_pool_results(title=title, thread_result=thread_result, fail_hard=True)

    #### Update all IP-Addresses Tags and other Fields ######################################################

    # Set the task title
    title = "Update All NetBox Prefixes IP-Addresses Tags and other Fields"

    # Run the thread pool to update all NetBox IP-Addresses Tags and other Fields
    thread_result = run_thread_pool(
        title=title,
        task=update_all_netbox_ip_addresses,
        max_workers=50,
        thread_list=nb_subnet_prefixes,
    )
    # Print the thread pool results and exit the script if any task has failed
    print_thread_pool_results(title=title, thread_result=thread_result, fail_hard=True)

    #### Update all VLANs Tags and other Fields #############################################################

    # Set the task title
    title = "Update All NetBox VLANs Tags and other Fields"

    # Run the thread pool to update all NetBox VLANs Tags and other Fields
    thread_result = run_thread_pool(
        title=title,
        task=update_all_netbox_vlans,
        max_workers=50,
        thread_list=nb_vlans,
    )
    # Print the thread pool results and exit the script if any task has failed
    print_thread_pool_results(title=title, thread_result=thread_result, fail_hard=True)
