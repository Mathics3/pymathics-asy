# -*- coding: utf-8 -*-


import sys


# from helper import session, check_evaluation
# It would be nice to load this code from .helper, but
# for some reason I can make the relative load works...

import time
from mathics.core.parser import parse, MathicsSingleLineFeeder
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression, String
from mathics.session import MathicsSession
import mathics

import pymathics.asy as asylib


session = MathicsSession()


def test_asymptote_cmd():
    from subprocess import DEVNULL, STDOUT, check_call
    import tempfile
    res = check_call(['asy', '--version'], stdout=DEVNULL, stderr=DEVNULL)
    assert res == 0

def check_evaluation(str_expr: str, str_expected: str, message=""):
    """Helper function to test that a WL expression against
    its results"""
    result = session.evaluate(str_expr)
    expected = session.evaluate(str_expected)

    print(time.asctime())
    print(message)
    if message:
        if result == (expected, message):
            print("   ->OK\n")
        else:
            print("    unexpected result =", result)
    else:
        if result == expected:
            print("   ->OK\n")
        else:
            print("    unexpected result =", result)
        


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
               #"test.jpg"
]

def format_tests(str_expr: str, str_expected: str, message=""):
    check_evaluation(str_expr, str_expected, message)


test_inputs = [ ('LoadModule["pymathics.asy"]', '"pymathics.asy"') ] +\
    [  ('Export[$TemporaryDirectory<>"/"<>"'+ filename +'", '+ test + ']',
       f'$TemporaryDirectory <> "/" <> "{filename}"')
        for test in tests
        for filename in fileformats
    ]

for expr, expected in test_inputs:
    print("\n", 80*"*")
    print("Expr:", expr)
    print("Expected:", expected)
    check_evaluation(expr, expected)
    print(80*"*","\n")
    
