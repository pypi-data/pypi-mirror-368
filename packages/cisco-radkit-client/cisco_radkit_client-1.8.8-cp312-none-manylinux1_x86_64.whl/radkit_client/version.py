# This file is part of RADKit / Lazy Maestro <radkit@cisco.com>
# Copyright (c) 2018-2025 by Cisco Systems, Inc.
# All rights reserved.

from __future__ import annotations

from importlib.metadata import version as get_version

__all__ = ["version_str"]

version_str = get_version("cisco_radkit_client")
