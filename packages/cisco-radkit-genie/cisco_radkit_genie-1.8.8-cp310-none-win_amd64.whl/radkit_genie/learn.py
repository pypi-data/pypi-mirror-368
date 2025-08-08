# This file is part of RADKit / Lazy Maestro <radkit@cisco.com>
# Copyright (c) 2018-2025 by Cisco Systems, Inc.
# All rights reserved.

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from contextvars import Context, copy_context

from genie.conf.base.utils import QDict  # type:ignore[import-untyped]
from genie.ops.utils import get_ops_exclude  # type:ignore[import-untyped]

from radkit_client.sync.device import Device as RADKitDevice
from radkit_client.sync.device import DeviceDict as RADKitDeviceDict
from radkit_common import nglog

from .devices import Device
from .exceptions import RADKitGenieMissingOS
from .parse import GenieDeviceResult, GenieResult, GenieResultStatus, GenieSingleResult
from .settings import get_settings

tGENIE = nglog.Tags.GENIE
logger = nglog.getAdapter(__name__, tags=[tGENIE])


def _task_learn(
    device: RADKitDevice,
    models: list[str],
    os: str | None = None,
    exec_timeout: int | None = None,
    skip_unknown_os: bool = False,
) -> tuple[str, QDict]:
    results = GenieDeviceResult()
    try:
        dev = Device(device, os=os, exec_timeout=exec_timeout)
    except RADKitGenieMissingOS:
        if skip_unknown_os:
            logger.info(
                "Skipped device as its OS is not known", device_name=device.name
            )
            for m in models:
                results[m] = GenieSingleResult(
                    data=None,
                    status=GenieResultStatus.FAILURE,
                    status_message=f"unknown OS for device {device.name}",
                )
            return device.name, results
        else:
            raise RADKitGenieMissingOS(
                f'{device.name} is missing OS information. Please fingerprint() it or specify the os, i.e. learn(..., os="iosxe")'
            )

    for model in models:
        logger.debug("Learning model", device_name=device.name, model=model)
        try:
            result = dev.learn(model)
        except Exception as e:
            # Many exceptions can happen here as genie will perform many operatins
            # to gather the data, so can't be sure hence catching all exceptions.
            # Anyway, it is unrecoverable, so we set the status to FAILURE and move on

            logger.error(
                "Exception occurred during learning", device_name=device.name, err=e
            )

            results[model] = GenieSingleResult(
                data=None,
                status=GenieResultStatus.FAILURE,
                status_message=f"Exception occurred during learning: {e}",
            )
            continue

        # Change device object to name, to make it comparable
        result.device = result.device.name

        output = QDict(result.to_dict())

        results[model] = GenieSingleResult(
            data=output,
            status=GenieResultStatus.SUCCESS,
            status_message="learnt successfully",
        )
        # adding exclude keys, useful for the Diff functionality
        try:
            results[model].exclude = get_ops_exclude(model, dev)
        except Exception as e:
            logger.info(
                "Unable to extract genie model exclude information, using empty list",
                model=model,
                err=e,
            )
            results[model].exclude = []

    return device.name, results


def learn(
    devices: RADKitDevice | RADKitDeviceDict,
    models: str | list[str],
    os: str | None = None,
    exec_timeout: int | None = None,
    skip_unknown_os: bool = False,
    num_threads: int | None = None,
) -> GenieResult:
    """
    .. USERFACING

    This function uses Genie's ``learn`` method to parse device features, so-called *models*,
    into structured data. Genie will execute the required commands on the device(s) as it sees fit.
    Please check https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/models for
    a list of supported models.

    ``learn()`` returns a dict of dicts, use  ``result[device][model].data`` to access the result.

    ``learn().to_dict()`` can convert the result to a special dictionary of type ``QDict`` which can also be parsed using Genie's
    `dq method <https://pubhub.devnetcloud.com/media/genie-docs/docs/userguide/utils/index.html#dq>`_.

    :param devices: a single RADKit :class:`Device <radkit_client.device.Device>` object or a
        :class:`DeviceDict <radkit_client.device.DeviceDict>` object containing multiple devices
    :param models: one or more model(s) to learn, as a ``str`` or ``list[str]``
    :param os: the genie device OS. If this option is omitted, the OS found by :func:`radkit_genie.fingerprint()` is
        used; else the RADKit Device Type is used. If none of the previous result in a valid genie device OS,
        this parameter is mandatory)
    :param skip_unknown_os: skip parsing output from devices whose OS is not known
        instead of raising an exception (default: ``False``)
    :param exec_timeout: timeout waiting for connection/result (in seconds, default: 60)
    :param num_threads: number of threads (default: 5)
    :return: ``GenieResult`` structure (dict of dict), use ``result[device][model].data`` to access the learnt data
    :raises: :exc:`RADKitGenieMissingOS <radkit_genie.RADKitGenieMissingOS>` if a device OS is missing

    Examples:

        .. code:: python

            # Learn from a single device, single model, specifying the OS explicitly
            learn_result = radkit_genie.learn(service.inventory['router1'], 'bgp', os='iosxe')
            parsed_result = learn_result['router1']['bgp'].data

            # Learn from a single device, single/multiple models, using OS fingerprinting
            device = service.inventory['router1']
            radkit_genie.fingerprint(device)
            single_result = radkit_genie.learn(device, 'bgp').to_dict()
            multi_result = radkit_genie.learn(device, ['bgp', 'platform']).to_dict()

            # Learn from multiple devices, single model, levering RADkit device type
            multiple_devices = service.inventory.filter('name', 'Edge')
            learn_result = radkit_genie.parse(multiple_devices, 'routing').to_dict()

    """

    def set_context(passed_context: Context) -> None:
        for var, value in passed_context.items():
            var.set(value)

    if isinstance(devices, RADKitDevice):
        # turn into a list so we can iterate
        devices = devices.singleton()

    if isinstance(models, str):
        models = [models]

    results = GenieResult()
    with ThreadPoolExecutor(
        max_workers=num_threads or get_settings().num_threads,
        initializer=set_context,
        initargs=(copy_context(),),
    ) as executor:
        tasks = []
        for device in devices.values():
            tasks.append(
                executor.submit(
                    _task_learn,
                    device,
                    models,
                    os,
                    exec_timeout,
                    skip_unknown_os,
                )
            )

        for task in as_completed(tasks):
            name, result = task.result()
            results[name] = result

    return results
