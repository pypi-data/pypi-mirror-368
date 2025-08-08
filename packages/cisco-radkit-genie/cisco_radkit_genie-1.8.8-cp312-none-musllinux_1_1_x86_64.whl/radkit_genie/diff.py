# This file is part of RADKit / Lazy Maestro <radkit@cisco.com>
# Copyright (c) 2018-2025 by Cisco Systems, Inc.
# All rights reserved.

from __future__ import annotations

import itertools
from typing import Any

from genie.conf.base.utils import QDict  # type:ignore[import-untyped]
from genie.utils.diff import Diff  # type:ignore[import-untyped]

from .exceptions import RADKitGenieException
from .parse import GenieResult


class DiffResult(list[dict[str, str]]):
    def __str__(self) -> str:
        result: list[str] = []
        for item in self:
            if str(item.get("result", "")):
                result.append(f"--- {item.get('a')} {item.get('cmd')}\n")
                result.append(f"+++ {item.get('b')} {item.get('cmd')}\n")
                result.append(f"{str(item.get('result'))}\n")
        return "".join(result)


def _verify_diff_args(
    result_a: QDict | dict[Any, Any], result_b: QDict | dict[Any, Any] | None = None
) -> None:
    if result_b:
        if not (isinstance(result_a, dict) and isinstance(result_a, dict)):
            raise TypeError(
                f"Expected dictionaries as arguments (got {type(result_a)}, {type(result_b)})"
            )
        if not (len(result_a) == 1 and len(result_b) == 1):
            raise RADKitGenieException(
                "Expect two parse/learn object from a single device only"
            )
        if len(list(*result_a.values())) != len(list(*result_b.values())):
            raise RADKitGenieException(
                "parse/learn results have different number of commands/models parsed/learned"
            )
    else:
        if not isinstance(result_a, dict):
            raise TypeError(f"Expected dictionary as arguments (got {type(result_a)})")
        if len(result_a) < 2:
            raise RADKitGenieException(
                "Expect results from multiple devices in result_a when result_b is None"
            )


def _verify_snapshot_args(result_a: dict[Any, Any], result_b: dict[Any, Any]) -> None:
    if not (isinstance(result_a, dict) and isinstance(result_a, dict)):
        raise TypeError(
            f"Expected dictionaries as arguments (got {type(result_a)}, {type(result_b)})"
        )
    if sorted(result_a.keys()) != sorted(result_b.keys()):
        raise RADKitGenieException(
            "cannot compare snapshots taken from different set of devices"
        )


def diff_snapshots(
    result_a: GenieResult | QDict,
    result_b: GenieResult | QDict,
    exclude: list[str] | None = None,
    exclude_add: list[str] | None = None,
) -> DiffResult:
    """
    .. USERFACING

    This function compares **two sets of results** from :func:`parse() <radkit_genie.parse>` or
    :func:`learn() <radkit_genie.learn>` **collected on the same set of devices and for the same
    commands/models**, and outputs the differences between the parsed command output
    or the learned model output.

    Unlike :func:`diff() <radkit_genie.diff>`, which compares command or model data across
    multiple devices, :func:`diff_snapshots() <radkit_genie.diff_snapshots>` is meant to perform
    a before/after comparison of successive snapshots.

    It can compare single commands from a single device, single commands from multiple
    devices or multiple commands from multiple devices. The only constraint is that both
    snapshots need to be collected from exactly the same set of devices and for the same
    commands/models.

    By default, Genie's :func:`parse() <radkit_genie.parse>` and :func:`learn() <radkit_genie.learn>`
    models define a number of attributes which should be excluded from comparison, for example
    running counters, neighbor uptime, etc. which typically change between invocations and are
    not necessarily interesting. The list of those attributes can be manipulated using the
    ``exclude`` or ``exclude_add`` parameters as described below.

    :param result_a: the result of a previous :func:`parse() <radkit_genie.parse>` or
        :func:`learn() <radkit_genie.learn>` call
    :param result_b: the result of a previous :func:`parse() <radkit_genie.parse>` or
        :func:`learn() <radkit_genie.learn>` call, taken from the same set of devices and
        including the same set of commands/models as ``result_a``
    :param exclude: override the list of excluded attributes (see above)
    :param exclude_add: add to Genie's default list of excluded attributes (see above)
    :return: Genie ``DiffResult`` object, can be converted to a unix-style diff output using
        ``str()`` (evaluates to ``False`` if no diffs are found)

    Examples:

        Compare routing state of the same device before and after an event:

        .. code:: python

            before = radkit_genie.learn(service.inventory['router1'], 'routing', os='iosxe')
            # [...]
            after =  radkit_genie.learn(service.inventory['router1'], 'routing', os='iosxe')
            diff = radkit_genie.diff_snapshots(before, after)
            print(str(diff) or 'No change detected')


        Compare multiple commands from the same device:

        .. code:: python

            cmds = ['show ip route', 'show ip cef']
            before = radkit_genie.parse(service.inventory['router1'].exec(cmds).wait(), os='iosxe')
            # [...]
            after =  radkit_genie.parse(service.inventory['router1'].exec(cmds).wait(), os='iosxe')
            diff = radkit_genie.diff_snapshots(before, after)
            print(str(diff) or 'No change detected')

    """
    if isinstance(result_a, GenieResult):
        result_a = result_a.to_dict(add_exclude=True)
    if isinstance(result_b, GenieResult):
        result_b = result_b.to_dict(add_exclude=True)

    try:
        _verify_snapshot_args(result_a, result_b)
    except Exception:
        raise

    results = DiffResult()

    for dev in result_a.keys():
        for cmd, res_a in result_a[dev].items():
            try:
                res_b = result_b[dev][cmd]
            except KeyError:
                raise RADKitGenieException(
                    f'cannot compare different snapshots, command/model "{cmd}" missing in result_b'
                )
            diff_result = diff_dicts(
                res_a, res_b, exclude=exclude, exclude_add=exclude_add
            )
            results.append({"a": dev, "b": dev, "cmd": cmd, "result": diff_result})

    return results


