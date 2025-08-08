import jax.numpy as np


def conv(w, x):
    return np.convolve(w, x)


def deconv(w, x):
    pass
