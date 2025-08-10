#!/usr/bin/env python3
"""
LERO - LeRobot dataset Operations toolkit

A comprehensive toolkit for editing and managing LeRobot datasets for robot imitation learning.
LERO (LeRobot dataset Operations toolkit) provides powerful tools for LeRobot dataset editing.

This package provides functionality for:
- Loading and editing LeRobot datasets
- Episode management (delete, copy, modify)
- GUI interface for visual dataset browsing
- Batch operations and automation

Licensed under the Apache License 2.0
"""

__version__ = "0.3.0"

from .dataset_editor.core import LeRobotDatasetEditor

# Conditionally import GUI module
try:
    from . import gui
    __all__ = ["LeRobotDatasetEditor", "gui"]
except ImportError:
    # GUI dependencies not available
    __all__ = ["LeRobotDatasetEditor"]