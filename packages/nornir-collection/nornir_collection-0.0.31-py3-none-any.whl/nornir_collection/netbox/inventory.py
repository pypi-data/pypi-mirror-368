#!/usr/bin/env python3
"""
This module contains general functions and tasks related to NetBox and Nornir.

The functions are ordered as followed:
- Task Helper Functions
- Single Nornir Tasks
- Nornir Tasks in regular Function
"""

from typing import Dict, List
from nornir.core import Nornir
from nornir.core.task import Task, Result
from nornir_collection.netbox.utils import get_nb_resources
from nornir_collection.utils import task_info, print_task_name, print_result, exit_error


#### Task Helper Functions ##################################################################################


#### Nornir Tasks ###########################################################################################


def _load_virtual_chassis_data(task: Task, all_devices: List[Dict]) -> Result:
    """
    Load NetBox virtual chassis member data.
    Args:
        task (Task): Nornir task object.
        all_devices: (List[Dict]): List of all devices from NetBox.
    Returns:
        Result: Nornir result object.
    """
    # Set the failed flag to False
    failed = False

    # If the device is not part of a virtual chassis
    if not task.host.get("virtual_chassis"):
        # Return the Nornir object
        result = (
            f"'Load Virtual-Chassis data' -> NetBoxResponse <Success: {not failed}>\n"
            + "-> Device is not part of a virtual-chassis in NetBox"
        )
        return Result(host=task.host, result=result, changed=False, failed=failed)

    # Dict comprehension to include only some key-value pairs
    include_keys = ["id", "url", "display", "name", "serial"]
    # Add an empty list for the members of the virtual chassis
    task.host["virtual_chassis"]["members"] = []
    # Add the data of all members to the master
    # Start with 2 as the master is number 1 and already in the lists
    for i in range(2, task.host["virtual_chassis"]["member_count"] + 1):
        # Get the member data
        member = [x for x in all_devices if x["name"] == f"{task.host['virtual_chassis']['name']}_{i}"]
        # Dict comprehension to include only some key-value pairs
        member = {k: v for (k, v) in member[0].items() if k in include_keys}
        member["serial"] = member["serial"] if member["serial"] else None
        # Add the member data to the virtual chassis master
        task.host["virtual_chassis"]["members"].append(member)

    # Return the Nornir object
    return Result(host=task.host)


def _load_interface_data(task: Task, all_interfaces: List[Dict], enrich_vlan_data: True) -> Result:
    """
    Load NetBox interface data.
    Args:
        task (Task): The Nornir task object.
        all_interfaces: (List[Dict]): List of all interfaces from NetBox.
    Returns:
        Result: Nornir result object.
    """
    # Set the failed flag to False
    failed = False

    # Get all interfaces from the master device
    interfaces = [x for x in all_interfaces if x["device"]["id"] == task.host["id"]]
    # Add all interfaces from the virtual chassis members
    if task.host.get("virtual_chassis") and task.host["virtual_chassis"].get("members"):
        for member in task.host["virtual_chassis"]["members"]:
            interfaces.extend([x for x in all_interfaces if x["device"]["id"] == member["id"]])
    # Return if the interfaces list is empty
    if not interfaces:
        # Return the Nornir object
        result = (
            f"'Load interface data' -> NetBoxResponse <Success: {not failed}>\n"
            + "-> No interface data found in NetBox"
        )
        return Result(host=task.host, result=result, changed=False, failed=failed)

    # Dict keys for comprehension to include only some key-value pairs
    # fmt: off
    include_keys = [
        "name", "int_template", "description", "type", "lag", "mode", "untagged_vlan", "tagged_vlans",
        "count_ipaddresses", "count_fhrp_groups", "int_peer_device", "enabled",
    ]
    # fmt: on
    # Make some normalization to the device interfaces data with the interface_filter list and others
    for interface in interfaces:
        # Remove the custom_fields key and make the custom_field native to Nornir
        for custom_field, value in interface["custom_fields"].items():
            interface[custom_field] = value
        interface.pop("custom_fields")
        # Dict comprehension to include only some key-value pairs
        interface = {k: v for (k, v) in interface.items() if k in include_keys}
        # If the interface has a peer device, add the peer device data to the interface
        if enrich_vlan_data and interface.get("int_peer_device"):
            # Get the interface peer device name
            peer_name = interface["int_peer_device"]["name"]
            # Slice the last two characters from the name to get the peer name of the virtual chassis
            peer_name = peer_name if task.nornir.inventory.hosts.get(peer_name) else peer_name[:-2]
            # Add the peer device data (VLAN name & VLAN ID) to the interface if 'cfg_vlans' exists
            if task.nornir.inventory.hosts[peer_name].data.get("cfg_vlans"):
                interface["int_peer_device"]["vlans"] = [
                    {k: v for (k, v) in vlan.items() if k in ["vid", "name"]}
                    for vlan in task.nornir.inventory.hosts[peer_name].data["cfg_vlans"]
                ]
            # Add an empty list if 'cfg_vlans' does not exist
            else:
                interface["int_peer_device"]["vlans"] = []

    # Reorder the list to have all LAG interfaces first and all virtual interfaces last
    lag_int = [i for i in interfaces if i["type"]["value"] == "lag"]
    virt_int = [i for i in interfaces if i["type"]["value"] == "virtual"]
    other_int = [i for i in interfaces if i["type"]["value"] not in ("lag", "virtual")]
    # Assign the interfaces list to the device
    interfaces = lag_int + other_int + virt_int

    # Create an empty interfaces list in the device data
    task.host["interfaces"] = []
    # Dict comprehension to include only some key-value pairs
    for interface in interfaces:
        data = {k: v for (k, v) in interface.items() if k in include_keys}
        task.host["interfaces"].append(data)

    # Return the Nornir object
    return Result(host=task.host)


