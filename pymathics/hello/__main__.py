# -*- coding: utf-8 -*-
from mathics.builtin.base import Builtin, String

class Hello(Builtin):
    """
    <dl>
      <dt>'Hello'[$person$]
      <dd>An example function in a Python-importable Mathics module.
    </dl>
    >> PyMathics`Hello["World"]
     = Hello, World!
    """

    def apply(self, person, evaluation):
        "PyMathics`Hello[person_]"
        return String("Hello, %s!" % person.get_string_value())
