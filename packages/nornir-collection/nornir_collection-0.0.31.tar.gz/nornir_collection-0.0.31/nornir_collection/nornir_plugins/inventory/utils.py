#!/usr/bin/env python3
"""
This module contains Nornir inventory plugins and Nornir Init functions.

The functions are ordered as followed:
- Inventory Transform Functions
- Nornir Init Functions
"""

import os
import argparse
import sys
import time
from typing import Literal
from dotenv import load_dotenv
from nornir import InitNornir
from nornir.core import Nornir
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir_collection.nornir_plugins.inventory.netbox import DSCNetBoxInventory
from nornir_collection.netbox.inventory import load_additional_netbox_data
from nornir_collection.utils import (
    print_task_title,
    task_name,
    task_info,
    task_error,
    nr_filter_args,
    exit_error,
    iterate_all,
    list_flatten,
    transform_env,
)


#### Inventory Transform Functions ##########################################################################


def nr_transform_host_creds_from_env(nr: Nornir, silent: bool = False) -> None:
    """
    This function loads the host login credentials from environment variables and stores them directly under
    the host inventory level. This function can be extended to to more host transformation.
    """

    if not silent:
        task_text = "NORNIR transform host credentials env variable"
        print(task_name(text=task_text))

    # Recreate Nornir 2.x transform function behavior
    for host in nr.inventory.hosts.values():
        # Verify that login credentials are set as environment variables. Raise a TypeError when is None
        try:
            # The host get the username and password loaded from an environment variable
            host.username = os.environ[host.username]
            host.password = os.environ[host.password]

            # Continue with the next for loop iteration
            continue

        except KeyError as error:
            print(task_error(text=task_text, changed=False))
            print(f"'{task_text}' -> OS.EnvironResponse <Success: False>")
            print(f"-> Environment variable {error} for host {host} not found\n")
        except TypeError:
            print(task_error(text=task_text, changed=False))
            print(f"'{task_text}' -> OS.EnvironResponse <Success: False>")
            print(f"-> Nornir inventory key username and/or password for host {host} not found\n")

        # Exit the script with a proper message
        exit_error(
            task_text=task_text,
            text="ALERT: TRANSFORM HOST CREDENTIALS FAILED!",
            msg="-> Analyse the error message and identify the root cause",
        )

    # Verify that default login credentials are set as environment variables. Raise a TypeError when is None
    try:
        nr.inventory.defaults.username = os.environ[nr.inventory.defaults.username]
        nr.inventory.defaults.password = os.environ[nr.inventory.defaults.password]

    except KeyError as error:
        print(task_error(text=task_text, changed=False))
        print(f"'{task_text}' -> OS.EnvironResponse <Success: False>")
        print(f"-> Environment variable {error} not found\n")

        # Exit the script with a proper message
        exit_error(
            task_text=task_text,
            text="ALERT: TRANSFORM DEFAULT CREDENTIALS FAILED!",
            msg="-> Analyse the error message and identify the root cause",
        )
    except TypeError:
        print(task_error(text=task_text, changed=False))
        print(f"'{task_text}' -> OS.EnvironResponse <Success: False>")
        print("-> Nornir default inventory key username and/or password not found\n")

        # Exit the script with a proper message
        exit_error(
            task_text=task_text,
            text="ALERT: TRANSFORM DEFAULT CREDENTIALS FAILED!",
            msg="-> Analyse the error message and identify the root cause",
        )

    if not silent:
        print(task_info(text=task_text, changed=False))
        print(f"'{task_text}' -> OS.EnvironResponse <Success: True>")
        print(f"-> Transformed {len(nr.inventory.hosts)} host credentials env variables")


def _tuple_with_env_list(iterable: dict) -> tuple:
    """
    TBD
    """
    env_keys = []
    envs = []

    # Iterate over all nested dict or list elements and return a generator object
    for env in iterate_all(iterable=iterable, returned="key-value"):
        if str(env[0]).startswith("env_"):
            env_keys.append(str(env[0]))
            envs.append(str(env[1]))

    return env_keys, envs


