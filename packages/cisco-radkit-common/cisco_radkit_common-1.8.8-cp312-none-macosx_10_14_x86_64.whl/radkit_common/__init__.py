# This file is part of RADKit / Lazy Maestro <radkit@cisco.com>
# Copyright (c) 2018-2025 by Cisco Systems, Inc.
# All rights reserved.

# isort: skip_file
from __future__ import annotations

import warnings

from cryptography.utils import CryptographyDeprecationWarning

# This has to be the FIRST import from this module
# Add "noqa" to keep flake8 from complaining
from . import licensing  # noqa

# Do not display asyncssh warnings
warnings.filterwarnings(
    action="ignore",
    category=UserWarning,
    message="Blowfish|SEED|CAST5 has been deprecated",
)


# TODO: part of fixing https://gitlab-sjc.cisco.com/lazy_maestro/standalone/-/issues/3872
#  make sure to remove the following import and the `warnings.filterwarnings` call
#  once the issue is resolved.
#  This will help understand if the fix is working as expected.
warnings.filterwarnings(
    action="ignore",
    category=CryptographyDeprecationWarning,
    message="Properties that return a naïve datetime object have been deprecated",
)
