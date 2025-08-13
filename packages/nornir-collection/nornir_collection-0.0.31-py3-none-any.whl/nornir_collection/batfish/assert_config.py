#!/usr/bin/env python3
"""
This module contains general functions and tasks related to Batfish.

The functions are ordered as followed:
- Batfish Helper Functions
- Nornir Batfish Tasks
- Nornir Batfish Tasks in regular Function
"""

from pybatfish.client.session import Session
from nornir.core import Nornir
from nornir.core.task import Task, Result
from nornir_collection.batfish.utils import (
    batfish_question_failed,
    batfish_assert_type_failed,
    batfish_exit_error,
)
from nornir_collection.utils import print_result, task_result, list_flatten, get_dict_value_by_path


#### Batfish Helper Functions ################################################################################


def batfish_assert_cfg_prop(task: Task, data: tuple, name_add: str = False) -> list:
    """
    Batfish assert helper task to assert the ref_prop against the cfg_prop based on the ref_prop data type.
    The col_name specifies the configuration property which should be asked to Batfish.
    """
    # Extract the variables from the data tuple
    col_name, ref_prop, cfg_prop = data
    # Set the name_add variable if exists, else col_name
    name_add = name_add if name_add else col_name

    if isinstance(ref_prop, str):
        # Define the property in the snapshot
        snap_prop = cfg_prop[col_name].to_string(index=False)
        snap_prop = snap_prop.rstrip()
        snap_prop = snap_prop.lstrip()
        # Set the Nornir task failed variable
        failed = bool(ref_prop != snap_prop)
        cfg_result = f"-> Expected: '{ref_prop}'\n-> Configured: '{snap_prop}'"

    elif isinstance(ref_prop, list):
        ref_prop = list_flatten(ref_prop)
        # Define the property in the snapshot
        snap_prop = list_flatten(cfg_prop[col_name].tolist())
        snap_prop = [str(x) for x in snap_prop]
        # Find extra and missing referency properties
        ref_prop_extra = [x for x in snap_prop if x not in ref_prop]
        ref_prop_missing = [x for x in ref_prop if x not in snap_prop]
        # Set the Nornir task failed variable
        failed = bool(ref_prop_extra + ref_prop_missing)
        cfg_result = (
            f"-> Expected: {ref_prop}\n"
            f"-> Missing (to add): {ref_prop_missing if ref_prop_missing else '[]'}\n"
            f"-> Extra (to remove): {ref_prop_extra if ref_prop_extra else '[]'}"
        )

    else:
        # Set the Nornir task failed variable
        failed = True
        cfg_result = (
            f"->'ref_prop' argument type {type(ref_prop)} is not implemented to assert\n"
            f"-> Update the function _batfish_assert_cfg_prop() to support this 'ref_prop' data type"
        )

    # Set the Nornir result to return
    level_name = "ERROR" if failed else "INFO"
    result = (
        f"{task_result(text=f'{task.name} {name_add}', changed=False, level_name=level_name)}\n"
        f"'{task.name} {col_name}' -> BatfishResponse <Success: {not failed}>\n"
        f"{cfg_result}"
    )

    return result, failed


def batfish_get_ref_props_from_nr_inv(task: Task, inv_key: str) -> dict:
    """
    Loop over all hosts keys to find keys which starts with the inv_startswith string and add the values
    to a dict. Then return this dict which should contain all ref_props data.
    """
    ref_props = {}
    # Loop over all hosts keys to find keys which starts with the inv_startswith string
    for key, value in task.host.items():
        if key.startswith(inv_key):
            # Update the ref_props dict with the value
            ref_props.update(value)

    return ref_props


#### Nornir Batfish Tasks ####################################################################################


