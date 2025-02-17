import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from probnum import diffeq, filtsmooth
from probnum import random_variables as random_variables
from probnum import random_variables, statespace
from probnum._randomvariablelist import _RandomVariableList
from scipy.integrate import solve_bvp
from tqdm import tqdm

from bvps import problem_examples

bvp = problem_examples.pendulum()
initial_grid = np.linspace(bvp.t0, bvp.tmax, 15)
initial_guess = np.zeros((2, len(initial_grid)))
refsol = solve_bvp(bvp.f, bvp.scipy_bc, initial_grid, initial_guess, tol=1e-12)


x = np.linspace(bvp.t0, bvp.tmax, 150)
y = refsol.sol(x)

path = "./data/firstpage_plot/"
np.save(path + "x.npy", x)
np.save(path + "y.npy", y)


plt.plot(x, y.T)
plt.annotate(
    "hi",
    (np.pi / 4.0 - 0.4, refsol.sol(np.pi / 4)[0]),
    bbox={"facecolor": "white", "edgecolor": "white", "pad": 10},
    zorder=10,
)
plt.annotate(
    "With BC",
    (0.5, refsol.sol(0.5)[1]),
    bbox={"facecolor": "white", "edgecolor": "white", "pad": 0},
    zorder=10,
)
plt.show()
