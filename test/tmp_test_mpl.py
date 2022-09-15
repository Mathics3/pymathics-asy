# -*- coding: utf-8 -*-

try:
    import matplotlib.pyplot as plt

    plt.plot([1, 2, 3], [1, 2, 3])
    print("OK")
except:
    print("mpl failed")
