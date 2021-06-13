#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cython: language_level=3

"""
Drawing Graphics with asy
"""


from math import floor, ceil, log10, sin, cos, pi, sqrt, atan2, degrees, radians, exp
import json
import base64
from itertools import chain
import numbers



from mathics.builtin.base import (
    Builtin,
    InstanceableBuiltin,
    BoxConstruct,
    BoxConstructError,
)
from mathics.builtin.options import options_to_rules
from mathics.core.expression import (
    Expression,
    Integer,
    Rational,
    Real,
    String,
    Symbol,
    SymbolTrue,
    SymbolFalse,
    strip_context,
    system_symbols,
    system_symbols_dict,
    from_python,
)

from mathics.builtin.graphics import (GRAPHICS_OPTIONS,
                                      GraphicsBox,
                                      Graphics,
                                      asy_number,
                                      RGBColor)

from mathics.formatter.asy import asy_create_pens
from mathics.builtin.drawing.graphics3d import Graphics3D, Graphics3DElements


class AsyGraphicsBox(GraphicsBox):
    context="System`"
    options = Graphics.options
    _graphics = Graphics(expression=False)
    attributes = ("HoldAll", "ReadProtected")

    messages = {
        "asynotav": 'Asymptote is not available in this system. Using the buggy backend.',
        "noasyfile": 'Asy requires write permisions over a temporary file, but it was not available. Using the buggy backend',
        "asyfail": 'Asymptote failed building the svg picture. Using the buggy backend.',
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
            width = float(width[:-2])*60
            height = float(height[:-4])*60
            return (tex, width, height)

    def boxes_to_mathml(self, leaves=None, **options):
        if leaves is None:
            leaves = self._leaves
        evaluation = options.get("evaluation", None)
        check_asy = False
        if evaluation:
            check_asy = evaluation.definitions.get_ownvalue("Settings`UseAsyForGraphics2D")
            if check_asy:
                check_asy = check_asy.replace.is_true()
        if check_asy:
            import os
            from subprocess import DEVNULL, STDOUT, check_call
            from pymathics.asy import asy_path
            import tempfile
            try:
                check_call([asy_path, '--version'], stdout=DEVNULL, stderr=DEVNULL)
            except:
                check_asy = False
                evaluation.message("AsyGraphicsBox", "asynotav")
                Expression("Set", Symbol("Settings`UseAsyForGraphics2D"), SymbolFalse).evaluate(evaluation)

        if check_asy:
            asy, width, height = self.boxes_to_tex(leaves, forxml=True, **options)
            fin = os.path.join(tempfile._get_default_tempdir(), next(tempfile._get_candidate_names()))
            fout = fin + ".png"
            try:
                with open(fin, 'w+') as borrador:
                    borrador.write(asy)
            except:
                evaluation.message("AsyGraphicsBox", "noasyfile")
                check_asy = False

        if check_asy:
            try:
                # check_call(['asy', '-f', 'svg', '--svgemulation' ,'-o', fout, fin], stdout=DEVNULL, stderr=DEVNULL)
                check_call([asy_path, '-f', 'png', '-render', '16', '-o', fout, fin], stdout=DEVNULL, stderr=DEVNULL)
            except:
                evaluation.message("AsyGraphicsBox", "asyfail")
                check_asy = False

        if check_asy:
            with open(fout, 'rb') as ff:
                png = ff.read()

            return (
                '''
                <mglyph width="%d" height="%d" src="data:image/png;base64,%s"/></mglyph>'''
                % (
                    int(width),
                    int(height),
                    base64.b64encode(png).decode("utf8"),
#                    base64.b64encode(svg.encode("utf8")).decode("utf8"),
                )
            )
        # Not using asymptote. Continue with the buggy backend...
        return super(AsyGraphicsBox, self).boxes_to_mathml(leaves=leaves, **options)