def _load_vlan_data(task: Task, all_vlans: List[Dict]) -> Result:
    """
    Load NetBox VLAN data.
    Args:
        task (Task): The Nornir task object.
        all_interfaces: (List[Dict]): List of all VLANs from NetBox.
    Returns:
        Result: Nornir result object.
    """
    # Set the failed flag to False
    failed = False

    # Return if the device has no VLAN groups
    if not task.host.get("vlan_groups"):
        # Return the Nornir object
        result = (
            f"'Load VLAN data' -> NetBoxResponse <Success: {not failed}>\n"
            + "-> No 'vlan_groups' key found in NetBox"
        )
        return Result(host=task.host, result=result, changed=False, failed=failed)

    # Dict keys for comprehension to include only some key-value pairs
    include_keys = ["display", "name", "vid", "status", "description", "group", "role", "prefix_count"]
    # Create an empty cfg_vlans dict in the device data
    task.host["cfg_vlans"] = []

    # Loop through the 'vlan_groups' and find VLANs that match the group and role
    for group, roles in task.host["vlan_groups"].items():
        # If the group_roles list is not empty, filter the VLANs to match only the role
        if roles:
            vlans = []
            for role in roles:
                # Update the VLANs to match all VLANs that match also the role
                # The following list comprehensions fails of the 'group' or the 'role' is None
                data = [x for x in all_vlans if (x["group"]["name"] == group and x["role"]["name"] == role)]
                vlans.extend(data)
                # Return if the data list is empty
                if not data:
                    failed = True
                    break
        else:
            # Get all VLANs that match the group name
            vlans = [x for x in all_vlans if x["group"]["name"] == group]
            # Return if the vlans list is empty
            if not vlans:
                failed = True
                break

        # Add the VLANs to the cfg_vlans dict
        for item in vlans:
            # Dict comprehension to include only some key-value pairs
            vlan = {k: v for (k, v) in item.items() if k in include_keys}
            task.host["cfg_vlans"].append(vlan)

    # Set the result based on the failed boolian
    result = f"'Load VLAN data' -> NetBoxResponse <Success: {not failed}>\n"
    if failed:
        result += "-> One or more 'groups' and/or 'roles' under the 'vlan_groups' key not found in NetBox"
    else:
        result += "-> All 'groups' and 'roles' under the 'vlan_groups' key found in NetBox"

    # Return the Nornir object
    return Result(host=task.host, result=result, changed=False, failed=failed)


def _load_cisco_support_data(task: Task, all_csupp: List[Dict]) -> Result:
    """
    Load NetBox Cisco support data.
    Args:
        task (Task): The Nornir task object.
        all_interfaces: (List[Dict]): List of all interfaces from NetBox.
    Returns:
        Result: Nornir result object.
    """
    # Set the failed flag to False
    failed = False

    # Get the Cisco Support data for the master
    data = [x for x in all_csupp if x["device"]["id"] == task.host["id"]]
    # Return if the data list is empty
    if not data:
        # Return the Nornir object
        result = (
            f"'Load Cisco-Support data' -> NetBoxResponse <Success: {not failed}>\n"
            + "-> No Cisco-Support data found in NetBox"
        )
        return Result(host=task.host, result=result, changed=False, failed=failed)

    # Dict keys for comprehension to exclude some key-value pairs from the response
    exclude_keys = ["device"]
    # Dict comprehension to exclude some key-value pairs
    data = {k: v for (k, v) in data[0].items() if k not in exclude_keys}
    task.host["cisco_support"] = {}
    task.host["cisco_support"]["master"] = data

    # Add all interfaces from the virtual chassis members
    if task.host.get("virtual_chassis") and task.host["virtual_chassis"].get("members"):
        task.host["cisco_support"]["members"] = []
        for member in task.host["virtual_chassis"]["members"]:
            data = [x for x in all_csupp if x["device"]["id"] == member["id"]]
            # Dict comprehension to exclude some key-value pairs
            data = {k: v for (k, v) in data[0].items() if k not in exclude_keys}
            task.host["cisco_support"]["members"].append(data)

    # Return the Nornir
    return Result(host=task.host)


