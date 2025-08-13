#!/usr/bin/env python3
"""
This module contains NETCONF functions and tasks related to Nornir. NETCONF operation RPCs like lock,
validate, commit, discard and unlock are not part of this module. Please take a look to ops_tasks module.

The functions are ordered as followed:
- Helper functions
- Nornir NETCONF tasks
- Nornir NETCONF tasks in regular function
"""

import traceback
from typing import Union
from colorama import init
from nornir_scrapli.tasks import netconf_edit_config
from nornir.core import Nornir
from nornir.core.task import Task, Result
from nornir_collection.cisco.configuration_management.utils import (
    extract_interface_name,
    extract_interface_number,
    render_jinja2_template,
    add_interface_data,
    set_restconf_result,
)
from nornir_collection.cisco.configuration_management.restconf.tasks import rc_cisco_get
from nornir_collection.utils import print_result, task_result

init(autoreset=True, strip=False)


#### Helper Functions #######################################################################################


def return_result_if_no_interfaces(task: Task) -> Union[str, None]:
    """
    TBD
    """
    if "interfaces" not in task.host:
        custom_result = (
            f"'{task.name}' -> NornirResponse <Success: True>\n"
            '-> Host inventory key task.host["interfaces"] not found' + f"\n\n{traceback.format_exc()}"
        )
        return custom_result

    # Return None if everything is fine
    return None


def return_result_if_no_template(task: Task, is_iface: bool, tpl_startswith: str) -> Union[str, dict, list]:
    """
    TBD
    """
    # If its a interface task, return the result if no Jinja2 interface templates were found
    if is_iface:
        # Create a list with the templates of the interface for verification
        nc_tpl = []
        for i in task.host["interfaces"]:
            if i["int_template"] is None:
                continue
            if i["int_template"].startswith(tpl_startswith):
                nc_tpl.append(i["int_template"])
        # Return the result if no Jinja2 templates were found
        if not nc_tpl:
            custom_result = (
                f"'{task.name}' -> NornirResponse <Success: True>\n"
                f'-> No interface template starting with "{tpl_startswith}" found'
            )
            return custom_result

        # Return the template list if everything is fine
        return nc_tpl

    # If its a system task, return the result if no Jinja2 system templates were found
    # Create a dict with all templates where the template key match the tpl_startswith string
    nc_tpl = {}
    for tpl_name, tpl_path in task.host.items():
        if tpl_name.startswith(tpl_startswith):
            # Add the template to the dict
            nc_tpl[tpl_name] = tpl_path

    # Return the result if no Jinja2 templates were found
    if not nc_tpl:
        custom_result = (
            f"'{task.name}' -> NornirResponse <Success: False>\n"
            f"-> No templates starting with '{tpl_startswith}' found"
        )
        return custom_result

    # Return the template dict if everything is fine
    return nc_tpl


