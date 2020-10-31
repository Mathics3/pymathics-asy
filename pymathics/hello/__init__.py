# -*- coding: utf-8 -*-
"""
PyMathics Hello test module.

This is an example of an external PyMathics module.

A PyMathics module is a Python module which can be loaded into Mathics using the
``LoadModule[]`` method.

In particular, to load this after installing this module as a Python module run inside
Mathics:

   ::

   In[1]:= LoadModule["pymathics.hello"]
   Out[1]= pymathics.hello

If you don't get an error, you should then be able to run:

   ::

   In[2]:= PyMathics`Hello["World"]
   Out[2]:= Hello, World!

   In[3]:= PyMathics`$HelloUser
   Out[3]:= $your-login-name$

"""

import os
from mathics.builtin.base import Builtin, Symbol, String, Predefined

# To be recognized as an external mathics module, the following variable
# is required:
#
pymathics_version_data = {
    "author": "Juan Mauricio Matera",
    "version": "1.0.0",
    "requires": [],
}  # Maybe this field is useful.


class Hello(Builtin):
    """
    <dl>
      <dt>'Hello'[$person$]
      <dd>An example function in a Python-importable Mathics module.
    </dl>
    >> PyMathics`Hello["World"]
     = Hello, World!
    """

    context = "PyMathics`"

    attributes = ("Protected", "OneIdentity")

    def apply(self, person, evaluation):
        "PyMathics`Hello[person_]"
        return String("Hello, %s!" % person)


class HelloUser(Predefined):
    """
    <dl>
       <dt>'$PyMathics`HelloUser'
       <dd>An example prefined string in a Python-importable Mathics module.
    </dl>
    >> Pymathics`HelloUser
     = ...
    """

    context = "PyMathics`"
    name = "$HelloUser"

    def evaluate(self, evaluation) -> String:
        return String(os.getlogin())
