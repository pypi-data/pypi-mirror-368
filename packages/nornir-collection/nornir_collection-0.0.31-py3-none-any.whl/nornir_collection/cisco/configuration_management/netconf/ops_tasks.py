#!/usr/bin/env python3
"""
This module contains the Nornir NETCONF operation RPC tasks lock, validate, discard, commit and unlock.
NETCONF RPC tasks like get-config or edit-config are not part of this module. Please take a look to
the module config_tasks for these tasks.

The functions are ordered as followed:
- Nornir NETCONF tasks
- Nornir NETCONF tasks in regular function
"""

import traceback
from typing import Literal
from nornir.core import Nornir
from nornir.core.task import Task, Result
from nornir_collection.utils import print_result


#### Nornir NETCONF Tasks ###################################################################################


def nc_ops_rpc(
    task: Task,
    rpc: Literal["lock", "validate", "discard", "commit", "unlock"],
    datastore: Literal["candidate", "running"] = "candidate",
    confirm: bool = False,
    confirm_timeout: int = 300,
    verbose: bool = False,
) -> Result:
    """
    This function is a Nornir Task using Scrapli to run a NETCONF RPC operation. The `rpc` argument
    specifies the NETCONF operation to perform. The `datastore` argument specifies the NETCONF datastore
    to perform the operation on. The `confirm` argument specifies if the commit operation should be
    confirm. The `confirm_timeout` argument sets the timeout period for the commit-confirm operation.
    The `verbose` argument sets the verbosity level of the result output.
    """
    # Track if the overall task has failed
    failed = False

    # Verify that the rpc argument is valid
    if rpc not in ("lock", "validate", "discard", "commit", "unlock"):
        result = (
            f"'{task.name}' -> NetconfResponse <Success: False>\n"
            + f"-> ValueError: '{rpc}' is not a supported NETCONF RPC"
        )
        return Result(host=task.host, result=result, changed=False, failed=True)

    # Get the Scrapli Netconf connection manually
    scrapli_conn = task.host.get_connection("scrapli_netconf", task.nornir.config)
    scrapli_conn.open()

    try:
        if rpc == "lock":
            nc_result = scrapli_conn.lock(target=datastore)
        elif rpc == "unlock":
            nc_result = scrapli_conn.unlock(target=datastore)
        elif rpc == "validate":
            nc_result = scrapli_conn.validate(source=datastore)
        elif rpc == "discard":
            nc_result = scrapli_conn.discard()
        elif rpc == "commit":
            if confirm:
                # Set a "bare" NETCONF commit-confirm string
                filter_commit_confirm = (
                    "<commit>\n"
                    "  <confirmed/>\n"
                    f"  <confirm-timeout>{confirm_timeout}</confirm-timeout>\n"
                    "</commit>"
                )
                nc_result = scrapli_conn.rpc(filter_=filter_commit_confirm)

            else:
                nc_result = scrapli_conn.commit()

    except Exception:
        result = (
            f"'{task.name}' -> NetconfResponse <Success: False>\n"
            + "-> Configuration attempt failed\n"
            + f"\n{traceback.format_exc()}"
        )
        return Result(host=task.host, result=result, changed=False, failed=True)

    # No Exception -> Continue to return the result
    ########################################### WORKAROUND ##################################################
    ### It seems that since 17.12.4 the NETCONF server implementation has a bug !                         ###
    ### If the database is locked by 'yang_mgmt_infra' or 'system system', the NETCONF rpc reply failed   ###
    ### The rpc reply contains one of the following errors:                                               ###
    ### - the configuration database is locked by session 20 yang_mgmt_infra tcp (system from 127.0.0.1)  ###
    ### - the configuration database is locked by session 238 system system (system from 0.0.0.0)         ###
    ### -> So we don't set the task as failed if this error occurs, as the configuration is still applied ###
    #########################################################################################################
    # Exclude the 'yang_mgmt_infra' and 'system system' locked database error
    if "database is locked by" in str(nc_result.result):
        if any(x in str(nc_result.result) for x in ["yang_mgmt_infra", "system system"]):
            pass
        else:
            failed = True
    # Else if the result XML payload dont't contain '<ok/>', the NETCONF rpc reply failed
    elif "<ok/>" not in str(nc_result.result):
        failed = True

    # Set the task result
    result = f"'{task.name}' -> {str(nc_result)}"
    # Add more details to the task result
    if rpc == "commit" and confirm and not failed:
        result += f"\n-> NETCONF commit-confirm timeout period is set to {confirm_timeout}s"
    if failed or verbose:
        if confirm:
            result += f"\n\n{filter_commit_confirm}"
        result += f"\n\n{nc_result.result}"

    # Set changed for the Nornir print result
    changed = not failed

    return Result(host=task.host, result=result, changed=changed, failed=failed)


#### Nornir NETCONF Tasks in regular Function ###############################################################


