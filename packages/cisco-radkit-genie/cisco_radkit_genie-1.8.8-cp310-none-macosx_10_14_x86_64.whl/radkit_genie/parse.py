# This file is part of RADKit / Lazy Maestro <radkit@cisco.com>
# Copyright (c) 2018-2025 by Cisco Systems, Inc.
# All rights reserved.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from genie.conf.base.utils import QDict  # type:ignore[import-untyped]
from genie.libs.conf.device import Device as GenieDevice  # type:ignore[import-untyped]
from genie.libs.parser.utils import get_parser_exclude  # type:ignore[import-untyped]
from genie.libs.parser.utils.common import ParserNotFound  # type:ignore[import-untyped]

from radkit_client.async_.formatting import (
    SmartMappingPtRepr,
    SmartMappingRepr,
    SmartPtRepr,
    SmartRepr,
)
from radkit_client.sync.exceptions import ClientError
from radkit_client.sync.exec import ExecResponse_ByDevice_ByCommand, ExecResponseBase
from radkit_common import nglog
from radkit_genie.devices import Device
from radkit_genie.exceptions import RADKitGenieException, RADKitGenieMissingOS


class GenieResultStatus(Enum):
    FAILURE = "FAILURE"
    SUCCESS = "SUCCESS"


@dataclass(repr=False)
class GenieSingleResult:
    # don't display result "data" as it's typically far too long to be displayed on screen
    __repr__ = SmartRepr["GenieSingleResult"](fields=["status", "status_message"])
    __pt_repr__ = SmartPtRepr["GenieSingleResult"](
        fields=["status_message", "data"],
        with_status=True,
    )
    data: QDict | None
    status: GenieResultStatus
    status_message: str
    exclude: list[str] | None = None


class GenieDeviceResult(dict[str, GenieSingleResult]):
    __repr__ = SmartMappingRepr["GenieDeviceResult"]()
    __pt_repr__ = SmartMappingPtRepr["GenieDeviceResult"](
        key_name="command",
    )

    @property
    def success_count(self) -> int:
        count = 0
        for single_result in self.values():
            if single_result.status == GenieResultStatus.SUCCESS:
                count += 1
        return count

    @property
    def fail_count(self) -> int:
        return len(self) - self.success_count


class GenieResult(dict[str, GenieDeviceResult]):
    __repr__ = SmartMappingRepr["GenieResult"]()
    __pt_repr__ = SmartMappingPtRepr["GenieResult"](
        fields=["commands", "success_count", "fail_count"],
        getters={
            "commands": lambda obj: list(obj),
        },
    )

    def to_dict(self, add_exclude: bool = False) -> QDict:
        """
        convert GenieResult to a dict (actually: QDict()) to allow for easier parsing

        :param add_exclude: Add information about excluded keys which genie diff would exclude
            when comparing two results (default: False)
        """
        result: dict[str, Any] = {}
        for dev, res in self.items():
            for cmd, output in res.items():
                if output.data is not None:
                    result.setdefault(dev, {})[cmd] = output.data.copy()
                    if add_exclude and output.exclude:
                        result[dev][cmd]["_exclude"] = output.exclude
                else:
                    result.setdefault(dev, {})[cmd] = None

        return QDict(result)


tGENIE = nglog.Tags.GENIE
logger = nglog.getAdapter(__name__, tags=[tGENIE])