def nr_transform_inv_from_env(
    inv_type: Literal["hosts", "groups", "defaults"],
    iterable: dict,
    env_mandatory: dict = False,
    verbose: bool = False,
    silent: bool = False,
) -> None:
    """
    This function transforms all environment variables in the iterable. It loops over a nested dictionary and
    if the key startswith "env_", it loads the environment variable specified by the value and replace the
    value with the environment variable. Optional a mandatory argument which have to be a dictionary can be
    specified. This dictionary must be part of the iterable and follows the same procedure to transform the
    environment variables. The optional argument verbose prints extensive results. The function returns None.
    """
    #### Prepare mandatory and non-mandatory env variables ##################################################

    mandatory_transform_env_keys, mandatory_transform_envs = _tuple_with_env_list(iterable=env_mandatory)
    transform_env_keys, transform_envs = _tuple_with_env_list(iterable=iterable)

    # Subtract the non-mandatory env_keys and envs from the mandatory env_keys and envs list
    transform_env_keys = [item for item in transform_env_keys if item not in mandatory_transform_env_keys]
    transform_envs = [item for item in transform_envs if item not in mandatory_transform_envs]

    # Flatten the transform_envs if it contains lists of lists
    transform_envs = list_flatten(transform_envs)

    #### Transform all mandatory env variables ##############################################################

    # If the mandatory_transform_env_keys list it not empty -> Transform all env variables in the list
    if mandatory_transform_env_keys:
        if not silent:
            task_text = f"NORNIR transform mandatory {inv_type} env variable"
            print(task_name(text=task_text))

        # Verify that all mandatory env key-value pairs exists in the Nornir inventory
        for key, value in env_mandatory.items():
            if key not in list(iterate_all(iterable=iterable, returned="key")):
                print(task_error(text=task_text, changed=False))
                print(f"'{task_text} {value}' -> OS.EnvironResponse <Success: False>")
                print(f"-> Nornir inventory key-value pair '{key}':'{value}' not found\n")
                sys.exit(1)

        try:
            # Loop over the generator object items and add the matching elemens based on the key to a list
            for env_key in mandatory_transform_env_keys:
                # If the environ load fails a KeyError would be raised and catched by the exception
                transform_env(iterable=iterable, startswith=env_key)

            if not silent:
                print(task_info(text=task_text, changed=False))
                print(f"'{task_text}' -> OS.EnvironResponse <Success: True>")
                print(f"-> Transformed {len(mandatory_transform_envs)} mandatory env variables")
                if verbose:
                    for env in mandatory_transform_envs:
                        print(f"  - {env}")

        except KeyError as error:
            print(task_error(text=task_text, changed=False))
            print(f"'{task_text} {error}' -> OS.EnvironResponse <Success: False>")
            print(f"-> Environment variable {error} not found\n")
            sys.exit(1)

    #### Transform all other envs if transform_envs is not empty ############################################

    # If the transform_env_keys list it not empty -> Transform all env variables in the list
    if transform_envs:
        if not silent:
            task_text = f"NORNIR transform non-mandatory {inv_type} env variable"
            print(task_name(text=task_text))

        try:
            # Loop over the generator object items and add the matching elemens based on the key to a list
            for env_key in transform_env_keys:
                # If the environ load fails a KeyError would be raised and catched by the exception
                transform_env(iterable=iterable, startswith=env_key)

            if not silent:
                print(task_info(text=task_text, changed=False))
                print(f"'{task_text}' -> OS.EnvironResponse <Success: True>")
                print(f"-> Transformed {len(transform_envs)} non-mandatory env variables")
                if verbose:
                    for env in transform_envs:
                        print(f"  - {env}")

        except KeyError as error:
            print(task_error(text=task_text, changed=False))
            print(f"'{task_text} {error}' -> OS.EnvironResponse <Success: False>")
            print(f"-> Environment variable {error} not found\n")
            sys.exit(1)


#### Nornir Init Functions ##################################################################################


def init_nornir(
    config_file: str,
    env_mandatory: dict = False,
    args: argparse.Namespace = False,
    add_netbox_data: dict[str:bool] = None,
    silent: bool = False,
) -> Nornir:
    """
    The Nornir inventory will be initialized, the host username and password will be transformed and loaded
    from environment variables. The same transformation will load all the environment variables from all
    inventory data keys which start with env_ and ensures that the mandatory specified environment variables
    are defined in the inventory. The function returns a filtered Nornir object or quits with an error message
    in case of issues during the function.
    """
    if not silent:
        print_task_title("Initialize Nornir Inventory")

    # Set a timer to track how long the init_nornir functions takes to finish
    timer_start = time.time()

    # Register the DSCNetBoxInventory Plugin
    InventoryPluginRegister.register("DSCNetBoxInventory", DSCNetBoxInventory)

    # Take environment variables from .env and override existing host environment variables. If .env or the
    # environment variable don't exist like in production environment, then directly the host environment
    # variable takes presence. This approach fullfil the 12-factor application rules.
    load_dotenv(".env", override=True)

    # Initialize Nornir Object with a config file
    # Set and unset the NB_SILENT environment variable to control the Nornir output of the inventory plugin
    os.environ["NB_SILENT"] = str(silent)
    nr = InitNornir(config_file=config_file)
    os.environ.pop("NB_SILENT", None)

    # Load additional data from NetBox into the Nornir inventory
    if add_netbox_data:
        load_additional_netbox_data(nr=nr, add_netbox_data=add_netbox_data, silent=silent)

    # Transform the host username and password from environment variables
    nr_transform_host_creds_from_env(nr=nr, silent=silent)

    # Transform the inventory and load all env variables staring with "env_" in the defaults yaml files
    nr_transform_inv_from_env(
        inv_type="defaults",
        iterable=nr.inventory.defaults.data,
        verbose=args.verbose if args else False,
        env_mandatory=env_mandatory,
        silent=silent,
    )

    # Transform the inventory and load all env variables staring with "env_" in the groups yaml files
    for group in nr.inventory.groups:
        nr_transform_inv_from_env(
            inv_type="groups",
            iterable=nr.inventory.groups[group].data,
            verbose=args.verbose if args else False,
            silent=silent,
        )

    # Filter the Nornir inventory based on the provided arguments from argparse
    if args:
        nr = nr_filter_args(nr=nr, args=args, silent=silent)

    if not silent:
        # Print the timer result
        task_text = "NORNIR initialize timer"
        print(f"{task_name(text=task_text)}")
        print(task_info(text=task_text, changed=False))
        print(f"'{task_text}' -> NornirResponse <Success: True>")
        print(f"-> Initialize Nornir finished in: {round(time.time() - timer_start, 1)}s")

    return nr
