# This file is part of RADKit / Lazy Maestro <radkit@cisco.com>
# Copyright (c) 2018-2025 by Cisco Systems, Inc.
# All rights reserved.

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from contextvars import Context, copy_context

from unicon import Connection  # type:ignore[import-untyped]
from unicon.plugins.generic.settings import (  # type:ignore[import-untyped]
    GenericSettings,
)
from unicon.utils import learn_os_platform  # type:ignore[import-untyped]

from radkit_client.sync.device import Device as RADKitDevice
from radkit_client.sync.device import DeviceDict as RADKitDeviceDict
from radkit_common import nglog

from .settings import get_settings
from .utils import update_ephemeral_attributes

tGENIE = nglog.Tags.GENIE
logger = nglog.getAdapter(__name__, tags=[tGENIE])


OS_MAPPING = {
    "nxos": {
        "os": ["Nexus Operating System"],
        "platform": {
            "aci": ["(?i)aci"],
            "mds": ["(?i)mds"],
            "n5k": ["(?i)n5k"],
            "n9k": ["(?i)n9k"],
            "nxosv": ["(?i)nxosv"],
        },
    },
    "iosxe": {
        "os": ["IOS( |-)XE Software"],
        "platform": {
            "cat3k": ["(?i)cat3k"],
            "cat9k": ["(?i)cat9k"],
            "cat9800": ["(?i)c(at)?9800"],
            "csr1000v": ["(?i)csr1000v"],
            "sdwan": ["(?i)sdwan"],
            "nxosv": ["(?i)nxosv"],
        },
    },
    "iosxr": {
        "os": ["IOS XR Software"],
        "platform": {
            "asr9k": ["(?i)asr9k"],
            "iosxrv": ["i(?i)osxrv"],
            "iosxrv9k": ["(?i)iosxrv9k"],
            "moonshine": ["(?i)moonshine"],
            "ncs5k": ["(?i)ncs5k"],
            "spitfire": ["(?i)spitfire"],
        },
    },
    "ios": {
        "os": ["IOS Software"],
        "platform": {
            "ap": ["TBD"],
            "iol": ["TBD"],
            "iosv": ["TBD"],
            "pagent": ["TBD"],
        },
    },
    "junos": {
        "os": ["JUNOS Software"],
        "platform": {
            "vsrx": ["vsrx"],
        },
    },
    "linux": {
        "os": ["Linux"],
    },
    "aireos": {
        "os": ["aireos"],
    },
    "cheetah": {
        "os": ["cheetah"],
    },
    "ise": {
        "os": ["ise"],
    },
    "asa": {
        "os": ["asa"],
    },
    "nso": {
        "os": ["nso"],
    },
    "confd": {
        "os": ["confd"],
    },
    "vos": {
        "os": ["vos"],
    },
    "cimc": {
        "os": ["cimc"],
    },
    "fxos": {
        "os": ["fxos"],
    },
    "staros": {
        "os": ["staros"],
    },
    "aci": {
        "os": ["aci"],
    },
    "sdwan": {
        "os": ["sdwan"],
    },
    "sros": {
        "os": ["sros"],
    },
    "apic": {
        "os": ["apic"],
    },
    "windows": {
        "os": ["windows"],
    },
}


def _learn_os(
    device: RADKitDevice, exec_timeout: int | None = None
) -> tuple[str, str, str]:
    # need the connection attrtibute for genie's learn_os_platform
    con = Connection(
        hostname=device.name,
        start=[],
        settings=GenericSettings(),
        log_buffer=True,
        log_stdout=False,
    )  # log_buffer=True disables file logging

    learned_os = learned_platform = error = ""
    for command in con.settings.LEARN_OS_COMMANDS:
        try:
            # fetch command
            timeout = exec_timeout or get_settings().exec_timeout
            response = device.exec(command, timeout=timeout).wait()
            assert response.result is not None
            output = response.result.data
        except Exception as e:
            logger.warning(
                "Error executing command",
                command=command,
                device_name=device.name,
                err=e,
            )
            error = str(e)
            continue
        learned_os, learned_platform = learn_os_platform(con, output, OS_MAPPING)
        if learned_os:
            error = ""
            break
    return learned_os, learned_platform, error


def _task_fingerprint(
    device: RADKitDevice, exec_timeout: int | None, update_device_attributes: bool
) -> tuple[str, dict[str, str]] | tuple[str, dict[str, None]] | tuple[str, None]:
    learned_os, learned_platform, error = _learn_os(device, exec_timeout=exec_timeout)
    if learned_os:
        result = {"os": learned_os}
        if learned_platform:
            result["platform"] = learned_platform
        if update_device_attributes:
            update_ephemeral_attributes(device, result)
        # mypy ignore can go once https://gitlab-sjc.cisco.com/lazy_maestro/standalone/issues/1944 is fixed
        logger.info("learnt OS", device_name=device.name, fields=result)
        return device.name, result
    elif error:
        logger.warning("Error learning OS", device_name=device.name)
        return device.name, None
    else:
        logger.warning("Unknown OS on device", device_name=device.name)
        return device.name, {"os": None}


def fingerprint(
    devices: RADKitDevice | RADKitDeviceDict,
    update_device_attributes: bool = True,
    exec_timeout: int | None = None,
    num_threads: int | None = None,
) -> dict[str, dict[str, str] | dict[str, None] | None]:
    """
    .. USERFACING

    Genie needs to know the operating system (OS) of the devices it interacts with,
    i.e. ``iosxe``, ``iosxr``, ``linux``, etc.
    Please refer to https://pubhub.devnetcloud.com/media/unicon/docs/user_guide/supported_platforms.html#supported-platforms
    for the list of supported OSes.

    The :func:`parse() <radkit_genie.parse>` and :func:`learn() <radkit_genie.learn>`
    functions accept the OS as an optional argument, but we also expose a method
    which attempts to learn the device's OS and stores it in the Client's local device metadata
    (this ephemeral data is only kept during the course of the session/script).
    Once the OS fingerprinting results are available, those will be leveraged automatically.

    :param devices: a single RADKit :class:`Device <radkit_client.device.Device>` object or a
        :class:`DeviceDict <radkit_client.device.DeviceDict>` object containing multiple devices
    :param update_device_attributes: update OS/platform in local RADKit device inventory (default: ``True``)
    :param exec_timeout: timeout waiting for connection/result (in seconds, default: 60)
    :param num_threads: number of threads (default: 5)
    :returns: a ``dict`` with the result of the fingerprinting attempt for each device
        (the value is set to ``None`` if the OS cannot be determined), e.g.
        ``{"C9k-u-4": {"os": "iosxe", "platform": "cat9k"}}``

    Examples:

        .. code:: python

            # Fingerprint a single device
            radkit_genie.fingerprint(service.inventory['router1'])
            # Fingerprint the entire inventory
            radkit_genie.fingerprint(service.inventory)

    """  # noqa: W291

    def set_context(passed_context: Context) -> None:
        for var, value in passed_context.items():
            var.set(value)

    if isinstance(devices, RADKitDevice):
        # turn into a list so we can iterate
        devices = devices.singleton()

    results = {}
    with ThreadPoolExecutor(
        max_workers=num_threads or get_settings().num_threads,
        initializer=set_context,
        initargs=(copy_context(),),
    ) as executor:
        tasks = []
        for name, device in devices.items():
            tasks.append(
                executor.submit(
                    _task_fingerprint, device, exec_timeout, update_device_attributes
                )
            )

        for task in as_completed(tasks):
            name, result = task.result()
            results[name] = result

    return results