def batfish_assert_cfg_node_property_task(task: Task, nr_inv: bool, data: tuple[Session, dict]) -> Result:
    """
    Nornir task to assert Batfish node properties agains values from the Nornir inventory or direct specified
    values in the ref_props dict. The ref_props argument in the data tuple specifies the Batfish node property
    question to ask as the key The value can be the Nornir inventory which have to be added as  a map list
    of the Nornir inventory dict keys if nr_inv is True or the correct value have to be specified if nr_inv
    is False.

    ref_props = {
        "Domain_Name": ["cfg_domain_name"],
        "NTP_Servers": ["cfg_ntp", "server"],
        "NTP_Source_Interface": ["cfg_ntp", "source"],
    }
    """

    # Extract the variables from the data tuple
    bf, ref_props = data

    # If the ref_props is a string to specify the inventory startswith key, then create a dict with all
    # inventory keys which start with this string (nested dict not supported)
    if isinstance(ref_props, str):
        ref_props = batfish_get_ref_props_from_nr_inv(task=task, inv_key=ref_props)

    # Set the initial Nornir Result object variables
    result = []
    failed = False

    # Extract the node properties for the host
    cfg_prop = bf.q.nodeProperties(nodes=str(task.host)).answer().frame()

    # If the cfg_prop dataframe is empty
    if cfg_prop.empty:
        subresult, subresult_failed = batfish_question_failed(task=task, df=cfg_prop)
        # Add the subresult to the Nornir result list
        result.append(subresult)
        # Return the Nornir result
        return Result(host=task.host, result=result, failed=True)

    # Loop over each column name, reference property key-value pair in the dict
    for col_name, ref_prop in ref_props.items():
        if nr_inv:
            # Get the value from the Nornir inventory with the ref_prop map list
            ref_prop = get_dict_value_by_path(data_dict=task.host, map_list=ref_prop)

        # Create a tuple with all needed data to assert the Batfish question
        data = (col_name, ref_prop, cfg_prop)

        # Assert the correct ref_prop type
        if isinstance(ref_prop, (str, list)):
            subresult, subresult_failed = batfish_assert_cfg_prop(task=task, data=data)
        else:
            data = (col_name, ref_prop, "'str' or 'list'")
            subresult, subresult_failed = batfish_assert_type_failed(task=task, data=data)

        # Add the subresult to the Nornir result list
        result.append(subresult)
        if subresult_failed:
            failed = True

    # Return the Nornir result
    return Result(host=task.host, result=result, failed=failed)


def batfish_assert_cfg_interface_property_task(
    task: Task, nr_inv: bool, data: tuple[Session, dict]
) -> Result:
    """
    Nornir task to assert Batfish interface properties agains values from the Nornir inventory or direct
    specified values in the ref_props dict. The ref_props argument in the data tuple specifies a dict for each
    interface with the Batfish interface property question to ask as the key. The value can be the Nornir
    inventory which have to be added as a map list of the Nornir inventory dict keys if nr_inv is True or
    the correct value have to be specified if nr_inv is False.

    ref_props = {
        "FortyGigabitEthernet1/1/1" : {
            "Switchport_Trunk_Encapsulation" : "DOT1Q",
            "Admin_Up" : "True",
            "Active" : "True",
        }
        "FortyGigabitEthernet1/1/2" : {
            "Switchport_Trunk_Encapsulation" : "DOT1Q",
            "Admin_Up" : "True",
            "Active" : "True",
        }
    }
    """

    # Extract the variables from the data tuple
    bf, ref_props = data

    # If the Nornir inventory should be used and ref_props is a string to specify the inventory startswith
    # key, then create a dict with all inventory keys which start with this string (nested dict not supported)
    if nr_inv and isinstance(ref_props, str):
        ref_props = batfish_get_ref_props_from_nr_inv(task=task, inv_key=ref_props)

    # Set the initial Nornir Result object variables
    result = []
    failed = False

    # Loop over each interface
    for interface in ref_props.keys():
        # Extract the interface properties for the host
        cfg_prop = bf.q.interfaceProperties(nodes=str(task.host), interfaces=interface).answer().frame()

        # If the cfg_prop dataframe is empty
        if cfg_prop.empty:
            subresult, subresult_failed = batfish_question_failed(task=task, df=cfg_prop, name_add=interface)
            # Add the subresult to the Nornir result list
            result.append(subresult)
            if subresult_failed:
                failed = True
        else:
            # Loop over each column name, reference property key-value pair in the dict
            for col_name, ref_prop in ref_props[interface].items():
                if nr_inv:
                    # Get the value from the Nornir inventory with the ref_prop map list
                    ref_prop = get_dict_value_by_path(data_dict=task.host, map_list=ref_prop)

                # Create a tuple with all needed data to assert the Batfish question
                data = (col_name, ref_prop, cfg_prop)

                # Assert the correct ref_prop type
                if isinstance(ref_prop, (str, list)):
                    subresult, subresult_failed = batfish_assert_cfg_prop(
                        task=task, data=data, name_add=interface
                    )
                else:
                    data = (col_name, ref_prop, "'str' or 'list'")
                    subresult, subresult_failed = batfish_assert_type_failed(
                        task=task, data=data, name_add=interface
                    )

                # Add the subresult to the Nornir result list
                result.append(subresult)
                if subresult_failed:
                    failed = True

    # Return the Nornir result
    return Result(host=task.host, result=result, failed=failed)


