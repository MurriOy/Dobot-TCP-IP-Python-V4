# Copyright (c) 2026 Dobot
# Licensed under the MIT License

"""
Dobot SDK V4 - Dobot Robot Python SDK

Supported models: CRA, E6, CRAF, NovaLite and other V4 series robots
"""

from .version import __version__
from .api.robot import DobotRobot
from .api.motion import CoordinateType
from .core.logger import get_logger, set_log_level, get_log_directory

__all__ = [
    "DobotRobot",
    "CoordinateType",
    "__version__",
    "get_logger",
    "set_log_level",
    "get_log_directory",
]