def netconf_configure_jinja2_rendered_payload_template(
    task: Task,
    j2_task_text: str,
    j2_tpl_path: str,
    custom_result: list,
    task_failed: bool,
    info_msg: str = None,
    verbose: bool = False,
    int_name: str = None,
    j2_tpl_name: str = None,
    j2_kwargs: dict = None,
) -> tuple:
    """
    TBD
    """
    try:
        # Render the Jinja2 payload template
        kwargs = j2_kwargs or {}
        nc_config = render_jinja2_template(task=task, tpl_path=j2_tpl_path, kwargs=kwargs)

        # If the Jinja2 template rendering was successful, set the Jinja2 print result item
        msg = f"{task_result(text=j2_task_text, changed=False, level_name='INFO', failed=False)}\n"
        if int_name:
            msg += f"'{int_name} ({j2_tpl_name})' -> Jinja2Response <Success: True>\n"
        elif j2_tpl_name:
            msg += f"'{j2_tpl_name}' -> Jinja2Response <Success: True>\n"
        else:
            msg += f"'{j2_task_text}' -> Jinja2Response <Success: True>\n"
        # Add the Jinja2 template name to the result string
        msg += f"-> {info_msg}"
        # Add the Jinja2 template result to the result string if verbose is True
        custom_result.append(msg + f"\n\n{nc_config}" if verbose else msg)

    except:  # noqa: E722
        task_failed = True
        # Set the Nornir print result item
        msg = f"{task_result(text=j2_task_text, changed=False, level_name='ERROR', failed=True)}\n"
        if int_name:
            msg += f"'{int_name} ({j2_tpl_name})' -> Jinja2Response <Success: False>\n"
        elif j2_tpl_name:
            msg += f"'{j2_tpl_name}' -> Jinja2Response <Success: False>\n"
        else:
            msg += f"'{j2_task_text}' -> Jinja2Response <Success: False>\n"
        # Add the Traceback as its an Nornir result for an exception
        msg += f"-> {info_msg}\n" + f"\n{traceback.format_exc()}"
        # Add the Nornir print result item to the custom_result list
        custom_result.append(msg)

        # Return the result as the Jinja2 template rendering failed
        return custom_result, task_failed

    # Configure the Jinja2 interface template
    try:
        # Apply config to the NETCONF candidate datastore
        nc_result = task.run(task=netconf_edit_config, config=nc_config, target="candidate")

        # If the task netconf_edit_config failed, set the Nornir result to return as failed
        if nc_result[0].failed:
            task_failed = True

        # Set level_name and failed for the Nornir print result item
        level_name = "ERROR" if nc_result[0].failed else "INFO"
        failed = bool(nc_result[0].failed)
        changed = not failed

        # Set the Nornir print result item
        msg = f"{task_result(text=task.name, changed=changed, level_name=level_name, failed=failed)}\n"
        if int_name:
            msg += f"'{int_name} ({j2_tpl_name})' -> {str(nc_result[0].scrapli_response)}"
        elif j2_tpl_name:
            msg += f"'{j2_tpl_name}' -> {str(nc_result[0].scrapli_response)}"
        else:
            msg += f"'{task.name}' -> {str(nc_result[0].scrapli_response)}"

        # Add the Nornir print result item to the custom_result list
        custom_result.append(
            msg + f"\n\n{nc_result[0].scrapli_response.result}"
            if nc_result[0].failed
            else (msg + f"\n\n{nc_result[0].scrapli_response.result}" if verbose else msg)
        )

    except:  # noqa: E722
        task_failed = True
        # Set the Nornir print result item
        msg = f"{task_result(text=task.name, changed=False, level_name='ERROR', failed=True)}\n"
        if int_name:
            msg += f"'{int_name} ({j2_tpl_name})' -> NetconfResponse <Success: False>\n"
        elif j2_tpl_name:
            msg += f"'{j2_tpl_name}' -> NetconfResponse <Success: False>\n"
        else:
            msg += f"'{task.name}' -> NetconfResponse <Success: False>\n"
        # Add the Traceback as its an Nornir result for an exception
        msg += f"\n{traceback.format_exc()}"
        # Add the Nornir print result item to the custom_result list
        custom_result.append(msg)

        # Return the result as the NETCONF config failed
        return custom_result, task_failed

    # Return the successful custom result and the task_failed status which is False
    return custom_result, task_failed


#### Nornir NETCONF Tasks ###################################################################################