#### Nornir Tasks in regular Function #######################################################################


def load_additional_netbox_data(nr: Nornir, add_netbox_data: dict[str:bool], silent: bool = False) -> Nornir:
    """
    Load additional data from NetBox into Nornir inventory based on 'add_netbox_data' options.
    """

    result_msg = []
    task_text = "NORNIR load NetBox additional inventory data"

    # Get the NetBox url from the inventory options
    nb_url = nr.config.inventory.options["nb_url"]

    # Add the virtual chassis data to the devices
    if add_netbox_data.get("load_virtual_chassis_data"):
        # Get all devices from NetBox
        all_devices = get_nb_resources(url=f"{nb_url}/api/dcim/devices/?limit=1000")
        # Run the custom Nornir task _load_virtual_chassis_data
        result = nr.run(
            name=task_text,
            task=_load_virtual_chassis_data,
            all_devices=all_devices,
            on_failed=True,
        )
        # Exit the script if the task failed
        if result.failed:
            print_result(result)
            exit_error(
                task_text=task_text,
                text="ALERT: LOAD VIRTUAL-CHASSIS DATA FAILED!",
                msg="-> Analyse the Nornir Init Python function and NetBox API response",
            )
        # Append the result message
        result_msg.append("  - Load Virtual-Chassis")

    # Add the Cisco support data to the devices
    if add_netbox_data.get("load_cisco_support_data"):
        # Get all Cisco-Support data from NetBox
        all_csupp = get_nb_resources(url=f"{nb_url}/api/plugins/device-support/cisco-device/?limit=1000")
        # Run the custom Nornir task _load_cisco_support_data
        result = nr.run(
            name=task_text,
            task=_load_cisco_support_data,
            all_csupp=all_csupp,
            on_failed=True,
        )
        # Exit the script if the task failed
        if result.failed:
            print_result(result)
            exit_error(
                task_text=task_text,
                text="ALERT: LOAD CISCO-SUPPORT FAILED!",
                msg="-> Analyse the Nornir Init Python function and NetBox API response",
            )
        # Append the result message
        result_msg.append("  - Load Cisco-Support")

    # Add the vlan data to the devices
    if add_netbox_data.get("load_vlan_data"):
        # Get all vlans from NetBox
        all_vlans = get_nb_resources(url=f"{nb_url}/api/ipam/vlans/?limit=1000?")
        # The task _load_vlan_data can only load VLANs that are part of a group and have a role. All VLANs
        # in the DSC Azure Tenant are not part of a group and needs to be excluded the the all_vlans list.
        all_vlans = [x for x in all_vlans if x["role"]["name"] != "AZURE"]
        # Run the custom Nornir task _load_vlan_data
        result = nr.run(
            name=task_text,
            task=_load_vlan_data,
            all_vlans=all_vlans,
            on_failed=True,
        )
        # Exit the script if the task failed
        if result.failed:
            print_result(result)
            exit_error(
                task_text=task_text,
                text="ALERT: LOAD VLAN DATA FAILED!",
                msg="-> Analyse the Nornir Init Python function and NetBox API response",
            )
        # Append the result message
        result_msg.append("  - Load VLANs")

    # Add the interfaces data to the devices
    if add_netbox_data.get("load_interface_data"):
        # Get all interfaces from NetBox
        all_interfaces = get_nb_resources(url=f"{nb_url}/api/dcim/interfaces/?limit=1000")
        # Run the custom Nornir task _load_interface_data
        # Enrich the interface data with VLAN data if the 'load_vlan_data' option is set
        result = nr.run(
            name=task_text,
            task=_load_interface_data,
            all_interfaces=all_interfaces,
            enrich_vlan_data=add_netbox_data.get("load_vlan_data", False),
            on_failed=True,
        )
        # Exit the script if the task failed
        if result.failed:
            print_result(result)
            exit_error(
                task_text=task_text,
                text="ALERT: LOAD INTERFACE DATA FAILED!",
                msg="-> Analyse the Nornir Init Python function and NetBox API response",
            )
        # Append the result message
        result_msg.append("  - Load Interfaces")

    if not silent:
        # Print the result of the additional loaded data
        print_task_name(text=task_text)
        print(task_info(text=task_text, changed=False))
        print("'Load NetBox additional inventory data' -> NornirResponse <Success: True>")
        print("-> Additional loaded data:")
        for msg in result_msg:
            print(msg)
