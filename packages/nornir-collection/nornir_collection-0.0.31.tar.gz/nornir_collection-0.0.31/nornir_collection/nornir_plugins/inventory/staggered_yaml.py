#!/usr/bin/env python3
"""
This module contains Nornir inventory plugin StaggeredYamlInventory.

The functions are ordered as followed:
- Helper Functions
- Inventory Plugin
"""

import pathlib
import glob
from typing import Literal
import ruamel.yaml
from nornir.core.inventory import Inventory, Group, Groups, Host, Hosts, Defaults, ParentGroups
from nornir.plugins.inventory.simple import _get_defaults, _get_inventory_element
from nornir_collection.utils import (
    print_task_name,
    task_info,
    task_error,
    exit_error,
    load_multiple_yaml_files_to_string,
)


#### Inventory Plugin #######################################################################################


class StaggeredYamlInventory:
    """
    This class is a deviation of the Nornir builtin SimpleInventory.
    This plugin have to be registered since Nornir 3.0
    """

    def __init__(
        self,
        hosts_base: str = "hosts.yaml",
        groups_base: str = "groups.yaml",
        defaults_base: str = "defaults.yaml",
        encoding: str = "utf-8",
    ) -> None:
        """
        StaggeredYamlInventory is an inventory plugin that loads data from multiple yaml files. The the base
        path all yaml files starting with hosts, groups, or defaults will be concatenated and loaded as dict.
        The yaml files follow the same structure as the native objects
        Args:
          hosts_base: base path recursively to files with hosts definition
          groups_base: basepath recursively to files with groups definition.
                If it doesn't exist it will be skipped
          defaults_base: base path recursively to files with defaults definition.
                If it doesn't exist it will be skipped
          encoding: Encoding used to save inventory files. Defaults to utf-8
        """

        self.task_text = "NORNIR initialize inventory plugin StaggeredYamlInventory"
        # Get the base path for the hosts, groups and defaults filed
        self.hosts_base = pathlib.Path(hosts_base).expanduser()
        self.groups_base = pathlib.Path(groups_base).expanduser()
        self.defaults_base = pathlib.Path(defaults_base).expanduser()
        # Create lists with all files recursively which starts with hosts, groups or defaults
        self.hosts_files = glob.glob(str(self.hosts_base) + "/**/hosts*.yaml", recursive=True)
        self.groups_files = glob.glob(str(self.groups_base) + "/**/groups*.yaml", recursive=True)
        self.defaults_files = glob.glob(str(self.defaults_base) + "/**/defaults*.yaml", recursive=True)
        self.encoding = encoding

    def load_multiple_yaml_files(self, inv_type: Literal["hosts", "groups", "defaults"]) -> dict:
        """
        TBD
        """
        yml = ruamel.yaml.YAML(typ="safe")
        yaml_string = str()

        # Use mapping to avoid long if elif else statements
        file_list = {"hosts": self.hosts_files, "groups": self.groups_files, "defaults": self.defaults_files}
        # Load the yaml files from file_list and concatinate them to one string
        yaml_string = load_multiple_yaml_files_to_string(file_list=file_list[inv_type], silent=True)

        try:
            yaml_dict = yml.load(yaml_string) or {}

        except ruamel.yaml.constructor.DuplicateKeyError as error:
            print(task_error(text=self.task_text, changed=False))
            print(f"'Load {inv_type} inventory yaml files' -> NornirResponse <Success: False>")
            print("-> Duplicate key in yaml files", "\n\n", error)
            # Exit the script with a proper message
            exit_error(
                task_text=self.task_text,
                text=f"ALERT: LOAD {inv_type.upper()} INVENTORY YAML FILES FAILED!",
                msg=f"-> Analyse the {inv_type} inventory yaml files and identify the root cause",
            )

        return yaml_dict

    def load(self) -> Inventory:
        """
        TBD
        """
        print_task_name(text=self.task_text)

        if self.defaults_files:
            defaults_dict = self.load_multiple_yaml_files(inv_type="defaults")

            defaults = _get_defaults(defaults_dict)
        else:
            defaults = Defaults()

        hosts = Hosts()
        hosts_dict = self.load_multiple_yaml_files(inv_type="hosts")

        for n, h in hosts_dict.items():
            hosts[n] = _get_inventory_element(Host, h, n, defaults)

        groups = Groups()
        if self.groups_files:
            groups_dict = self.load_multiple_yaml_files(inv_type="groups")

            for n, g in groups_dict.items():
                groups[n] = _get_inventory_element(Group, g, n, defaults)

            for g in groups.values():
                g.groups = ParentGroups([groups[g] for g in g.groups])

        try:
            for h in hosts.values():
                h.groups = ParentGroups([groups[g] for g in h.groups])

        except KeyError as error:
            print(task_error(text=self.task_text, changed=False))
            print("'Assign groups to hosts' -> NornirResponse <Success: False>")
            print(f"-> Group {error} not found")
            # Exit the script with a proper message
            exit_error(
                task_text=self.task_text,
                text="ALERT: ASSIGN GROUPS TO HOSTS FAILED!",
                msg="-> Analyse the Nornir group files",
            )

        print(task_info(text=self.task_text, changed=False))
        print(f"'{self.task_text}' -> NornirResponse <Success: True>")
        print("-> Loaded YAML inventory data")

        return Inventory(hosts=hosts, groups=groups, defaults=defaults)