def nc_edit_cleanup_portchannel(task: Task, verbose: bool = False) -> Result:
    """
    TBD
    """
    # The custom_result list will be filled with the results
    custom_result = []

    # Return the Nornir result as failed if the host have no interfaces
    iface_result = return_result_if_no_interfaces(task=task)
    # If the return in not None, then it's the custom Nornir result to return
    if isinstance(iface_result, str):
        return Result(host=task.host, custom_result=iface_result, failed=True)

    #### Get all current configured Port-channels with RESTCONF #############################################

    task_text = "RESTCONF GET Portchannel interfaces"

    # Set the RESTCONF port, yang query and url to get all configured SVIs
    yang_query = "Cisco-IOS-XE-native:native/interface"
    url = f"https://{task.host.hostname}:443/restconf/data/{yang_query}"

    # RESTCONF HTTP Get for all SVIs
    response = rc_cisco_get(url=url, auth=(task.host.username, task.host.password), verify=False)

    # Set the RESTCONF result and return the Nornir result if the RESTCONF response status_code is not 200
    custom_result = set_restconf_result(
        task=Task,
        task_text=task_text,
        yang_query=yang_query,
        response=response,
        custom_result=custom_result,
        verbose=verbose,
    )

    #### Render NETCONF payload to remove Port-channels with Jinja2 #########################################

    task_text = "Render Jinja2 NETCONF payload"

    # Create a empty list to add all current configured Port-channels and their associated interfaces
    current_po = {}
    remove_po = {}
    if "Port-channel" in response["json"]["Cisco-IOS-XE-native:interface"]:
        # Loop through all Port-channels and add them and their associated interfaces as a list to the dict
        for po in response["json"]["Cisco-IOS-XE-native:interface"]["Port-channel"]:
            current_po[po["name"]] = []
            for i_name, i_detail in response["json"]["Cisco-IOS-XE-native:interface"].items():
                for i in i_detail:
                    if i.get("Cisco-IOS-XE-ethernet:channel-group"):
                        if i["Cisco-IOS-XE-ethernet:channel-group"]["number"] == po["name"]:
                            current_po[po["name"]].append({"name": i_name, "number": i["name"]})

        # Exclude NoneType or empty string interface template names
        # Select only the interface name and convert it to lowercase
        ifaces = [i["name"].lower() for i in task.host["interfaces"] if i["int_template"]]
        # Include interfaces name starts with 'port-channel' and replace to only have the Port-channel number
        inventory_po = [int(i.replace("port-channel", "")) for i in ifaces if i.startswith("port-channel")]
        # Create a dict with all configured Port-channel which are not part of the inventoryp
        remove_po = {k: v for k, v in current_po.items() if k not in inventory_po}

    # If there are no Port-channel to remove, return the Nornir result
    if not remove_po:
        custom_result.append(
            f"{task_result(text=task_text, changed=False, level_name='INFO', failed=False)}\n"
            + f"'{task_text}' -> NornirResponse <Success: True>\n"
            + "-> No Portchannel interfaces to remove"
        )
        return Result(host=task.host, custom_result=custom_result, failed=False)

    # Set the info message for the Nornir result
    info_msg = f"Port-channel interfaces to remove: {len(remove_po)}"

    # Render the Jinja2 payload template and configure the NETCONF candidate datastore
    custom_result, task_failed = netconf_configure_jinja2_rendered_payload_template(
        task=task,
        j2_task_text=task_text,
        j2_tpl_path="iosxe_netconf/tpl_sys/cleanup/cleanup_portchannel.j2",
        custom_result=custom_result,
        task_failed=False,
        info_msg=info_msg,
        verbose=verbose,
        j2_kwargs={"remove_po": remove_po},
    )

    # Return the Nornir NETCONF result
    return Result(host=task.host, custom_result=custom_result, failed=task_failed)


