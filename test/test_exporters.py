# -*- coding: utf-8 -*-


import sys
import pytest

# from helper import session, check_evaluation
# It would be nice to load this code from .helper, but
# for some reason I can make the relative load works...

# import time
from mathics.session import MathicsSession


session = MathicsSession()


def test_asymptote_cmd():
    from subprocess import DEVNULL, STDOUT, check_call
    res = check_call(['asy', '--version'], stdout=DEVNULL, stderr=DEVNULL)
    assert res == 0

def check_evaluation(str_expr: str, str_expected: str, message=""):
    """Helper function to test that a WL expression against
    its results"""
    result = session.evaluate(str_expr)
    expected = session.evaluate(str_expected)

#    print(time.asctime())
#   print(message)
    if message:
        assert result == expected, message
    else:
        assert result == expected


tests = ['A',
         'MatrixForm[{{a,n},{c,d}}]; a+b',
         'Integrate[f[x],x]',
         'Evaluate[Plot[Cos[x],{x,0,20}]]',
#         'Evaluate[Plot3D[Cos[x*y],{x,-1,1},{y,-1,1}]]',
         'Evaluate[DensityPlot[Cos[x*y],{x,-1,1},{y,-1,1}]]',
]

fileformats = ["test.pdf", 
               "test.svg", 
               "test.png", 
#               "test.jpg"
]

@pytest.mark.parametrize(
    "str_expr, str_expected",
    [ ('LoadModule["pymathics.asy"]', '"pymathics.asy"') ] +\
    [  ('Export[$TemporaryDirectory<>"/"<>"'+ filename +'", '+ test + ']',
       f'$TemporaryDirectory <> "/" <> "{filename}"')
        for test in tests
        for filename in fileformats
    ]
)
def test_evaluation(str_expr: str, str_expected: str, message=""):
    check_evaluation(str_expr, str_expected, message)


