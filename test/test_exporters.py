# -*- coding: utf-8 -*-


import sys
import pytest

#from .helper import session, check_evaluation
# It would be nice to load this code from .helper, but
# for some reason I can make the relative load works...

import time
from mathics.core.parser import parse, MathicsSingleLineFeeder
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.session import MathicsSession

session = MathicsSession(add_builtin=True, catch_interrupt=False)
session.evaluate('LoadModule["pymathics.asy"]')

def check_evaluation(str_expr: str, str_expected: str, message=""):
    """Helper function to test that a WL expression against
    its results"""
    result = session.evaluate(str_expr)
    expected = session.evaluate(str_expected)

    print(time.asctime())
    print(message)
    if message:
        assert result == expected, message
    else:
        assert result == expected
###########################


tests = ('MatrixForm[{{a,n},{c,d}}]; a+b',
         'Integrate[f[x],x]',
         'Evaluate[Plot[Cos[x],{x,0,20}]]',
         'Evaluate[Plot3D[Cos[x*y],{x,-1,1},{y,-1,1}]]',
         'Evaluate[DensityPlot[Cos[x*y],{x,-1,1},{y,-1,1}]]',
)

@pytest.mark.parametrize(
    "str_expr, str_expected",
    [
      (f'Export[$TemporaryDirectory<>"/"<>"{filename}", {test}]',
       f'$TemporaryDirectory <> "/" <> "{filename}"')
        for test in tests
        for filename in ("test.pdf", "test.png", "test.jpg", "test.svg")
    ]
)
def test_evaluation(str_expr: str, str_expected: str, message=""):
    check_evaluation(str_expr, str_expected, message)