def batfish_assert_cfg_switched_vlan_property_task(
    task: Task, nr_inv: bool, data: tuple[Session, dict]
) -> Result:
    """
    Nornir task to assert Batfish switched vlan properties agains values from the Nornir inventory or direct
    specified values in the ref_props dict. The ref_props argument in the data tuple specifies the Batfish
    node property question to ask as the key The value can be the Nornir inventory which have to be added
    as a map list of the Nornir inventory dict keys if nr_inv is True or the correct value have to be
    specified if nr_inv is False.

    ref_props = {
        "VLAN_ID": ["cfg_vlans"],
        "VLAN_ID_ADD": ["cfg_vlans_add"],
    }
    """

    # Extract the variables from the data tuple
    bf, ref_props = data

    # If the Nornir inventory should be used and ref_props is a string to specify the inventory startswith
    # key, then create a dict with all inventory keys which start with this string (nested dict not supported)
    if nr_inv and isinstance(ref_props, str):
        ref_props = batfish_get_ref_props_from_nr_inv(task=task, inv_key=ref_props)

    # Set the initial Nornir Result object variables
    result = []
    failed = False

    # Extract the node properties for the host
    cfg_prop = bf.q.switchedVlanProperties(nodes=str(task.host)).answer().frame()

    # If the cfg_prop dataframe is empty
    if cfg_prop.empty:
        subresult, subresult_failed = batfish_question_failed(task=task, df=cfg_prop)
        # Add the subresult to the Nornir result list
        result.append(subresult)
        # Return the Nornir result
        return Result(host=task.host, result=result, failed=True)

    # Loop over each column name, reference property key-value pair in the dict
    for col_name, ref_prop in ref_props.items():
        if nr_inv:
            # Get the value from the Nornir inventory with the ref_prop map list
            ref_prop = get_dict_value_by_path(data_dict=task.host, map_list=ref_prop)
            # If the Nornir inventory is a dict, assume that the key is the vlan number and create a list
            if isinstance(ref_prop, dict):
                ref_prop = [str(vlan) for vlan in ref_prop.keys()]
            # If the custom column name VLAN_ID_ADD exists in the ref_prop, then add these vlans to the list
            if "VLAN_ID_ADD" in ref_prop:
                # Get the value from the Nornir inventory with the ref_prop map list
                ref_prop_add = get_dict_value_by_path(data_dict=task.host, map_list=ref_prop["VLAN_ID_ADD"])
                # If the Nornir inventory is a dict, assume that the key is the vlan number and create a list
                if isinstance(ref_prop_add, dict):
                    ref_prop_add = [str(vlan) for vlan in ref_prop_add.keys()]
                # Add both vlan lists together
                ref_prop = ref_prop + ref_prop_add

        # Add vlan 1 as it's the default and can't be deleted
        ref_prop = ["1"] + ref_prop

        # Create a tuple with all needed data to assert the Batfish question
        data = (col_name, ref_prop, cfg_prop)

        # Assert the correct ref_prop type
        if isinstance(ref_prop, list):
            subresult, subresult_failed = batfish_assert_cfg_prop(task=task, data=data)
        else:
            data = (col_name, ref_prop, "'list'")
            subresult, subresult_failed = batfish_assert_type_failed(task=task, data=data)

        # Add the subresult to the Nornir result list
        result.append(subresult)
        if subresult_failed:
            failed = True

    # Return the Nornir result
    return Result(host=task.host, result=result, failed=failed)


#### Nornir Batfish Tasks in regular Function ################################################################


def batfish_assert_config_property(nr: Nornir, nr_inv: bool, data: tuple, soft: bool = False) -> Result:
    """
    This function runs a Nornir task to ask Batfish configuration properties. The batfish session, the batfish
    question and the ref_props dict according to the specified batfish question have to be specified as the
    data tuple. The nr_inv argument specified is the values to assert should be loaded from the Nornir
    inventory by a dict key map list or are specified already directly correct.
    The result is printed in Nornir style and in case of an assert error the script exits with error code 1.
    """

    # Extract the variables from the data tuple
    bf, bf_question, ref_props = data

    # Map list to identify which Nornir task to execute for the correct Batfish question
    batfish_config_property_task = {
        "node": batfish_assert_cfg_node_property_task,
        "interface": batfish_assert_cfg_interface_property_task,
        "vlan": batfish_assert_cfg_switched_vlan_property_task,
    }

    # Run the Nornir task to assert Batfish configuration properties
    result = nr.run(
        task=batfish_config_property_task[bf_question],
        name=f"BATFISH query {bf_question}",
        nr_inv=nr_inv,
        data=(bf, ref_props),
        on_failed=True,
    )

    # Print the Nornir task result
    print_result(result=result, result_sub_list=True)

    if not soft:
        # If the task failed exit with error code 1
        if result.failed:
            batfish_exit_error(result=result, bf_question="config")
