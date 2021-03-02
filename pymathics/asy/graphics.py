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

from mathics.builtin.base import (
    Builtin,
    InstancableBuiltin,
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
                                      Graphics)



class AsyGraphicsBox(GraphicsBox):
    options = Graphics.options

    attributes = ("HoldAll", "ReadProtected")

    messages = {
        "asynotav": 'Asymptote is not available in this system. Using the buggy backend.',
        "noasyfile": 'Asy requires write permisions over a temporary file, but it was not available. Using the buggy backend',
        "asyfail": 'Asymptote failed building the svg picture. Using the buggy backend.',
    }

    def boxes_to_tex(self, leaves, **options):
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

    def boxes_to_xml(self, leaves, **options):
        evaluation = options.get("evaluation", None)
        check_asy = False
        if evaluation:
            check_asy = evaluation.definitions.get_ownvalue("Settings`UseAsyForGraphics2D")
            if check_asy:
                check_asy = check_asy.replace.is_true()
  
        if check_asy:
            import os
            from subprocess import DEVNULL, STDOUT, check_call
            import tempfile
            try:
                check_call(['asy', '--version'], stdout=DEVNULL, stderr=DEVNULL)
            except:
                check_asy = False
                evaluation.message("GraphicsBox", "asynotav")
                Expression("Set", Symbol("Settings`UseAsyForGraphics2D"), SymbolFalse).evaluate(evaluation)

        if check_asy:
            asy, width, height = self.boxes_to_tex(leaves, forxml=True, **options)
            fin = os.path.join(tempfile._get_default_tempdir(), next(tempfile._get_candidate_names()))
            fout = fin + ".svg"
            try:
                with open(fin, 'w+') as borrador:
                    borrador.write(asy)
            except:
                evaluation.message("GraphicsBox", "noasyfile")
                check_asy = False

        if check_asy:
            try:
                check_call(['asy', '-f', 'svg', '--svgemulation' ,'-o', fout, fin], stdout=DEVNULL, stderr=DEVNULL)
            except:
                evaluation.message("GraphicsBox", "asyfail")
                check_asy = False

        if check_asy:
            with open(fout, 'rt') as ff:
                svg = ff.read()

            svg = svg[svg.find("<svg "):]
            return (
                '<img  width="%dpx" height="%dpx" src="data:image/svg+xml;base64,%s"/>'
                % (
                    int(width),
                    int(height),
                    base64.b64encode(svg.encode("utf8")).decode("utf8"),
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
            '<mglyph width="%dpx" height="%dpx" src="data:image/svg+xml;base64,%s"/>'
            % (
                int(width),
                int(height),
                base64.b64encode(svg_xml.encode("utf8")).decode("utf8"),
            )
        )



class AsyGraphics3DBox(AsyGraphicsBox):
    def boxes_to_text(self, leaves, **options):
        return "-Graphics3D-"

    def _prepare_elements(self, leaves, options, max_width=None):
        if not leaves:
            raise BoxConstructError

        graphics_options = self.get_option_values(leaves[1:], **options)

        evaluation = options["evaluation"]

        base_width, base_height, size_multiplier, size_aspect = self._get_image_size(
            options, graphics_options, max_width
        )

        # TODO: Handle ImageScaled[], and Scaled[]
        lighting_option = graphics_options["System`Lighting"]
        lighting = lighting_option.to_python()  # can take symbols or strings
        self.lighting = []

        if lighting == "System`Automatic":
            self.lighting = [
                {"type": "Ambient", "color": [0.3, 0.2, 0.4]},
                {
                    "type": "Directional",
                    "color": [0.8, 0.0, 0.0],
                    "position": [2, 0, 2],
                },
                {
                    "type": "Directional",
                    "color": [0.0, 0.8, 0.0],
                    "position": [2, 2, 2],
                },
                {
                    "type": "Directional",
                    "color": [0.0, 0.0, 0.8],
                    "position": [0, 2, 2],
                },
            ]
        elif lighting == "Neutral":  # Lighting->"Neutral"
            self.lighting = [
                {"type": "Ambient", "color": [0.3, 0.3, 0.3]},
                {
                    "type": "Directional",
                    "color": [0.3, 0.3, 0.3],
                    "position": [2, 0, 2],
                },
                {
                    "type": "Directional",
                    "color": [0.3, 0.3, 0.3],
                    "position": [2, 2, 2],
                },
                {
                    "type": "Directional",
                    "color": [0.3, 0.3, 0.3],
                    "position": [0, 2, 2],
                },
            ]
        elif lighting == "System`None":
            pass

        elif isinstance(lighting, list) and all(
            isinstance(light, list) for light in lighting
        ):
            for light in lighting:
                if light[0] in ['"Ambient"', '"Directional"', '"Point"', '"Spot"']:
                    try:
                        head = light[1].get_head_name()
                    except AttributeError:
                        break
                    color = get_class(head)(light[1])
                    if light[0] == '"Ambient"':
                        self.lighting.append(
                            {
                                "type": "Ambient",
                                "color": color.to_rgba(),
                            }
                        )
                    elif light[0] == '"Directional"':
                        position = [0, 0, 0]
                        if isinstance(light[2], list):
                            if len(light[2]) == 3:
                                position = light[2]
                            if len(light[2]) == 2 and all(  # noqa
                                isinstance(p, list) and len(p) == 3 for p in light[2]
                            ):
                                position = [
                                    light[2][0][i] - light[2][1][i] for i in range(3)
                                ]
                        self.lighting.append(
                            {
                                "type": "Directional",
                                "color": color.to_rgba(),
                                "position": position,
                            }
                        )
                    elif light[0] == '"Point"':
                        position = [0, 0, 0]
                        if isinstance(light[2], list) and len(light[2]) == 3:
                            position = light[2]
                        self.lighting.append(
                            {
                                "type": "Point",
                                "color": color.to_rgba(),
                                "position": position,
                            }
                        )
                    elif light[0] == '"Spot"':
                        position = [0, 0, 1]
                        target = [0, 0, 0]
                        if isinstance(light[2], list):
                            if len(light[2]) == 2:
                                if (
                                    isinstance(light[2][0], list)
                                    and len(light[2][0]) == 3  # noqa
                                ):
                                    position = light[2][0]
                                if (
                                    isinstance(light[2][1], list)
                                    and len(light[2][1]) == 3  # noqa
                                ):
                                    target = light[2][1]
                            if len(light[2]) == 3:
                                position = light[2]
                        angle = light[3]
                        self.lighting.append(
                            {
                                "type": "Spot",
                                "color": color.to_rgba(),
                                "position": position,
                                "target": target,
                                "angle": angle,
                            }
                        )

        else:
            evaluation.message("Graphics3D", "invlight", lighting_option)

        # ViewPoint Option
        viewpoint_option = graphics_options["System`ViewPoint"]
        viewpoint = viewpoint_option.to_python(n_evaluation=evaluation)

        if isinstance(viewpoint, list) and len(viewpoint) == 3:
            if all(isinstance(x, numbers.Real) for x in viewpoint):
                # TODO Infinite coordinates e.g. {0, 0, Infinity}
                pass
        else:
            try:
                viewpoint = {
                    "Above": [0, 0, 2],
                    "Below": [0, 0, -2],
                    "Front": [0, -2, 0],
                    "Back": [0, 2, 0],
                    "Left": [-2, 0, 0],
                    "Right": [2, 0, 0],
                }[viewpoint]
            except KeyError:
                # evaluation.message()
                # TODO
                viewpoint = [1.3, -2.4, 2]

        assert (
            isinstance(viewpoint, list)
            and len(viewpoint) == 3
            and all(isinstance(x, numbers.Real) for x in viewpoint)
        )
        self.viewpoint = viewpoint

        # TODO Aspect Ratio
        # aspect_ratio = graphics_options['AspectRatio'].to_python()

        boxratios = graphics_options["System`BoxRatios"].to_python()
        if boxratios == "System`Automatic":
            boxratios = ["System`Automatic"] * 3
        else:
            boxratios = boxratios
        if not isinstance(boxratios, list) or len(boxratios) != 3:
            raise BoxConstructError

        plot_range = graphics_options["System`PlotRange"].to_python()
        if plot_range == "System`Automatic":
            plot_range = ["System`Automatic"] * 3
        if not isinstance(plot_range, list) or len(plot_range) != 3:
            raise BoxConstructError

        elements = Graphics3DElements(leaves[0], evaluation)

        def calc_dimensions(final_pass=True):
            if "System`Automatic" in plot_range:
                xmin, xmax, ymin, ymax, zmin, zmax = elements.extent()
            else:
                xmin = xmax = ymin = ymax = zmin = zmax = None

            try:
                if plot_range[0] == "System`Automatic":
                    if xmin is None and xmax is None:
                        xmin = 0
                        xmax = 1
                    elif xmin == xmax:
                        xmin -= 1
                        xmax += 1
                elif isinstance(plot_range[0], list) and len(plot_range[0]) == 2:
                    xmin, xmax = list(map(float, plot_range[0]))
                    xmin = elements.translate((xmin, 0, 0))[0]
                    xmax = elements.translate((xmax, 0, 0))[0]
                else:
                    raise BoxConstructError

                if plot_range[1] == "System`Automatic":
                    if ymin is None and ymax is None:
                        ymin = 0
                        ymax = 1
                    elif ymin == ymax:
                        ymin -= 1
                        ymax += 1
                elif isinstance(plot_range[1], list) and len(plot_range[1]) == 2:
                    ymin, ymax = list(map(float, plot_range[1]))
                    ymin = elements.translate((0, ymin, 0))[1]
                    ymax = elements.translate((0, ymax, 0))[1]
                else:
                    raise BoxConstructError

                if plot_range[2] == "System`Automatic":
                    if zmin is None and zmax is None:
                        zmin = 0
                        zmax = 1
                    elif zmin == zmax:
                        zmin -= 1
                        zmax += 1
                elif isinstance(plot_range[1], list) and len(plot_range[1]) == 2:
                    zmin, zmax = list(map(float, plot_range[2]))
                    zmin = elements.translate((0, 0, zmin))[2]
                    zmax = elements.translate((0, 0, zmax))[2]
                else:
                    raise BoxConstructError
            except (ValueError, TypeError):
                raise BoxConstructError

            boxscale = [1.0, 1.0, 1.0]
            if boxratios[0] != "System`Automatic":
                boxscale[0] = boxratios[0] / (xmax - xmin)
            if boxratios[1] != "System`Automatic":
                boxscale[1] = boxratios[1] / (ymax - ymin)
            if boxratios[2] != "System`Automatic":
                boxscale[2] = boxratios[2] / (zmax - zmin)

            if final_pass:
                xmin *= boxscale[0]
                xmax *= boxscale[0]
                ymin *= boxscale[1]
                ymax *= boxscale[1]
                zmin *= boxscale[2]
                zmax *= boxscale[2]

                # Rescale lighting
                for i, light in enumerate(self.lighting):
                    if self.lighting[i]["type"] != "Ambient":
                        self.lighting[i]["position"] = [
                            light["position"][j] * boxscale[j] for j in range(3)
                        ]
                    if self.lighting[i]["type"] == "Spot":
                        self.lighting[i]["target"] = [
                            light["target"][j] * boxscale[j] for j in range(3)
                        ]

                # Rescale viewpoint
                self.viewpoint = [
                    vp * max([xmax - xmin, ymax - ymin, zmax - zmin])
                    for vp in self.viewpoint
                ]

            return xmin, xmax, ymin, ymax, zmin, zmax, boxscale

        xmin, xmax, ymin, ymax, zmin, zmax, boxscale = calc_dimensions(final_pass=False)

        axes, ticks = self.create_axes(
            elements, graphics_options, xmin, xmax, ymin, ymax, zmin, zmax, boxscale
        )

        return elements, axes, ticks, calc_dimensions, boxscale

    def boxes_to_tex(self, leaves, **options):
        elements, axes, ticks, calc_dimensions, boxscale = self._prepare_elements(
            leaves, options, max_width=450
        )

        elements._apply_boxscaling(boxscale)

        asy = elements.to_asy()

        xmin, xmax, ymin, ymax, zmin, zmax, boxscale = calc_dimensions()

        # TODO: Intelligently place the axes on the longest non-middle edge.
        # See algorithm used by web graphics in mathics/web/media/graphics.js
        # for details of this. (Projection to sceen etc).

        # Choose axes placement (boundbox edge vertices)
        axes_indices = []
        if axes[0]:
            axes_indices.append(0)
        if axes[1]:
            axes_indices.append(6)
        if axes[2]:
            axes_indices.append(8)

        # Draw boundbox and axes
        boundbox_asy = ""
        boundbox_lines = self.get_boundbox_lines(xmin, xmax, ymin, ymax, zmin, zmax)

        for i, line in enumerate(boundbox_lines):
            if i in axes_indices:
                pen = create_pens(
                    edge_color=RGBColor(components=(0, 0, 0, 1)), stroke_width=1.5
                )
            else:
                pen = create_pens(
                    edge_color=RGBColor(components=(0.4, 0.4, 0.4, 1)), stroke_width=1
                )

            path = "--".join(["(%.5g,%.5g,%.5g)" % coords for coords in line])
            boundbox_asy += "draw((%s), %s);\n" % (path, pen)

        # TODO: Intelligently draw the axis ticks such that they are always
        # directed inward and choose the coordinate direction which makes the
        # ticks the longest. Again, details in mathics/web/media/graphics.js

        # Draw axes ticks
        ticklength = 0.05 * max([xmax - xmin, ymax - ymin, zmax - zmin])
        pen = create_pens(
            edge_color=RGBColor(components=(0, 0, 0, 1)), stroke_width=1.2
        )
        for xi in axes_indices:
            if xi < 4:  # x axis
                for i, tick in enumerate(ticks[0][0]):
                    line = [
                        (tick, boundbox_lines[xi][0][1], boundbox_lines[xi][0][2]),
                        (
                            tick,
                            boundbox_lines[xi][0][1],
                            boundbox_lines[xi][0][2] + ticklength,
                        ),
                    ]

                    path = "--".join(
                        ["({0},{1},{2})".format(*coords) for coords in line]
                    )

                    boundbox_asy += "draw(({0}), {1});\n".format(path, pen)
                    boundbox_asy += 'label("{0}",{1},{2});\n'.format(
                        ticks[0][2][i],
                        (tick, boundbox_lines[xi][0][1], boundbox_lines[xi][0][2]),
                        "S",
                    )

                for small_tick in ticks[0][1]:
                    line = [
                        (
                            small_tick,
                            boundbox_lines[xi][0][1],
                            boundbox_lines[xi][0][2],
                        ),
                        (
                            small_tick,
                            boundbox_lines[xi][0][1],
                            boundbox_lines[xi][0][2] + 0.5 * ticklength,
                        ),
                    ]

                    path = "--".join(
                        ["({0},{1},{2})".format(*coords) for coords in line]
                    )

                    boundbox_asy += "draw(({0}), {1});\n".format(path, pen)

            if 4 <= xi < 8:  # y axis
                for i, tick in enumerate(ticks[1][0]):
                    line = [
                        (boundbox_lines[xi][0][0], tick, boundbox_lines[xi][0][2]),
                        (
                            boundbox_lines[xi][0][0],
                            tick,
                            boundbox_lines[xi][0][2] - ticklength,
                        ),
                    ]
                    path = "--".join(
                        ["({0},{1},{2})".format(*coords) for coords in line]
                    )

                    boundbox_asy += "draw(({0}), {1});\n".format(path, pen)

                    boundbox_asy += 'label("{0}",{1},{2});\n'.format(
                        ticks[1][2][i],
                        (boundbox_lines[xi][0][0], tick, boundbox_lines[xi][0][2]),
                        "NW",
                    )

                for small_tick in ticks[1][1]:
                    line = [
                        (
                            boundbox_lines[xi][0][0],
                            small_tick,
                            boundbox_lines[xi][0][2],
                        ),
                        (
                            boundbox_lines[xi][0][0],
                            small_tick,
                            boundbox_lines[xi][0][2] - 0.5 * ticklength,
                        ),
                    ]
                    path = "--".join(
                        ["({0},{1},{2})".format(*coords) for coords in line]
                    )
                    boundbox_asy += "draw(({0}), {1});\n".format(path, pen)
            if 8 <= xi:  # z axis
                for i, tick in enumerate(ticks[2][0]):
                    line = [
                        (boundbox_lines[xi][0][0], boundbox_lines[xi][0][1], tick),
                        (
                            boundbox_lines[xi][0][0],
                            boundbox_lines[xi][0][1] + ticklength,
                            tick,
                        ),
                    ]
                    path = "--".join(
                        ["({0},{1},{2})".format(*coords) for coords in line]
                    )
                    boundbox_asy += "draw(({0}), {1});\n".format(path, pen)
                    boundbox_asy += 'label("{0}",{1},{2});\n'.format(
                        ticks[2][2][i],
                        (boundbox_lines[xi][0][0], boundbox_lines[xi][0][1], tick),
                        "W",
                    )
                for small_tick in ticks[2][1]:
                    line = [
                        (
                            boundbox_lines[xi][0][0],
                            boundbox_lines[xi][0][1],
                            small_tick,
                        ),
                        (
                            boundbox_lines[xi][0][0],
                            boundbox_lines[xi][0][1] + 0.5 * ticklength,
                            small_tick,
                        ),
                    ]
                    path = "--".join(
                        ["({0},{1},{2})".format(*coords) for coords in line]
                    )
                    boundbox_asy += "draw(({0}), {1});\n".format(path, pen)

        (height, width) = (400, 400)  # TODO: Proper size
        tex = r"""
\begin{{asy}}
import three;
import solids;
size({0}cm, {1}cm);
currentprojection=perspective({2[0]},{2[1]},{2[2]});
currentlight=light(rgb(0.5,0.5,1), specular=red, (2,0,2), (2,2,2), (0,2,2));
{3}
{4}
\end{{asy}}
""".format(
            asy_number(width / 60),
            asy_number(height / 60),
            self.viewpoint,
            asy,
            boundbox_asy,
        )
        return tex

    def boxes_to_xml(self, leaves, **options):
        elements, axes, ticks, calc_dimensions, boxscale = self._prepare_elements(
            leaves, options
        )

        elements._apply_boxscaling(boxscale)

        json_repr = elements.to_json()

        xmin, xmax, ymin, ymax, zmin, zmax, boxscale = calc_dimensions()

        # TODO: Cubeoid (like this)
        # json_repr = [{'faceColor': (1, 1, 1, 1), 'position': [(0,0,0), None],
        # 'size':[(1,1,1), None], 'type': 'cube'}]

        json_repr = json.dumps(
            {
                "elements": json_repr,
                "axes": {
                    "hasaxes": axes,
                    "ticks": ticks,
                },
                "extent": {
                    "xmin": xmin,
                    "xmax": xmax,
                    "ymin": ymin,
                    "ymax": ymax,
                    "zmin": zmin,
                    "zmax": zmax,
                },
                "lighting": self.lighting,
                "viewpoint": self.viewpoint,
            }
        )

        # return "<mn>3</mn>"

        # xml = ('<graphics3d xmin="%f" xmax="%f" ymin="%f" ymax="%f" '
        #        'zmin="%f" zmax="%f" data="%s" />') % (
        #           xmin, xmax, ymin, ymax, zmin, zmax, json_repr)
        xml = '<graphics3d data="{0}" />'.format(html.escape(json_repr))
        xml = "<mtable><mtr><mtd>{0}</mtd></mtr></mtable>".format(xml)
        return xml

    def create_axes(
        self, elements, graphics_options, xmin, xmax, ymin, ymax, zmin, zmax, boxscale
    ):
        axes = graphics_options.get("System`Axes")
        if axes.is_true():
            axes = (True, True, True)
        elif axes.has_form("List", 3):
            axes = (leaf.is_true() for leaf in axes.leaves)
        else:
            axes = (False, False, False)
        ticks_style = graphics_options.get("System`TicksStyle")
        axes_style = graphics_options.get("System`AxesStyle")
        label_style = graphics_options.get("System`LabelStyle")
        if ticks_style.has_form("List", 3):
            ticks_style = ticks_style.leaves
        else:
            ticks_style = [ticks_style] * 3
        if axes_style.has_form("List", 3):
            axes_style = axes_style.leaves
        else:
            axes_style = [axes_style] * 3

        ticks_style = [elements.create_style(s) for s in ticks_style]
        axes_style = [elements.create_style(s) for s in axes_style]
        label_style = elements.create_style(label_style)
        ticks_style[0].extend(axes_style[0])
        ticks_style[1].extend(axes_style[1])

        ticks = [
            self.axis_ticks(xmin, xmax),
            self.axis_ticks(ymin, ymax),
            self.axis_ticks(zmin, zmax),
        ]

        # Add zero if required, since axis_ticks does not
        if xmin <= 0 <= xmax:
            ticks[0][0].append(0.0)
            ticks[0][0].sort()
        if ymin <= 0 <= ymax:
            ticks[1][0].append(0.0)
            ticks[1][0].sort()
        if zmin <= 0 <= zmax:
            ticks[2][0].append(0.0)
            ticks[2][0].sort()

        # Convert ticks to nice strings e.g 0.100000000000002 -> '0.1' and
        # scale ticks appropriately
        ticks = [
            [
                [boxscale[i] * x for x in t[0]],
                [boxscale[i] * x for x in t[1]],
                ["%g" % x for x in t[0]],
            ]
            for i, t in enumerate(ticks)
        ]

        return axes, ticks

    def get_boundbox_lines(self, xmin, xmax, ymin, ymax, zmin, zmax):
        return [
            [(xmin, ymin, zmin), (xmax, ymin, zmin)],
            [(xmin, ymax, zmin), (xmax, ymax, zmin)],
            [(xmin, ymin, zmax), (xmax, ymin, zmax)],
            [(xmin, ymax, zmax), (xmax, ymax, zmax)],
            [(xmin, ymin, zmin), (xmin, ymax, zmin)],
            [(xmax, ymin, zmin), (xmax, ymax, zmin)],
            [(xmin, ymin, zmax), (xmin, ymax, zmax)],
            [(xmax, ymin, zmax), (xmax, ymax, zmax)],
            [(xmin, ymin, zmin), (xmin, ymin, zmax)],
            [(xmax, ymin, zmin), (xmax, ymin, zmax)],
            [(xmin, ymax, zmin), (xmin, ymax, zmax)],
            [(xmax, ymax, zmin), (xmax, ymax, zmax)],
        ]
