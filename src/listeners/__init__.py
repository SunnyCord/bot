###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from pkgutil import iter_modules

LOAD_EXTENSIONS = [module.name for module in iter_modules(__path__, f"{__package__}.")]
