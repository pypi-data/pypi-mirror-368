# This file is part of RADKit / Lazy Maestro <radkit@cisco.com>
# Copyright (c) 2018-2025 by Cisco Systems, Inc.
# All rights reserved.

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextvars import Context, copy_context
from dataclasses import dataclass
from typing import Any

from radkit_client.async_.formatting import (
    SmartMappingPtRepr,
    SmartMappingRepr,
    SmartPtRepr,
    SmartRepr,
)
from radkit_client.sync.device import Device as RADKitDevice
from radkit_client.sync.device import DeviceDict as RADKitDeviceDict
from radkit_common import nglog

from .devices import Device
from .exceptions import RADKitGenieMissingOS
from .parse import GenieResultStatus
from .settings import get_settings

tGENIE = nglog.Tags.GENIE
logger = nglog.getAdapter(__name__, tags=[tGENIE])


@dataclass(repr=False)
class GenieApiSingleResult:
    __repr__ = SmartRepr["GenieApiSingleResult"](
        fields=["api", "status", "status_message", "data"]
    )
    __pt_repr__ = SmartPtRepr["GenieApiSingleResult"](
        fields=["api", "status_message", "data"],
        with_status=True,
    )
    api: str
    data: Any
    status: GenieResultStatus
    status_message: str


class GenieApiResult(dict[str, GenieApiSingleResult]):
    __repr__ = SmartMappingRepr["GenieApiResult"]()
    __pt_repr__ = SmartMappingPtRepr["GenieApiResult"](
        key_name="device",
    )


def _task_api(
    device: RADKitDevice,
    api: str,
    api_args: tuple[Any, ...],
    api_kwargs: dict[str, Any],
    os: str | None = None,
    exec_timeout: int | None = None,
    skip_unknown_os: bool = False,
) -> tuple[str, GenieApiSingleResult]:
    # Returns whatever the underlying Genie API returns.
    try:
        dev = Device(device, os=os, exec_timeout=exec_timeout)
    except RADKitGenieMissingOS:
        if skip_unknown_os:
            logger.info(
                "Skipped device as its OS is not known", device_name=device.name
            )
            return device.name, GenieApiSingleResult(
                api=api,
                data=None,
                status=GenieResultStatus.FAILURE,
                status_message=f"Skipped device {device.name} as its OS is not known",
            )
        else:
            raise RADKitGenieMissingOS(
                f'{device.name} is missing OS information. Please fingerprint() it or specify the os, i.e. api(..., os="iosxe")'
            )

    logger.debug("Executing API", device_name=device.name, api=api)
    try:
        data = getattr(dev.api, api)(*api_args, **api_kwargs)
        result = GenieApiSingleResult(
            api=api,
            data=data,
            status=GenieResultStatus.SUCCESS,
            status_message="api execution successful",
        )
    except Exception as e:
        logger.error(
            "Exception occurred during API execution", device_name=device.name, err=e
        )
        result = GenieApiSingleResult(
            api=api,
            data=None,
            status=GenieResultStatus.FAILURE,
            status_message=f"Executing {device.name}.{api}(...) failed: {e}",
        )

    return device.name, result


def api(
    devices: RADKitDevice | RADKitDeviceDict,
    api: str,
    os: str | None = None,
    exec_timeout: int | None = None,
    skip_unknown_os: bool = False,
    num_threads: int | None = None,
) -> Callable[..., GenieApiResult]:
    """
    .. USERFACING

    This method exposes Genie APIs to execute device/OS specific tasks on one or more RADKit devices.
    Please check https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/apis for supported APIs.

    :param devices: a single RADKit :class:`Device <radkit_client.device.Device>` object or a
        :class:`DeviceDict <radkit_client.device.DeviceDict>` object containing multiple devices
    :param api: the API to execute
    :param os: the genie device OS. If this option is omitted, the OS found by :func:`radkit_genie.fingerprint()` is
        used; else the RADKit Device Type is used. If none of the previous result in a valid genie device OS,
        this parameter is mandatory)
    :param skip_unknown_os: skip parsing output from devices whose OS is not known
        instead of raising an exception (default: ``False``)
    :param exec_timeout: timeout waiting for connection/result (in seconds, default: 60)
    :param num_threads: number of threads (default: 5)
    :return: callable object taking the API parameters as arguments and returning a dict of
        Genie API return values (key: device name, value: ``str`` or ``list[str]``, depending on API)
    :raises: :exc:`RADKitGenieMissingOS` if a device OS is missing

    Examples:
        The method can execute an API on a single device, or multiple devices.

        .. code:: python

            result = radkit_genie.api(
                service.inventory['router1'], 'get_interface_admin_status', os='iosxe'
            )('Vlan1022')
            status = result['router1'].data

            result = radkit_genie.api(
                service.inventory['router1'], 'get_interface_names'
            )()
            names = result['router1'].data

            device = service.inventory['router1']
            radkit_genie.fingerprint(device)
            result = radkit_genie.api(
                service.inventory['router1'], 'get_interface_admin_status'
            )('Vlan1022')
            status = result['router1'].data

            multiple_devices = service.inventory.filter('name', 'Edge')
            radkit_genie.fingerprint(multiple_devices)
            result = radkit_genie.api(
                service.inventory['router1'], 'get_interface_admin_status'
            )('GigabitEthernet0/1/2')
            status = result['router1'].data

    """

    def set_context(passed_context: Context) -> None:
        for var, value in passed_context.items():
            var.set(value)

    def genie_wrapper(*api_args: object, **api_kwargs: object) -> GenieApiResult:
        nonlocal devices
        if isinstance(devices, RADKitDevice):
            # turn into a list so we can iterate
            devices = devices.singleton()

        results = GenieApiResult()
        with ThreadPoolExecutor(
            max_workers=num_threads or get_settings().num_threads,
            initializer=set_context,
            initargs=(copy_context(),),
        ) as executor:
            tasks = []
            for device in devices.values():
                tasks.append(
                    executor.submit(
                        _task_api,
                        device,
                        api,
                        api_args,
                        api_kwargs,
                        os=os,
                        exec_timeout=exec_timeout,
                        skip_unknown_os=skip_unknown_os,
                    )
                )

            for task in as_completed(tasks):
                name, result = task.result()
                results[name] = result

        return results

    return genie_wrapper
