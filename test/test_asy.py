# -*- coding: utf-8 -*-


import os
import pymathics.asy


import shutil

try:
    asy_path = shutil.which("asy")
    print("asy found in ", asy_path)
except:
    print("asy path couldn't be found. Set to asy")
    asy_path = "asy"


def test_asycmd():
    try:
        assert os.system(asy_path + " -version") == 0
    except:
        print("path=", asy_path)
        assert False
