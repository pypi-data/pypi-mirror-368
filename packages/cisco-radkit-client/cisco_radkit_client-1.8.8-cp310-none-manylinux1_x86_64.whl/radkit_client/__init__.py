# This file is part of RADKit / Lazy Maestro <radkit@cisco.com>
# Copyright (c) 2018-2025 by Cisco Systems, Inc.
# All rights reserved.

# isort: skip_file

from __future__ import annotations

# This has to be the FIRST import from this module
# Add "noqa" to keep flake8 from complaining
from . import licensing  # noqa

# For backwards compatibility: expose all sync modules at the top level on
# their old location.
import sys

# Expose the sync API at the top-level.
from .sync import *  # noqa: F403,F401
from .sync import __all__  # noqa: F401

for name in [
    "certs",
    "client",
    "command",
    "context",
    "device",
    "device_flow",
    "exceptions",
    "helpers",
    "http",
    "login",
    "netconf",
    "paths",
    "pipes",
    "port_forwarding",
    "request",
    "service",
    "settings",
    "swagger",
    "terminal",
    "ssh_forwarding",
]:
    sys.modules[f"radkit_client.{name}"] = getattr(
        __import__(f"radkit_client.sync.{name}").sync, name
    )