def nc_edit_cleanup_svi(task: Task, verbose: bool = False) -> Result:
    """
    TBD
    """
    # The custom_result list will be filled with the results
    custom_result = []

    # Return the Nornir result as failed if the host have no interfaces
    iface_result = return_result_if_no_interfaces(task=task)
    # If the return in not None, then it's the custom Nornir result to return
    if isinstance(iface_result, str):
        return Result(host=task.host, custom_result=iface_result, failed=True)

    #### Get all current configured SVIs with RESTCONF ######################################################

    task_text = "RESTCONF GET VLAN interfaces"

    # Set the RESTCONF port, yang query and url to get all configured SVIs
    yang_query = "Cisco-IOS-XE-native:native/interface/Vlan"
    url = f"https://{task.host.hostname}:443/restconf/data/{yang_query}"

    # RESTCONF HTTP Get for all SVIs
    response = rc_cisco_get(url=url, auth=(task.host.username, task.host.password), verify=False)

    # Set the RESTCONF result and return the Nornir result if the RESTCONF response status_code is not 200
    custom_result = set_restconf_result(
        task=Task,
        task_text=task_text,
        yang_query=yang_query,
        response=response,
        custom_result=custom_result,
        verbose=verbose,
    )

    # Create a list with all current configured SVIs except the default VLAN 1
    current_svi = [x["name"] for x in response["json"]["Cisco-IOS-XE-native:Vlan"] if x["name"] != 1]

    #### Render NETCONF payload to remove SVIs with Jinja2 ##################################################

    task_text = "Render Jinja2 NETCONF payload"

    # Exclude NoneType or empty string interface template names
    # Select only the interface name and convert it to lowercase
    interfaces = [i["name"].lower() for i in task.host["interfaces"] if i["int_template"]]
    # Include interfaces which name starts with 'vlan' and replace 'vlan' to only have the SVI number
    inventory_svi = [int(i.replace("vlan", "")) for i in interfaces if i.startswith("vlan")]
    # Create a list with all configured SVIs which are not part of the inventoryp
    remove_svi = [svi for svi in current_svi if svi not in inventory_svi]

    # If there are no SVIs to remove, return the Nornir result
    if not remove_svi:
        custom_result.append(
            f"{task_result(text=task_text, changed=False, level_name='INFO', failed=False)}\n"
            + f"'{task_text}' -> NornirResponse <Success: True>\n"
            + "-> No VLAN interfaces to remove"
        )
        return Result(host=task.host, custom_result=custom_result, failed=False)

    # Set the info message for the Nornir result
    info_msg = f"VLAN interfaces to remove: {len(remove_svi)}"

    # Render the Jinja2 payload template and configure the NETCONF candidate datastore
    custom_result, task_failed = netconf_configure_jinja2_rendered_payload_template(
        task=task,
        j2_task_text=task_text,
        j2_tpl_path="iosxe_netconf/tpl_sys/cleanup/cleanup_svi.j2",
        custom_result=custom_result,
        task_failed=False,
        info_msg=info_msg,
        verbose=verbose,
        j2_kwargs={"remove_svi": remove_svi},
    )

    # Return the Nornir NETCONF result
    return Result(host=task.host, custom_result=custom_result, failed=task_failed)


def nc_edit_cleanup_vlan(task: Task, verbose: bool = False) -> Result:
    """
    TBD
    """
    # The custom_result list will be filled with the results
    custom_result = []

    #### Get all current configured VLANs with RESTCONF #####################################################

    task_text = "RESTCONF GET VLANs"

    # Set the RESTCONF port, yang query and url to get all configured SVIs
    yang_query = "Cisco-IOS-XE-native:native/vlan/Cisco-IOS-XE-vlan:vlan-list"
    url = f"https://{task.host.hostname}:443/restconf/data/{yang_query}"

    # RESTCONF HTTP Get for all SVIs
    response = rc_cisco_get(url=url, auth=(task.host.username, task.host.password), verify=False)

    # Set the RESTCONF result and return the Nornir result if the RESTCONF response status_code is not 200
    custom_result = set_restconf_result(
        task=Task,
        task_text=task_text,
        yang_query=yang_query,
        response=response,
        custom_result=custom_result,
        verbose=verbose,
    )

    # Create a list with all current configured VLANs except the default VLAN 1
    current_vlans = [x for x in response["json"]["Cisco-IOS-XE-vlan:vlan-list"] if x["id"] != 1]

    #### Render NETCONF payload to remove VLANs with Jinja2 #################################################

    task_text = "Render Jinja2 NETCONF payload"
    # Create a list with all configured VLANs which are not part of the inventory
    remove_vlans = [x for x in current_vlans if x["id"] not in [x["vid"] for x in task.host["cfg_vlans"]]]

    # If there are no VLANs to remove, return the Nornir result
    if not remove_vlans:
        custom_result.append(
            f"{task_result(text=task_text, changed=False, level_name='INFO', failed=False)}\n"
            + f"'{task_text}' -> NornirResponse <Success: True>\n"
            + "-> No VLANs to remove"
        )
        return Result(host=task.host, custom_result=custom_result, failed=False)

    # Set the info message for the Nornir result
    info_msg = f"VLANs to remove: {len(remove_vlans)}"

    # Render the Jinja2 payload template and configure the NETCONF candidate datastore
    custom_result, task_failed = netconf_configure_jinja2_rendered_payload_template(
        task=task,
        j2_task_text=task_text,
        j2_tpl_path="iosxe_netconf/tpl_sys/cleanup/cleanup_vlan.j2",
        custom_result=custom_result,
        task_failed=False,
        info_msg=info_msg,
        verbose=verbose,
        j2_kwargs={"remove_vlans": remove_vlans},
    )

    # Return the Nornir NETCONF result
    return Result(host=task.host, custom_result=custom_result, failed=task_failed)


