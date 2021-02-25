# -*- coding: utf-8 -*-
"""
Pymathics asymptote graphics handler.

This module provides a replacement for the graphics subsystem using asymptote to draw and export graphics.

"""

import os
import os.path as osp

print(osp.dirname(__file__))
for d in os.walk(osp.dirname(__file__)):
    print(d)



from pymathics.asy.version import __version__
from pymathics.asy.exportasy import (ExportToJPG,
                                     ExportToPNG,
                                     ExportToSVG,
                                     ExportToPDF)
from mathics.builtin.importexport import Export as MathicsExport
__all__ = ("__version__", "ExportToJPG", "ExportToPNG", "ExportToSVG", "ExportToPDF", "pymathics_version_data")

# To be recognized as an external mathics module, the following variable
# is required:
#
MathicsExport._extdict["pdf"] = "PDF"



pymathics_version_data = {
    "author": "The Mathics Team",
    "version": __version__,
    "requires": [],
}
