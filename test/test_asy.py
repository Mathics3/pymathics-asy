

import os

def test_asycmd():
    try:
        assert os.system("asy -version") == 0
    except:
        assert False