def nc_edit_tpl_config(task: Task, tpl_startswith: str, verbose: bool = False) -> Result:
    """
    TBD
    """
    # Return the result if no Jinja2 interface templates for a 'tpl_startswith' string were found
    nc_tpl_result = return_result_if_no_template(task=task, is_iface=False, tpl_startswith=tpl_startswith)
    # If the return in a string, then it's the custom Nornir result to return
    if isinstance(nc_tpl_result, str):
        return Result(host=task.host, custom_result=nc_tpl_result, failed=True)

    #### Configure each Jinja2 rendered template ############################################################

    # Track if the overall task has failed
    task_failed = False
    # The custom_result list will be filled with the result of each template
    custom_result = []

    # Gather all NETCONF templates to apply
    for tpl_name, tpl_path in nc_tpl_result.items():
        # Render the Jinja2 payload template and configure the NETCONF candidate datastore
        custom_result, task_failed = netconf_configure_jinja2_rendered_payload_template(
            task=task,
            j2_task_text="Render Jinja2 NETCONF payload template",
            j2_tpl_path=tpl_path,
            custom_result=custom_result,
            task_failed=task_failed,
            info_msg=tpl_path,
            verbose=verbose,
            j2_tpl_name=tpl_name,
        )

    # Return the Nornir NETCONF result
    return Result(host=task.host, custom_result=custom_result, failed=task_failed)


def nc_edit_tpl_int_config(task: Task, tpl_startswith: str, verbose: bool = False) -> Result:
    """
    TBD
    """
    # Return the Nornir result as failed if the host have no interfaces
    iface_result = return_result_if_no_interfaces(task=task)
    # If the return in not None, then it's the custom Nornir result to return
    if isinstance(iface_result, str):
        return Result(host=task.host, custom_result=iface_result, failed=True)

    # Return the result if no Jinja2 interface templates for a 'tpl_startswith' string were found
    nc_tpl_result = return_result_if_no_template(task=task, is_iface=True, tpl_startswith=tpl_startswith)
    # If the return in a string, then it's the custom Nornir result to return
    if isinstance(nc_tpl_result, str):
        return Result(host=task.host, custom_result=nc_tpl_result, failed=False)

    #### Configure each interface with the Jinja2 rendered template #########################################

    j2_task_text = "Render Jinja2 NETCONF interface payload template"
    # Track if the overall task has failed
    task_failed = False
    # The custom_result list will be filled with the result of each interface
    custom_result = []

    # Exclude NoneType or empty string interface template names
    interfaces = [i for i in task.host["interfaces"] if i["int_template"]]
    # Exclude interface templates if they don't start with the tpl_startswith string
    interfaces = [i for i in interfaces if i["int_template"].startswith(tpl_startswith)]

    for interface in interfaces:
        # Set the interface template name
        tpl_name = interface["int_template"]
        # Check if the interface template name is in the host inventory
        if tpl_name in task.host:
            # Set the interface template path
            tpl_path = task.host[tpl_name]

            # Add additional interface data for Jinja2 **kwargs
            interface = add_interface_data(task=task, interface=interface)
            # Extract the interface name and the interface number into a variable and add the current
            # interface details for the Jinja2 **kwargs
            j2_kwargs = {
                "interface": {
                    "interface_name": extract_interface_name(interface["name"]),
                    "interface_number": extract_interface_number(interface["name"]),
                    **interface,
                }
            }

            # Render the Jinja2 payload template and configure the NETCONF candidate datastore
            custom_result, task_failed = netconf_configure_jinja2_rendered_payload_template(
                task=task,
                j2_task_text=j2_task_text,
                j2_tpl_path=tpl_path,
                custom_result=custom_result,
                task_failed=task_failed,
                info_msg=tpl_path,
                verbose=verbose,
                int_name=interface["name"],
                j2_tpl_name=tpl_name,
                j2_kwargs=j2_kwargs,
            )
        # Else the interface template name is not in the host inventory
        else:
            custom_result.append(
                f"{task_result(text=j2_task_text, changed=False, level_name='ERROR', failed=True)}\n"
                f"'{interface['name']} ({tpl_name})' -> NornirResponse <Success: False>\n"
                f"-> Interface template '{tpl_name}' not found in the host inventory"
            )
            task_failed = True

    # Return the Nornir NETCONF result
    return Result(host=task.host, custom_result=custom_result, failed=task_failed)