def parse(
    radkitrequest: ExecResponseBase[Any],
    parser: str | None = None,
    os: str | None = None,
    skip_unknown_os: bool = False,
) -> GenieResult:
    """
    .. USERFACING

    This function uses Genie parsers to parse command output returned
    by RADKit Client's :meth:`Device.exec() <radkit_client.device.Device.exec>`
    call into structured data.

    Please check https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/parsers
    for supported parsers. Genie tries to search for the relevant parser based on the
    command executed (using fuzzy search); if the search fails, you can provide the parser
    and the OS manually.

    ``parse(...).to_dict()`` converts the result into a special dictionary of type ``QDict`` which can
    also be parsed using Genie's `dq method <https://pubhub.devnetcloud.com/media/genie-docs/docs/userguide/utils/index.html#dq>`_.

    :param radkitrequest: return value of RADKit Client's :meth:`Device.exec() <radkit_client.device.Device.exec>` call
    :param parser: parser to choose (if omitted, the parser is derived from the command issued)
    :param os: the genie device OS. If this option is omitted, the OS found by :func:`radkit_genie.fingerprint()` is
        used; else the RADKit Device Type is used. If none of the previous result in a valid genie device OS,
        this parameter is mandatory)
    :param skip_unknown_os: skip parsing output from devices whose OS is not known
        instead of raising an exception (default: ``False``)
    :return: ``GenieResult`` structure (dict of dict), use ``result[device][cmd].data`` to access the parsed data
    :raises: :exc:`RADKitGenieMissingOS <radkit_genie.RADKitGenieMissingOS>` if a device OS is missing

    Examples:

        .. code:: python

            # Parse the output from a single device and a single command, specifying the OS explicitly
            single_response = service.inventory['devicename'].exec('show ip route').wait()
            result = radkit_genie.parse(single_response, os='iosxe')
            parsed_data = result['devicename']['show ip route'].data

            # Parse the output from multiple devices and multiple commands, leveraging RADkit device type
            # to genie OS mapping
            multi_response = service.inventory.filter('name', 'Edge').exec(['show ip route', 'show version']).wait()
            result = radkit_genie.parse(multi_response)
            for device in result.keys():
                parsed_routes = result[device]['show ip route'].data
                parsed_version = result[device]['show version'].data

            # turn result into a Genie QDict for easy dict parsing
            response = service.inventory.filter('name', 'Edge').exec('show ip route').wait()
            qdict = radkit_genie.parse(response).to_dict()
            paths = qdict.q.contains('1.1.1.1)

    """
    radkitresults = radkitrequest.by_device_by_command

    # use str(r.status) to address the various *ExecResultStatus enum types
    if any("PROCESSING" in str(r.status) for r in radkitresults.values()):
        raise RADKitGenieException(
            "Error, cannot parse requests which are still being processed"
        )

    if parser:
        if (
            isinstance(radkitresults, ExecResponse_ByDevice_ByCommand)
            and len(radkitresults) > 0
            and len(radkitresults[next(iter(radkitresults.keys()))]) > 1
        ):
            raise ValueError(
                "parser hint option only supported with single-command responses"
            )
        else:
            logger.debug("Using genie parser", parser=parser)

    results = GenieResult()

    for device, commands in radkitresults.items():
        results[device] = GenieDeviceResult()
        dev = None

        commands_items = list(commands.items())

        for cmd, radkitresult in commands_items:
            if dev is None:
                radkitdevice = radkitresult.device

                # create genie device object, needed for os/abstraction information
                try:
                    dev = Device(radkitdevice, os=os)
                except RADKitGenieMissingOS:
                    if skip_unknown_os:
                        logger.info(
                            "Skipped device as its OS is unknown", device_name=device
                        )
                        for c, _ in commands_items:
                            results[device][c] = GenieSingleResult(
                                data=None,
                                status=GenieResultStatus.FAILURE,
                                status_message=f"unknown OS for device {device}",
                            )
                        break
                    else:
                        raise RADKitGenieMissingOS(
                            f'{device} is missing OS information. Please fingerprint() it or specify the os, i.e. parse(..., os="iosxe")'
                        )

            try:
                # access to result.data fails for unsuccessful RADKit requests, will
                # be caught as ClientError below
                output = radkitresult.data
                if output is None:
                    raise ClientError

                # as we are parsing an already executed command's output,
                # we need to provide the correct parser to genie
                # we allow the user to provide a parser in case genie lookup fails
                _parser = parser or cmd

                logger.debug(
                    "Start genie parse", device_name=device, command=cmd, parser=_parser
                )

                parse_result = dev.parse(_parser, output=output)

                results[device][cmd] = GenieSingleResult(
                    data=parse_result,
                    status=GenieResultStatus.SUCCESS,
                    status_message="parsed successfully",
                )
                # adding exclude keys, useful for the Diff functionality
                try:
                    results[device][cmd].exclude = get_parser_exclude(_parser, dev)
                except (AttributeError, LookupError, ParserNotFound, ValueError):
                    results[device][cmd].exclude = []
                except Exception as e:
                    # expecting the exception to be one of(AttributeError, LookupError, PareserNotFound, ValueError),
                    # but it is hard to be sure, so we catch all exceptions.
                    # Anyway, it is unrecoverable, so we log it and move on

                    logger.error(
                        "Unable to extract genie parser exclude information, using empty list",
                        command=cmd,
                        err=e,
                    )
                    results[device][cmd].exclude = []

            except ClientError:
                if radkitresult.status_message:
                    errmsg = radkitresult.status_message
                else:
                    errmsg = f"Error, status code {radkitresult.status}"
                logger.info(
                    "Cannot parse command",
                    command=cmd,
                    device_name=device,
                    err=errmsg,
                )
                results[device][cmd] = GenieSingleResult(
                    data=None,
                    status=GenieResultStatus.FAILURE,
                    status_message=errmsg,
                )

            except Exception as e:
                logger.error("Genie exception", command=cmd, device_name=device, err=e)
                results[device][cmd] = GenieSingleResult(
                    data=None, status=GenieResultStatus.FAILURE, status_message=str(e)
                )

    return results


def parse_text(
    text: str,
    parser: str,
    os: str,
) -> QDict:
    """
    .. USERFACING

    While radkit_genie's :func:`parse() <radkit_genie.parse>` function is most commonly invoked
    when dealing with parsing the output of the RADKit :meth:`Device.exec() <radkit_client.sync.device.Device.exec()>` call,
    we also provide a convenience function to invoke Genie's parsers on raw text output, for example collected
    as part of RADKit's exec-sequence.

    This method expects the output of a single command, the parser to be used (i.e. the command executed) and the
    device's operating system (os).

    Please check https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/parsers
    for supported parsers.

    :param text: the text output of a single command
    :param parser: parser to choose (typically the command executed)
    :param os: the genie device OS (mandatory)
    :return: ``dict`` structure as returned by Genie's parse method

    Examples:

        .. code:: python

            # Parse the output from a device output
            parsed_result = radkit_genie.parse_text(output, "show version", "iosxe")
            version = parsed_result["version"]["xe_version"]
            serial = parsed_result["version"]["chassis_sn"]

    """

    if not isinstance(text, str):
        raise TypeError("Please pass plain text output as input to this function")

    geniedevice = GenieDevice("dummy", os=os, custom={"abstraction": {"order": ["os"]}})
    parsed_output = geniedevice.parse(parser, output=text)
    return parsed_output
