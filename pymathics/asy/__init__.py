# -*- coding: utf-8 -*-
"""
Pymathics asymptote graphics handler.

This module provides a replacement for the graphics subsystem using asymptote to draw and export graphics.

"""

import pkg_resources
import os

from pymathics.asy.version import __version__
from pymathics.asy.exportasy import (ExportToJPG,
                                     ExportToPNG,
                                     ExportToSVG,
                                     ExportToPDF)
from pymathics.asy.graphics import (AsyGraphicsBox)
from mathics.core.expression import Expression, String, SymbolTrue
from mathics.core.evaluation import Evaluation
from mathics.builtin.importexport import Export as MathicsExport
__all__ = ("__version__", "ExportToJPG", "ExportToPNG", "ExportToSVG", "ExportToPDF",
           "AsyGraphicsBox", "pymathics_version_data")


ROOT_DIR = pkg_resources.resource_filename('pymathics.asy', '')



def onload(definitions):
#    from mathics.builtin import box_constructs
#    box_constructs["System`GraphicsBox"] = AsyGraphicsBox(expression=False)
#    box_constructs["System`Graphics3DBox"] = AsyGraphics3DBox(expression=False)
    MathicsExport._extdict["pdf"] = "PDF"
    definitions.set_ownvalue("Settings`UseAsyForGraphics2D", SymbolTrue)
    for root, dirs, files in os.walk(os.path.join(ROOT_DIR, "autoload")):
        for path in [os.path.join(root, f) for f in files if f.endswith(".m")]:
            Expression("Get", String(path)).evaluate(Evaluation(definitions))

# To be recognized as an external mathics module, the following variable
# is required:
#




pymathics_version_data = {
    "author": "The Mathics Team",
    "version": __version__,
    "requires": [],
    "onload" : onload
}
