# This file is part of RADKit / Lazy Maestro <radkit@cisco.com>
# Copyright (c) 2018-2025 by Cisco Systems, Inc.
# All rights reserved.

# isort: skip_file
from __future__ import annotations

import asyncio
import sys

# On Windows set WindowsSelectorEventLoopPolicy
# (affects Python >=3.8)
# Credits go to: https://github.com/encode/httpx/issues/914#issuecomment-622586610
# Related Python bug: https://bugs.python.org/issue39232
# Related issue: #2030
# Related httpx issue: https://github.com/encode/httpx/issues/914
# Since Python 3.8 default event loop on Windows is ProactorEventLoop
# which causes trouble when using asyncio.run(), httpx, aiohttp and maybe other
# libraries.
# Set it back again to SelectorEventLoop.
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# This has to be the FIRST import from this module
# Add "noqa" to keep flake8 from complaining
from . import licensing  # noqa

import warnings

# Do not display asyncssh warnings
warnings.filterwarnings(
    action="ignore",
    category=UserWarning,
    message="Blowfish|SEED|CAST5 has been deprecated",
)
