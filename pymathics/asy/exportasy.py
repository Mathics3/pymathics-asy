#!/usr/bin/env python3
# -*- coding: utf-8 -*-


########################   Asy Exporters  ###############################
#
# This could be in another module, or in a pymathics external module
#
#

import tempfile
import os
from subprocess import DEVNULL, STDOUT, check_call
from mathics.core.expression import (Expression, String, BoxError, SymbolFailed, SymbolNull)
from mathics_scanner import replace_wl_with_plain_text
from mathics.builtin.image import Image
from mathics.builtin import Builtin

class _AsyExporter(Builtin):
    attributes = ("HoldRest", )

    messages = {"boxerr": "Not able to interpret box `1`",
                "nowrtacs": "ExportToPDF requires write access.",
                "asyfld"  :  "Asymptote failed to generate the file",
    }

    extension = None

    def apply_asy(self, filename, expr, evaluation, **options):
        '%(name)s[filename_String, expr_, OptionsPattern[%(name)s]]'

        if expr.get_head_name() == "System`Image":
            res = Expression("System`ImageExport", filename,  expr)
            return res.evaluate(evaluation)

        filename = filename.value
        if expr.get_head_name() not in ("System`Graphics", "System`Graphics3D"):
            expr = Expression("Text", expr)
            expr = Expression("Graphics",
                              Expression("List",
                                         expr)
            )

        asy_code = Expression("MakeBoxes", expr).evaluate(evaluation)
        try:
            asy_code = asy_code.boxes_to_tex(evaluation=evaluation)
        except BoxError as e:
            evaluation.message(self.get_name(),"boxerr", e.box)
            return SymbolFailed

        asy_code = asy_code[13:-10]
        asy_code = replace_wl_with_plain_text(asy_code, False)
        # TODO: Handle properly WL characters to latex commands
        asy_code = asy_code.replace("\\[DifferentialD]", "d ")
        fin = os.path.join(tempfile._get_default_tempdir(),
                           next(tempfile._get_candidate_names()))
        from pymathics.asy import asy_path
        try:
            with open(fin, 'w+') as borrador:
                borrador.write(asy_code)
        except:
            evaluation.message(self.get_name(),"nowrtacs")
            return SymbolFailed
        if self.extension == "svg":
            cmdline = [asy_path, '-f', self.extension,
          	       '--svgemulation' ,
                       '-o',
                       filename,
                       fin]
        else:
            cmdline = [asy_path, '-f', self.extension,
                       '-o',
                       filename,
                       fin]
        try:
            check_call(cmdline, stdout=DEVNULL, stderr=DEVNULL)
        except:
            evaluation.message(self.get_name(), "asyfld")
            return SymbolFailed
        return SymbolNull


class ExportToSVG(_AsyExporter):
    """
    <dl>
    <dt> 'System`Convert`TextDump`ExportSVG[$filename$, $expr$]'
    <dd> Export the expression to a SVG file

    This is an internal builtin that takes an expression,
    convert it in a Graphics object, and export it to Asy.
    Then, from the asy set of instructions, a pdf is built
    </dl>
    """
    extension = "svg"
    context = "System`Convert`TextDump`"


class ExportToPDF(_AsyExporter):
    """
    <dl>
    <dt> 'System`Convert`PDFDump`ExportToPDF[$filename$, $expr$]'
    <dd> Export the expression to a PDF file

    This is an internal builtin that takes an expression,
    convert it in a Graphics object, and export it to Asy.
    Then, from the asy set of instructions, a pdf is built
    </dl>
    """

    extension = "pdf"
    context = "System`Convert`PDFDump`"


class ExportToPNG(_AsyExporter):
    """
    <dl>
    <dt> 'System`Convert`Image`ExportPNG[$filename$, $expr$]'
    <dd> Export the expression to a PNG file

    This is an internal builtin that takes an expression,
    convert it in a Graphics object, and export it to Asy.
    Then, from the asy set of instructions, a pdf is built
    </dl>
    """
    extension = "png"
    context = "System`Convert`Image`"


class ExportToJPG(_AsyExporter):
    """
    <dl>
    <dt> 'System`Convert`Image`ExportJPG[$filename$, $expr$]'
    <dd> Export the expression to a JPG file

    This is an internal builtin that takes an expression,
    convert it in a Graphics object, and export it to Asy.
    Then, from the asy set of instructions, a pdf is built
    </dl>
    """
    extension = "jpeg"
    context = "System`Convert`Image`"

