# This file is part of RADKit / Lazy Maestro <radkit@cisco.com>
# Copyright (c) 2018-2025 by Cisco Systems, Inc.
# All rights reserved.

from __future__ import annotations

from typing import Any

from radkit_client.sync.device import Device as RADKitDevice
from radkit_common import nglog

tGENIE = nglog.Tags.GENIE
logger = nglog.getAdapter(__name__, tags=[tGENIE])


def get_ephemeral_attributes(device: RADKitDevice, attr: str) -> str | None:
    """
    Retrieve ephemeral device attribute attr.
    Returns None if no ephemeral attributes are present or if the attr is not found
    """
    try:
        value = str(device.attributes.ephemeral[attr])
    except (AttributeError, KeyError):
        value = None

    return value


def update_ephemeral_attributes(device: RADKitDevice, attrs: dict[str, Any]) -> None:
    """
    Update ephemeral Radkit Device ephmeral attributes with attrs. We are using dict.update() method
    to update the attributes, so existing attributes can also be overwritten.

    :Parameters:
        :param device: (Device) Radkit device object
        :param attrs: (dict) attribute dict
    :Returns:
        :returns: (None type) None
    """
    if not isinstance(attrs, dict):
        raise ValueError("expect a dict-like structure")

    for k, v in attrs.items():
        device.attributes.ephemeral[k] = v
    logger.debug(
        "Updated ephemeral attributes", device_name=device.name, attributes=attrs
    )