#### Nornir NETCONF Tasks in regular Function ###############################################################


def nc_cfg_cleanup(nr: Nornir, cfg_status: bool = True, verbose: bool = False) -> bool:
    """
    TBD
    """
    # Return False if cfg_status argument is False
    if not cfg_status:
        return False

    tasks = {
        nc_edit_cleanup_portchannel: "NETCONF portchannel cleanup",
        nc_edit_cleanup_svi: "NETCONF vlan interface cleanup",
        nc_edit_cleanup_vlan: "NETCONF vlan cleanup",
    }

    # Run each task from the Nornir tasks list
    for task, name in tasks.items():
        # Run the custom nornir task
        nc_result = nr.run(
            name=name,
            task=task,
            verbose=verbose,
            on_failed=True,
        )

        # Print the result
        print_result(result=nc_result, result_sub_list=True, attrs=["custom_result"])

        # If the task failed -> nc_result.failed is True. So return False if nc_result.failed is True
        if nc_result.failed:
            cfg_status = False

    return cfg_status


def nc_cfg_tpl(nr: Nornir, cfg_tasks: dict, cfg_status: bool = True, verbose: bool = False) -> bool:
    """
    TBD
    """

    # Return False if cfg_status argument is False
    if not cfg_status:
        return False

    # Run each task from config_tasks
    for tpl_startswith, task_text in cfg_tasks.items():
        # Run the custom nornir task nc_edit_tpl_config
        nc_result = nr.run(
            name=task_text,
            task=nc_edit_tpl_config,
            tpl_startswith=tpl_startswith,
            verbose=verbose,
            on_failed=True,
        )

        # Print the result
        print_result(result=nc_result, result_sub_list=True, attrs=["custom_result"])

        # If the task failed -> nc_result.failed is True. So return False if nc_result.failed is True
        if nc_result.failed:
            cfg_status = False

    return cfg_status


def nc_cfg_tpl_int(nr: Nornir, cfg_tasks: dict, cfg_status: bool = True, verbose: bool = False) -> bool:
    """
    TBD
    """

    # Return False if cfg_status argument is False
    if not cfg_status:
        return False

    # Run each task from interface_tasks
    for tpl_startswith, task_text in cfg_tasks.items():
        # Run the custom nornir task nc_edit_tpl_int_config
        nc_result = nr.run(
            name=task_text,
            task=nc_edit_tpl_int_config,
            tpl_startswith=tpl_startswith,
            verbose=verbose,
            on_failed=True,
        )

        # Print the result
        print_result(result=nc_result, result_sub_list=True, attrs=["custom_result"])

        # If the task failed -> nc_result.failed is True. So return False if nc_result.failed is True
        if nc_result.failed:
            cfg_status = False

    return cfg_status
