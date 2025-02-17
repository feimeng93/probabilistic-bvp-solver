"""Initialise a BVP solver."""
import numpy as np
import scipy.linalg
from probnum import diffeq, filtsmooth, problems, random_variables, statespace, utils
from probnum._randomvariablelist import _RandomVariableList

from .kalman import MyIteratedDiscreteComponent, MyKalman
from .mesh import *
from .ode_measmods import from_ode, from_second_order_ode
from .problems import SecondOrderBoundaryValueProblem
from .stopcrit import ConstantStopping, MyStoppingCriterion

# __all__ = ["bvp_initialise", "bvp_initialise_ode", "bvp_initialise_guesses"]


# def bvp_initialise(
#     bvp,
#     bridge_prior,
#     initial_grid,
#     initial_guess_vector=None,
#     initial_guess_function=None,
# ):
#     return bvp_initialise_ode(bvp, bridge_prior, initial_grid)


def bvp_initialise_ode(bvp, bridge_prior, initial_grid, initrv):

    if isinstance(bvp, SecondOrderBoundaryValueProblem):
        measmod = from_second_order_ode(bvp, bridge_prior)

        bvp_dim = len(bvp.R.T) // 2

    else:
        measmod = from_ode(bvp, bridge_prior)
        bvp_dim = len(bvp.R.T)

    # rv = random_variables.Normal(
    #     np.zeros(bridge_prior.dimension), 1e5 * np.eye(bridge_prior.dimension)
    # )
    # initrv = bridge_prior.initialise_boundary_conditions(rv)

    kalman = MyKalman(
        dynamics_model=bridge_prior, measurement_model=measmod, initrv=initrv
    )

    grid = initial_grid

    # Initial solve
    data = np.zeros((len(grid), bvp_dim))
    # stopcrit_ieks = ConstantStopping(maxit=10)

    # kalman_posterior = kalman.iterated_filtsmooth(
    #     dataset=data, times=grid, measmodL=None, measmodR=None, stopcrit=stopcrit_ieks
    # )

    posterior = kalman.filtsmooth(dataset=data, times=grid)
    sigma_squared = kalman.ssq
    return posterior, sigma_squared


def bvp_initialise_guesses(bvp, bridge_prior, initial_grid, initial_guesses, initrv):

    d = len(initial_guesses[0])
    measmod = statespace.DiscreteLTIGaussian(
        state_trans_mat=bridge_prior.proj2coord(0),
        shift_vec=np.zeros(d),
        proc_noise_cov_mat=1e-6 * np.eye(d),
        proc_noise_cov_cholesky=1e-3 * np.eye(d),
    )

    # rv = random_variables.Normal(
    #     np.ones(bridge_prior.dimension), 1e2 * np.eye(bridge_prior.dimension)
    # )

    kalman = MyKalman(
        dynamics_model=bridge_prior, measurement_model=measmod, initrv=initrv
    )

    # Initial solve
    grid = initial_grid
    data = initial_guesses

    posterior = kalman.filtsmooth(dataset=data, times=grid)
    sigma_squared = kalman.ssq
    return posterior, sigma_squared
