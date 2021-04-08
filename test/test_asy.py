# -*- coding: utf-8 -*-


import os
import pymathics.asy

def test_asycmd():
    try:
        assert os.system(pymathics.asy.asy_path +" -version") == 0
    except:
        print("path=", pymathics.asy.asy_path)
        assert False