def nc_lock(
    nr: Nornir,
    datastore: Literal["candidate", "running"] = "candidate",
    cfg_status: bool = True,
    verbose: bool = False,
) -> bool:
    """
    This function uses Nornir to run a NETCONF lock operation on the specified datastore using Scrapli.
    If the `cfg_status` argument is set to False, the function will immediately return False without
    performing any operations, in order to skip the NETCONF lock operation.
    """

    # Return False if cfg_status argument is False
    if not cfg_status:
        return False

    # Lock the NETCONF datastore with Scrapli netconf_lock
    nc_result = nr.run(
        name="NETCONF lock datastore",
        task=nc_ops_rpc,
        rpc="lock",
        datastore=datastore,
        verbose=verbose,
        on_failed=True,
    )

    # Print the result
    print_result(result=nc_result)

    # If the task failed -> nc_result.failed is True. So return False if nc_result.failed is True
    if nc_result.failed:
        cfg_status = False

    return cfg_status


def nc_validate(
    nr: Nornir,
    datastore: Literal["candidate", "running"] = "candidate",
    cfg_status: bool = True,
    verbose: bool = False,
) -> bool:
    """
    This function uses Nornir to run a NETCONF validate operation on the specified datastore using Scrapli.
    If the `cfg_status` argument is set to False, the function will immediately return False without
    performing any operations, in order to skip the NETCONF validate operation.
    """

    # Return False if cfg_status argument is False
    if not cfg_status:
        return False

    # Lock the NETCONF datastore with Scrapli netconf_validate
    nc_result = nr.run(
        name="NETCONF validate datastore",
        task=nc_ops_rpc,
        rpc="validate",
        datastore=datastore,
        verbose=verbose,
        on_failed=True,
    )

    # Print the result
    print_result(result=nc_result)

    # If the task failed -> nc_result.failed is True. So return False if nc_result.failed is True
    if nc_result.failed:
        cfg_status = False

    return cfg_status


def nc_commit(
    nr: Nornir,
    confirm: bool = False,
    confirm_timeout: int = 300,
    cfg_status: bool = True,
    verbose: bool = False,
) -> bool:
    """
    This function uses Nornir to run a NETCONF commit operation using Scrapli. Optionally, the function
    can perform a commit-confirm operation by setting the `confirm` argument to True. The
    `confirm_timeout` argument sets the timeout period for the commit-confirm operation. If the
    `cfg_status` argument is set to False, the function will immediately return False without performing
    any operations, in order to skip the NETCONF commit operation.
    """

    # Return False if cfg_status argument is False
    if not cfg_status:
        return False

    # Set the task name
    if confirm:
        task_name = "NETCONF commit-confirm datastore"
    else:
        task_name = "NETCONF commit datastore"

    # Lock the NETCONF datastore with Scrapli netconf_commit
    nc_result = nr.run(
        name=task_name,
        task=nc_ops_rpc,
        rpc="commit",
        confirm=confirm,
        confirm_timeout=confirm_timeout,
        verbose=verbose,
        on_failed=True,
    )

    # Print the result
    print_result(result=nc_result)

    # If the task failed -> nc_result.failed is True. So return False if nc_result.failed is True
    if nc_result.failed:
        cfg_status = False

    return cfg_status


def nc_unlock(
    nr: Nornir,
    datastore: Literal["candidate", "running"] = "candidate",
    cfg_status: bool = True,
    verbose: bool = False,
) -> bool:
    """
    This function uses Nornir to run a NETCONF unlock operation on the specified datastore using Scrapli.
    If the `cfg_status` argument is set to False, the function will immediately return False without
    performing any operations, in order to skip the NETCONF unlock operation.
    """

    # Return False if cfg_status argument is False
    if not cfg_status:
        return False

    # Lock the NETCONF datastore with Scrapli netconf_unlock
    nc_result = nr.run(
        name="NETCONF unlock datastore",
        task=nc_ops_rpc,
        rpc="unlock",
        datastore=datastore,
        verbose=verbose,
        on_failed=True,
    )

    # Print the result
    print_result(result=nc_result)

    # If the task failed -> nc_result.failed is True. So return False if nc_result.failed is True
    if nc_result.failed:
        cfg_status = False

    return cfg_status


def nc_discard(nr: Nornir, cfg_status: bool = False, verbose: bool = False) -> bool:
    """
    This function uses Nornir to run a NETCONF discard operation using Scrapli. If the `cfg_status`
    argument is set to True, the function will immediately return True without performing any operations,
    as no NETCONF discard is needed.
    """

    # Return True if cfg_status argument is True
    if cfg_status:
        return True

    # Lock the NETCONF datastore with Scrapli netconf_discard
    nc_result = nr.run(
        name="NETCONF discard datastore",
        task=nc_ops_rpc,
        rpc="discard",
        verbose=verbose,
        on_failed=True,
    )

    # Print the result
    print_result(result=nc_result)

    # If the task failed -> nc_result.failed is True. So return False if nc_result.failed is True
    if nc_result.failed:
        cfg_status = False

    return cfg_status
