#!/usr/bin/env python3
# This file is part of RADKit / Lazy Maestro <radkit@cisco.com>
# Copyright (c) 2018-2025 by Cisco Systems, Inc.
# All rights reserved.

from __future__ import annotations

from contextvars import ContextVar

from pydantic import Field, PositiveInt

from radkit_common.settings import RADKitBaseModel, RADKitSettingsLoader

__all__ = [
    "GenieSettings",
    "GenieSettingsLoader",
    "get_settings",
    "get_settings_loader",
]


class GenieSettings(RADKitBaseModel):
    """
    RADKit Genie settings.
    """

    exec_timeout: PositiveInt = Field(60, description="Exec timeout")
    num_threads: PositiveInt = Field(5, description="Thread num")

    @staticmethod
    def get_env_prefix() -> str:
        return "RADKIT_GENIE_"


class GenieSettingsLoader(RADKitSettingsLoader[GenieSettings]):
    pydantic_type = GenieSettings
    toml_table_header = "genie"
    toml_table_header_visible = True
    settings_context = ContextVar("settings_context", default=None)


def get_settings() -> GenieSettings:
    return get_settings_loader().pydantic_obj


def get_settings_loader() -> GenieSettingsLoader:
    settings_loader = GenieSettingsLoader.from_context()

    if settings_loader is None:
        settings_loader = GenieSettingsLoader()

    return settings_loader
