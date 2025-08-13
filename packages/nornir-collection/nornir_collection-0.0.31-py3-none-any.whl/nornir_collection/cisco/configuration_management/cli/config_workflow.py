#!/usr/bin/env python3
"""
This module contains complete CLI screen-scraping configuration workflows with Nornir.

The functions are ordered as followed:
- Complete CLI configuration workflows
"""

from nornir.core import Nornir
from nornir_collection.cisco.configuration_management.cli.config_tasks import (
    jinja2_generate_config,
    cfg_eem_replace_config,
    cfg_jinja2_config,
    cfg_multiline_banner,
    cfg_tpl_int_cli,
    save_config_cli,
)
from nornir_collection.utils import (
    print_task_title,
)

#### Complete CLI Configuration Workflow 01 ##################################################################


def cli_cfg_network_from_code_01(
    nr: Nornir, banner_motd: str, rebuild: bool = False, verbose: bool = False
) -> bool:
    """
    This function improves modularity as it is used within multiple scripts. The network will be reconfigured
    to from the day0 config its desired state.
    """

    print_task_title("Configure network from code")

    # Set a variable to verify the network config status
    cfg_status = True

    # Returns a Nornir AggregatedResult object containing all generated configs by Jinja2 or terminates the
    # script if one or more tasks failed
    j2_base_config = jinja2_generate_config(
        nr=nr,
        name="Jinja2 render base config",
        path="cli_path_tpl_base_config",
        template="cli_payload_tpl_base_config",
        verbose=verbose,
    )
    # cfg_status validation is not needed as the script ends with an error in case there is an issue with
    # one or more config renderings

    # If args.rebuild it True load the day0 config, otherwise load the golden-config
    if rebuild:
        # Replace the running-config with the day0 config from the switch flash:
        cfg_status = cfg_eem_replace_config(
            nr=nr,
            name="Scrapli load day0-config",
            eem_name="eem_load_day0_config",
            file="flash:day0-config",
            verbose=verbose,
        )

    else:
        # Replace the running-config with the golden-config from the switch flash:
        cfg_status = cfg_eem_replace_config(
            nr=nr,
            name="Scrapli load golden-config",
            eem_name="eem_load_golden_config",
            file="flash:golden-config",
            verbose=verbose,
        )

    # Configures the Jinja2 generated config from the jinja2_generate_config() function returned
    # AggregatedResult object -> j2_config
    if cfg_status:
        cfg_status = cfg_jinja2_config(
            nr=nr,
            name="Scrapli apply Jinja2 rendered base config",
            jinja2_result=j2_base_config,
            verbose=verbose,
        )

    # Configures the Cisco motd multi-line banner
    if cfg_status:
        cfg_status = cfg_multiline_banner(
            nr=nr,
            name="Scrapli configure motd multi-line banner",
            multiline_banner=banner_motd,
            verbose=verbose,
        )

    # Configures all interfaces which are part of an interface template template
    if cfg_status:
        cfg_status = cfg_tpl_int_cli(
            nr=nr,
            name="Scrapli configure interface templates",
            verbose=verbose,
        )

    # Save the config to startup-config
    if cfg_status:
        cfg_status = save_config_cli(
            nr=nr,
            name="Netmiko save running-config to startup-config",
            verbose=verbose,
        )

    return cfg_status
