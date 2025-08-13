#!/usr/bin/env python3
"""
This module contains the Nornir inventory plugin DSCNetBoxInventory.

The functions are ordered as followed:
- Helper Functions
- Inventory Plugin
"""

import os
import logging
from typing import Any, Dict, List, Optional, Union, Type
import requests
import ruamel.yaml
from nornir.core.inventory import (
    ConnectionOptions,
    Defaults,
    Group,
    Groups,
    Host,
    HostOrGroup,
    Hosts,
    Inventory,
    ParentGroups,
)
from nornir_collection.utils import print_task_name, task_info

logger = logging.getLogger(__name__)


#### Helper Functions #######################################################################################


def _get_connection_options(data: Dict[str, Any]) -> Dict[str, ConnectionOptions]:
    """
    TBD
    """

    cp = {}
    for cn, c in data.items():
        cp[cn] = ConnectionOptions(
            hostname=c.get("hostname"),
            port=c.get("port"),
            username=c.get("username"),
            password=c.get("password"),
            platform=c.get("platform"),
            extras=c.get("extras"),
        )
    return cp


def _get_defaults(data: Dict[str, Any]) -> Defaults:
    """
    TBD
    """
    return Defaults(
        hostname=data.get("hostname"),
        port=data.get("port"),
        username=data.get("username"),
        password=data.get("password"),
        platform=data.get("platform"),
        data=data.get("data"),
        connection_options=_get_connection_options(data.get("connection_options", {})),
    )


def _get_inventory_element(
    typ: Type[HostOrGroup], data: Dict[str, Any], name: str, defaults: Defaults
) -> HostOrGroup:
    """
    TBD
    """
    return typ(
        name=name,
        hostname=data.get("hostname"),
        port=data.get("port"),
        username=data.get("username"),
        password=data.get("password"),
        platform=data.get("platform"),
        data=data.get("data"),
        groups=data.get("groups"),  # this is a hack, we will convert it later to the correct type
        defaults=defaults,
        connection_options=_get_connection_options(data.get("connection_options", {})),
    )


#### Inventory Plugin #######################################################################################


class DSCNetBoxInventory:
    """
    This class is a deviation of the Nornir plugin NetBoxInventory2.
    This plugin have to be registered since Nornir 3.0

    Inventory plugin that uses `NetBox <https://github.com/netbox-community/netbox>`_ as backend.
    Note:
        Additional data provided by the NetBox devices API endpoint will be
        available through the NetBox Host data attribute.
    Environment Variables:
        * ``NB_URL``: Corresponds to nb_url argument
        * ``NB_TOKEN``: Corresponds to nb_token argument
    Arguments:
        nb_url: NetBox url
        nb_token: NetBox API token
        ssl_verify: Enable/disable certificate validation
            (defaults to True)
    """

    def __init__(
        self,
        nb_url: Optional[str] = None,
        nb_token: Optional[str] = None,
        ssl_verify: Union[bool, str] = True,
        nb_silent: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Init function
        """
        nb_url = nb_url or os.environ.get("NB_URL")
        nb_token = nb_token or os.environ.get("NB_TOKEN")
        nb_silent = nb_silent or os.environ.get("NB_SILENT")

        self.task_text = "NORNIR initialize inventory plugin DSCNetBoxInventory"
        self.nb_url = nb_url
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Token {nb_token}"})
        self.session.verify = ssl_verify
        self.nb_silent = nb_silent

    def _get_resources(self, url: str, params: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
        """
        TBD
        """
        # Define the resource list
        resources: List[Dict[str, Any]] = []
        # While there is a next page continue the loop
        while url:
            # Do the http request
            r = self.session.get(url, params=params)
            # Verify the response code
            if not r.status_code == 200:
                raise ValueError(f"Failed to get data from NetBox instance {self.nb_url}")
            # Extract the json data from the http response
            resp = r.json()
            # Add the response to the resource list
            resources.extend(resp.get("results"))
            # Get the url of the next page
            url = resp.get("next")

        # Retrun the resources list
        return resources

    def load(self) -> Inventory:
        """
        TBD
        """
        yml = ruamel.yaml.YAML(typ="safe")

        if not self.nb_silent:
            print_task_name(text=self.task_text)

        # Load all NetBox devices with a primary IP address assigned
        devices: List[Dict[str, Any]] = []
        devices.extend(
            self._get_resources(
                url=f"{self.nb_url}/api/dcim/devices/",
                params={"limit": 1000, "has_primary_ip": True},
            )
        )

        # Create the defaults
        defaults = Defaults()
        defaults_dict: Dict[str, Any] = {}
        with open("inventory/defaults.yaml", "r", encoding="utf-8") as f:
            defaults_dict = yml.load(f) or {}
        defaults = _get_defaults(defaults_dict)

        # Create the hosts
        hosts = Hosts()
        for device in devices:
            serialized_device: Dict[Any, Any] = {}
            serialized_device["data"] = device

            # Remove the custom_fields key and make the custom_field native to Nornir
            for cf, value in device["custom_fields"].items():
                serialized_device["data"][cf] = value
            serialized_device["data"].pop("custom_fields")

            # Remove the config_context key and make the config_context native to Nornir
            for cc, value in device["config_context"].items():
                serialized_device["data"][cc] = value
            serialized_device["data"].pop("config_context")

            # Set the Nornir hostname (ip address or fqdn)
            hostname = None
            if device.get("primary_ip"):
                hostname = device.get("primary_ip", {}).get("address", "").split("/")[0]
            else:
                if device.get("name") is not None:
                    hostname = device["name"]
            serialized_device["hostname"] = hostname

            # Set the Nornir host name
            if serialized_device["data"].get("virtual_chassis"):
                name = serialized_device["data"].get("virtual_chassis").get("name")
            else:
                name = serialized_device["data"].get("name") or str(serialized_device["data"].get("id"))

            # Add virtual chassis master serial to the virtual_chassis dict
            if serialized_device["data"].get("virtual_chassis"):
                master_serial = device["serial"] if device["serial"] else None
                serialized_device["data"]["virtual_chassis"]["master"]["serial"] = master_serial

            # Flatten the list of Tags which contains only the slug of each NetBox tag
            device["tags"] = [tag["name"] for tag in device["tags"]]

            # Extract the device connection options
            # Add Nornir connection options from the device context data
            if "connection_options" in device and device["connection_options"] is not None:
                serialized_device["connection_options"] = device["connection_options"]
            else:
                serialized_device["connection_options"] = {}
            # Remove the connection_options key from the serialized_device data
            if (
                "connection_options" in serialized_device["data"]
                and serialized_device["data"]["connection_options"] is not None
            ):
                serialized_device["data"].pop("connection_options")

            # Set the Nornir host elements
            hosts[name] = _get_inventory_element(Host, serialized_device, name, defaults)

        # Create the groups
        groups = Groups()
        groups_dict: Dict[str, Any] = {}
        for n, g in groups_dict.items():
            groups[n] = _get_inventory_element(Group, g, n, defaults)
        for g in groups.values():
            g.groups = ParentGroups([groups[g] for g in g.groups])
        for h in hosts.values():
            h.groups = ParentGroups([groups[g] for g in h.groups])

        if not self.nb_silent:
            # Print the DSCNetBoxInventory result
            print(task_info(text=self.task_text, changed=False))
            print(f"'{self.task_text}' -> NornirResponse <Success: True>")
            print(f"-> Loaded NetBox base inventory data of {len(hosts)} devices")

        return Inventory(hosts=hosts, groups=groups, defaults=defaults)
