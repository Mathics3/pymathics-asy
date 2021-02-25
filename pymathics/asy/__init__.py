# -*- coding: utf-8 -*-
"""
Pymathics asymptote graphics handler.

This module provides a replacement for the graphics subsystem using asymptote to draw and export graphics.

"""

import os
from pymathics.asygraphics.version import __version__
from pymathics.asygraphics.__main__ import Hello # noqa
from pymathics.asy.exportasy import (ExportToJPG,
                                     ExportToPNG,
                                     ExportToSVG,
                                     ExportToPDF)
__all__ = ("__version__", "ExportToJPG", "ExportToPNG", "ExportToSVG", "ExportToPDF", "pymathics_version_data")

# To be recognized as an external mathics module, the following variable
# is required:
#
pymathics_version_data = {
    "author": "The Mathics Team",
    "version": __version__,
    "requires": [],
}
