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
                                      create_pens,
                                      RGBColor)

from mathics.builtin.graphics3d import Graphics3D, Graphics3DElements


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
        if not leaves:
            leaves = self._leaves
        elements, calc_dimensions = self._prepare_elements(
            leaves, options, max_width=450
        )

        xmin, xmax, ymin, ymax, w, h, width, height = calc_dimensions()
        elements.view_width = w

        asy_completely_visible = "\n".join(
            element.to_asy()
            for element in elements.elements
            if element.is_completely_visible
        )

        asy_regular = "\n".join(
            element.to_asy()
            for element in elements.elements
            if not element.is_completely_visible
        )

        asy_box = "box((%s,%s), (%s,%s))" % (
            asy_number(xmin),
            asy_number(ymin),
            asy_number(xmax),
            asy_number(ymax),
        )

        if self.background_color is not None:
            color, opacity = self.background_color.to_asy()
            asy_background = "filldraw(%s, %s);" % (asy_box, color)
        else:
            asy_background = ""

        tex = r"""
usepackage("amsmath");
size(%scm, %scm);
%s
%s
clip(%s);
%s
""" % (
            asy_number(width / 60),
            asy_number(height / 60),
            asy_background,
            asy_regular,
            asy_box,
            asy_completely_visible,
        )
        forxml = options.get("forxml", None)
        if forxml:
            return (tex, width, height)
        else:
            return "\n\\begin{asy}\n" + tex + "\n\\end{asy}\n"

    def boxes_to_xml(self, leaves=None, **options):
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
                evaluation.message("GraphicsBox", "asynotav")
                Expression("Set", Symbol("Settings`UseAsyForGraphics2D"), SymbolFalse).evaluate(evaluation)

        if check_asy:
            asy, width, height = self.boxes_to_tex(leaves, forxml=True, **options)
            fin = os.path.join(tempfile._get_default_tempdir(), next(tempfile._get_candidate_names()))
            fout = fin + ".png"
            try:
                with open(fin, 'w+') as borrador:
                    borrador.write(asy)
            except:
                evaluation.message("GraphicsBox", "noasyfile")
                check_asy = False

        if check_asy:
            try:
                # check_call(['asy', '-f', 'svg', '--svgemulation' ,'-o', fout, fin], stdout=DEVNULL, stderr=DEVNULL)
                check_call([asy_path, '-f', 'png', '-render', '16', '-o', fout, fin], stdout=DEVNULL, stderr=DEVNULL)
            except:
                evaluation.message("GraphicsBox", "asyfail")
                check_asy = False

        if check_asy:
            with open(fout, 'rb') as ff:
                png = ff.read()

            # svg = svg[svg.find("<svg "):]
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
        elements, calc_dimensions = self._prepare_elements(leaves, options, neg_y=True)

        xmin, xmax, ymin, ymax, w, h, width, height = calc_dimensions()
        elements.view_width = w

        svg = elements.to_svg()

        if self.background_color is not None:
            svg = '<rect x="%f" y="%f" width="%f" height="%f" style="fill:%s"/>%s' % (
                xmin,
                ymin,
                w,
                h,
                self.background_color.to_css()[0],
                svg,
            )

        xmin -= 1
        ymin -= 1
        w += 2
        h += 2

        svg_xml = """
            <svg xmlns:svg="http://www.w3.org/2000/svg"
                xmlns="http://www.w3.org/2000/svg"
                version="1.1"
                viewBox="%s">
                %s
            </svg>
        """ % (
            " ".join("%f" % t for t in (xmin, ymin, w, h)),
            svg,
        )

        return (
            '<img width="%dpx" height="%dpx" src="data:image/svg+xml;base64,%s"/>'
            % (
                int(width),
                int(height),
                base64.b64encode(svg_xml.encode("utf8")).decode("utf8"),
            )
        )


