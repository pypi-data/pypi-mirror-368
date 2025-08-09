import numpy as np


def next_pow2(x: int):
    n = np.log2(x)
    return 2 ** (np.floor(n) + 1)