def diff(
    result_a: GenieResult | QDict,
    result_b: GenieResult | QDict | None = None,
    exclude: list[str] | None = None,
    exclude_add: list[str] | None = None,
) -> DiffResult:
    """
    .. USERFACING

    This function compares the results of :func:`parse() <radkit_genie.parse>` or
    :func:`learn() <radkit_genie.learn>` **across multiple devices** and outputs the differences
    between the parsed command output or the learned model output.

    Unlike :func:`diff_snapshots() <radkit_genie.diff_snapshots>`, which performs a before/after
    comparison of successive snapshots taken from the same device(s), :func:`diff() <radkit_genie.diff>`
    compares the same output between two or more devices, for example to compare software versions.

    If you pass a single result object to :func:`diff() <radkit_genie.diff>`, it expects
    command/model output from a set of devices, and compares the output in all combinations.
    This allows us, for example, to compare the routes collected across several devices,
    or a specific feature/command state.

    If you pass two result objects, it assumes you collected the same command(s)/model(s)
    from two different devices and compares them. In this case, each of the result objects
    can only include output from a single device.

    By default, Genie's :func:`parse() <radkit_genie.parse>` and :func:`learn() <radkit_genie.learn>`
    models define a number of attributes which should be excluded from comparison, for example
    running counters, neighbor uptime, etc. which typically change between invocations and are
    not necessarily interesting. The list of those attributes can be manipulated using the
    ``exclude`` or ``exclude_add`` parameters as described below.

    :param result_a: the result of a previous :func:`parse() <radkit_genie.parse>` or
        :func:`learn() <radkit_genie.learn>` call
    :param result_b: the result of a previous :func:`parse() <radkit_genie.parse>` or
        :func:`learn() <radkit_genie.learn>` call (if this parameter is set to ``None`` or is not
        specified at all, ``diff()`` assumes that ``result_a`` contains the command/model results
        from multiple devices and compares those)
    :param exclude: override the list of excluded attributes (see above)
    :param exclude_add: add to Genie's default list of excluded attributes (see above)
    :return: Genie ``DiffResult`` object, can be converted to a unix-style diff output using
        ``str()`` (evaluates to ``False`` if no diffs are found)

    Examples:

        Compare the same command/model from two calls to two devices:

        .. code:: python

            cmds = ['show ip route', 'show ip cef']
            r1_out = radkit_genie.parse(service.inventory['router1'].exec(cmds).wait(), os='iosxe')
            r2_out = radkit_genie.parse(service.inventory['router1'].exec(cmds).wait(), os='iosxe')
            diff = radkit_genie.diff(r1_out, r2_out)

        Compare the same command across more than two devices, ignoring IPv4 addresses
        which are expected to be different. Here we only pass a single argument and
        diff compares the result between each pair of routers:

        .. code:: python

            lo0_state = radkit_genie.parse(service.inventory.filter('name', 'Edge').exec('show interfaces Loopback0')
            diff = radkit_genie.diff(lo0_state, exclude_add=['ipv4'])
            print(str(diff) or 'No change detected')

    """

    def _run_diff(
        device_a: str, device_b: str, result_a: QDict, result_b: QDict
    ) -> DiffResult:
        results = DiffResult()
        for cmd, res_a in result_a[device_a].items():
            try:
                res_b = result_b[device_b][cmd]
            except KeyError:
                raise RADKitGenieException(
                    f"cannot find command/model {cmd} parsed/learned for {device_b}"
                )

            diff_result = diff_dicts(
                res_a, res_b, exclude=exclude, exclude_add=exclude_add
            )
            results.append(
                {"a": device_a, "b": device_b, "cmd": cmd, "result": diff_result}
            )
        return results

    if isinstance(result_a, GenieResult):
        result_a = result_a.to_dict(add_exclude=True)
    if isinstance(result_b, GenieResult):
        result_b = result_b.to_dict(add_exclude=True)

    try:
        _verify_diff_args(result_a, result_b)
    except Exception:
        raise

    results = DiffResult()

    if result_b is not None:
        device_a = list(result_a.keys())[0]
        device_b = list(result_b.keys())[0]

        results += _run_diff(device_a, device_b, result_a, result_b)
    else:
        for device_a, device_b in itertools.combinations(result_a.keys(), 2):
            results += _run_diff(device_a, device_b, result_a, result_a)

    return results


def diff_dicts(
    dict_a: dict[Any, Any],
    dict_b: dict[Any, Any],
    exclude: list[str] | None = None,
    exclude_add: list[str] | None = None,
    verbose: bool | None = None,
    list_order: bool | None = None,
) -> Diff:
    """
    Compares two discrete genie parse/learn results, i.e. the actual genie result dictionaries.
    Return value is a genie Diff object, use str() to convert to a traditional diff output.
    """

    if exclude is None:
        exclude = dict_a.get("_exclude", dict_b.get("_exclude", []))
        assert exclude is not None  # to make mypy happy
    if exclude_add:
        exclude = exclude.copy() + exclude_add

    diff = Diff(dict_a, dict_b, exclude=exclude, verbose=verbose, list_order=list_order)
    diff.findDiff()
    return diff
