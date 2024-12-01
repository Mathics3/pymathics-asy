#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cython: language_level=3

"""
Drawing Graphics with asy
"""


import base64
import json
import numbers
from itertools import chain
from math import atan2, ceil, cos, degrees, exp, floor, log10, pi, radians, sin, sqrt

from mathics.builtin.box.graphics import GraphicsBox
from mathics.builtin.drawing.graphics3d import Graphics3D, Graphics3DElements
from mathics.builtin.graphics import GRAPHICS_OPTIONS, Graphics, RGBColor
from mathics.builtin.options import options_to_rules
from mathics.core.atoms import Integer, Rational, Real, String
from mathics.core.builtin import Builtin, BuiltinElement
from mathics.core.convert.python import from_python
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolFalse, SymbolTrue, strip_context
from mathics.format.asy import asy_create_pens
from mathics.core.attributes import A_HOLD_ALL, A_READ_PROTECTED

class AsyGraphicsBox(GraphicsBox):
    context = "System`"
    options = Graphics.options
    _graphics = Graphics(expression=False)
    attributes = A_HOLD_ALL| A_READ_PROTECTED

    messages = {
        "asynotav": "Asymptote is not available in this system. Using the buggy backend.",
        "noasyfile": "Asy requires write permisions over a temporary file, but it was not available. Using the buggy backend",
        "asyfail": "Asymptote failed building the svg picture. Using the buggy backend.",
    }

    def apply_makeboxes(self, content, evaluation, options):
        """System`MakeBoxes[System`Graphics[content_, OptionsPattern[System`Graphics]],
        System`StandardForm|System`TraditionalForm|System`OutputForm]"""
        gb = self._graphics.apply_makeboxes(content, evaluation, options)
        leaves = gb._leaves
        return AsyGraphicsBox(*leaves)

    def boxes_to_tex(self, leaves=None, **options):
        tex = super(AsyGraphicsBox, self).boxes_to_tex(leaves=leaves, **options)
        forxml = options.get("forxml", None)
        if not forxml:
            return tex
        else:
            # All this extra code is because
            # in the core there is not a
            # boxes_to_asy but a boxes_to_tex
            # function, or a way to avoid the
            # header needed in LaTeX.
            tex = tex[13:-10]
            widthheight = tex[28:]
            endline = widthheight.find("\n")
            widthheight = widthheight[:endline]
            width, height = widthheight.split(",")
            width = float(width[:-2]) * 60
            height = float(height[:-4]) * 60
            return (tex, width, height)

    def boxes_to_mathml(self, leaves=None, **options):
        if leaves is None:
            leaves = self._leaves
        evaluation = options.get("evaluation", None)
        check_asy = False
        if evaluation:
            check_asy = evaluation.definitions.get_ownvalue(
                "Settings`UseAsyForGraphics2D"
            )
            if check_asy:
                check_asy = check_asy.replace.is_true()
        if check_asy:
            import os
            import tempfile
            from subprocess import DEVNULL, STDOUT, check_call

            from pymathics.asy import asy_path

            try:
                check_call([asy_path, "--version"], stdout=DEVNULL, stderr=DEVNULL)
            except:
                check_asy = False
                evaluation.message("AsyGraphicsBox", "asynotav")
                Expression(
                    "Set", Symbol("Settings`UseAsyForGraphics2D"), SymbolFalse
                ).evaluate(evaluation)

        if check_asy:
            asy, width, height = self.boxes_to_tex(leaves, forxml=True, **options)
            fin = os.path.join(
                tempfile._get_default_tempdir(), next(tempfile._get_candidate_names())
            )
            fout = fin + ".png"
            try:
                with open(fin, "w+") as borrador:
                    borrador.write(asy)
            except:
                evaluation.message("AsyGraphicsBox", "noasyfile")
                check_asy = False

        if check_asy:
            try:
                # check_call(['asy', '-f', 'svg', '--svgemulation' ,'-o', fout, fin], stdout=DEVNULL, stderr=DEVNULL)
                check_call(
                    [asy_path, "-f", "png", "-render", "16", "-o", fout, fin],
                    stdout=DEVNULL,
                    stderr=DEVNULL,
                )
            except:
                evaluation.message("AsyGraphicsBox", "asyfail")
                check_asy = False

        if check_asy:
            with open(fout, "rb") as ff:
                png = ff.read()

            return """
                <mglyph width="%d" height="%d" src="data:image/png;base64,%s"/></mglyph>""" % (
                int(width),
                int(height),
                base64.b64encode(png).decode("utf8"),
                #                    base64.b64encode(svg.encode("utf8")).decode("utf8"),
            )
        # Not using asymptote. Continue with the buggy backend...
        return super(AsyGraphicsBox, self).boxes_to_mathml(leaves=leaves, **options)
