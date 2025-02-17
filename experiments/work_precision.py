"""Try out probsolve_bvp."""
import time

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from probnum import diffeq, filtsmooth
from probnum import random_variables as random_variables
from probnum import random_variables, statespace
from probnum._randomvariablelist import _RandomVariableList
from probnumeval import timeseries
from scipy.integrate import solve_bvp
from tqdm import tqdm

from bvps import bridges, bvp_solver, problem_examples

# Easy aliases
anees = timeseries.anees
rmse = timeseries.root_mean_square_error


TMAX = 1.0
XI = 0.001


bvp = problem_examples.bratus_second_order(tmax=1.0)
bvp1st = bvp.to_first_order()

TOL = 1e-5

initial_grid = np.linspace(bvp.t0, bvp.tmax, 300)
initial_guess = np.ones((bvp1st.dimension, len(initial_grid)))

refsol = solve_bvp(bvp1st.f, bvp1st.scipy_bc, initial_grid, initial_guess, tol=TOL)
refsol_fine = solve_bvp(
    bvp1st.f, bvp1st.scipy_bc, initial_grid, initial_guess, tol=1e-10
)
assert refsol_fine.success
bvp.solution = refsol_fine.sol

results = {}

testlocations = np.linspace(bvp.t0, bvp.tmax, 50)


for q in [3, 4, 5]:
    print()
    print()
    print("q", q)
    print()

    results[q] = {}

    ibm = statespace.IBM(
        ordint=q,
        spatialdim=1,
        forward_implementation="sqrt",
        backward_implementation="sqrt",
    )
    # ibm.equivalent_discretisation_preconditioned._proc_noise_cov_cholesky *= 1e5

    # initial_grid = np.linspace(bvp.t0, bvp.tmax, 2)

    # print(len(refsol.x))
    # reference_solution = lambda *args, **kwargs: refsol_fine.sol(*args, **kwargs)[
    #     0
    # ].T.reshape((-1, 1))
    # scipy_sol = lambda *args, **kwargs: refsol.sol(*args, **kwargs)[0].T.reshape(
    #     (-1, 1)
    # )

    # error = rmse(scipy_sol, reference_solution, testlocations)
    # print("Scipyerror:", error)

    evalgrid = np.linspace(bvp.t0, bvp.tmax, 250, endpoint=True)

    for tol_order in np.arange(1.0, 9.0):
        if q == 3:
            if tol_order > 7:
                tol_order = 7.0
        TOL = 10.0 ** (-tol_order)

        print("tol", TOL)
        solver = bvp_solver.BVPSolver.from_default_values_std_refinement(
            ibm, initial_sigma_squared=1e2, normalise_with_interval_size=False
        )
        initial_grid = np.linspace(bvp.t0, bvp.tmax, 3)
        initial_guess = np.ones((len(initial_grid), bvp.dimension))

        initial_posterior, sigma_squared = solver.compute_initialisation(
            bvp, initial_grid, initial_guess=initial_guess, use_bridge=True
        )

        solution_gen = solver.solution_generator(
            bvp,
            atol=TOL,
            rtol=TOL,
            initial_posterior=initial_posterior,
            maxit_ieks=5,
            maxit_em=1,
            yield_ieks_iterations=False,
        )

        start_time = time.time()
        for post, ssq in solution_gen:
            print(len(post.locations))
        end_time = time.time() - start_time
        solution = diffeq.KalmanODESolution(post)

        testlocations = np.linspace(bvp.t0, bvp.tmax)
        reference_solution = lambda *args, **kwargs: bvp.solution(*args, **kwargs)[
            0
        ].reshape((-1, 1))
        # plt.plot(testlocations, reference_solution(testlocations))
        # plt.plot(testlocations, solution(testlocations).mean[:, 0])
        # plt.show()
        solution_mean = (
            lambda *args, **kwargs: solution(*args, **kwargs)
            .mean[:, 0]
            .reshape((-1, 1))
        )

        print(ssq)
        chi2 = anees(solution, reference_solution, testlocations, damping=1e-30) / ssq

        initial_guess = np.ones((len(initial_grid), bvp1st.dimension)).T

        start_time_scipy = time.time()
        scipy_solution = solve_bvp(
            bvp1st.f, bvp1st.scipy_bc, initial_grid, initial_guess, tol=TOL
        )
        runtime_scipy = time.time() - start_time_scipy
        assert scipy_solution.success

        # How accurate would scipy be?
        scipy_sol_for_rmse = lambda *args: scipy_solution.sol(*args)[0][:, None]
        error_scipy = timeseries.root_mean_square_error(
            scipy_sol_for_rmse, reference_solution, testlocations
        )

        error = rmse(solution_mean, reference_solution, testlocations)
        results[q][TOL] = {}
        results[q][TOL]["chi2"] = chi2
        results[q][TOL]["error"] = error
        results[q][TOL]["N"] = len(solution.locations)
        results[q][TOL]["time"] = end_time
        results[q][TOL]["scipy_error"] = error_scipy
        results[q][TOL]["scipy_N"] = len(scipy_solution.x)
        results[q][TOL]["scipy_time"] = runtime_scipy

    print(chi2, error, end_time)
print(results)

import json

with open("./data/bratus_problem_work_precision.json", "w") as outfile:
    json.dump(results, outfile)
