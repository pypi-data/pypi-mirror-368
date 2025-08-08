# This file is part of RADKit / Lazy Maestro <radkit@cisco.com>
# Copyright (c) 2018-2025 by Cisco Systems, Inc.
# All rights reserved.
# Copyright (c)  Cisco Systems, Inc. - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from .api import api
from .devices import Device
from .diff import diff, diff_dicts, diff_snapshots
from .exceptions import RADKitGenieException, RADKitGenieMissingOS
from .fingerprint import fingerprint
from .learn import learn
from .parse import GenieResultStatus, parse, parse_text

__all__ = [
    "api",
    "parse",
    "parse_text",
    "learn",
    "fingerprint",
    "diff",
    "diff_snapshots",
    "diff_dicts",
    "Device",
    "RADKitGenieException",
    "RADKitGenieMissingOS",
    "GenieResultStatus",
]

from .settings import GenieSettingsLoader
from .version import version_str

__version__ = version_str

GenieSettingsLoader.to_context(GenieSettingsLoader())
