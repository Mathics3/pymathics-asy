Test PyMathics module

This is a Python module for Mathics that is an simple "Hello, World" example
that is typically used as a minimal example to for demonstration purposes.

Here we are demonstrating how to write a PyMathics module.

To install in development mode (run code from the source tree):

::

   $ make develop


After installing inside Mathics you can load this using the
``LoadModule[]`` function.

Then to the function ``Pymathics\`Hello[]`` and the variable ``PyMathics\`$HelloUser`` will be available.

::

      $ mathicsscript
      In[1]:= LoadModule["pymathics.hello"]
      Out[1]= pymathics.hello

      In[2]:= PyMathics`Hello["World"]
      Out[2]:= Hello, World!

      In[3]:= PyMathics`$HelloUser
      Out[3]:= $your-login-name$
