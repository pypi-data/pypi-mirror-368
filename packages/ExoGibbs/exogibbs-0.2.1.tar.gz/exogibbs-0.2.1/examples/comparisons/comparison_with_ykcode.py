"""
Validation of Gibbs Minimization Against ykawashima's B4 code
============================================================

This example demonstrates and validates the ExoGibbs thermochemical equilibrium
solver against the code by ykawashima when she was at B4.

"""

from exogibbs.optimize.minimize import minimize_gibbs
from exogibbs.optimize.core import compute_ln_normalized_pressure
from exogibbs.equilibrium.gibbs import extract_and_pad_gibbs_data
from exogibbs.equilibrium.gibbs import interpolate_hvector_all
from exogibbs.io.load_data import get_data_filepath
from exogibbs.io.load_data import load_formula_matrix
from exogibbs.io.load_data import DEFAULT_JANAF_GIBBS_MATRICES
from exogibbs.io.load_data import NUMBER_OF_SPECIES_SAMPLE
import numpy as np
import pandas as pd
from jax import jacrev
import jax.numpy as jnp

from jax import config

config.update("jax_enable_x64", True)

##############################################################################
# Setup Test System and Parameters
# ---------------------------------
# We initialize the analytical H system and define the thermochemical
# equilibrium problem parameters.


# Define stoichiometric constraint matrix
formula_matrix = load_formula_matrix()
# check if the formula matrix is full raw rank
rank = np.linalg.matrix_rank(formula_matrix)
print("formula matrix is row-full rank",rank == formula_matrix.shape[0])

# Thermodynamic conditions
temperature = 500.0  # K
P = 10.0  # bar
Pref = 1.0  # bar, reference pressure
ln_normalized_pressure = compute_ln_normalized_pressure(P, Pref)

# Initial guess for log number densities
ln_nk = jnp.zeros(formula_matrix.shape[1])  # log(n_species)  
ln_ntot = 0.0  # log(total number density)

# Element abundance constraint
npath = get_data_filepath(NUMBER_OF_SPECIES_SAMPLE)
number_of_species_init = pd.read_csv(npath, header=None, sep=",").values[0]
b_element_vector = formula_matrix @ number_of_species_init

# Gibbs matrix
ref = pd.read_csv("yk.list", header=None, sep=",").values[0]
print("ref", ref.shape)
path = get_data_filepath(DEFAULT_JANAF_GIBBS_MATRICES)
gibbs_matrices = np.load(path, allow_pickle=True)["arr_0"].item()
molecules, T_table, mu_table, grid_lens = extract_and_pad_gibbs_data(gibbs_matrices)


def hvector_func(temperature):
    return interpolate_hvector_all(temperature, T_table, mu_table)


# Convergence criteria
epsilon_crit = 1e-11
max_iter = 1000

##############################################################################
# Single-Point Equilibrium Validation
# ------------------------------------
# First, we solve for equilibrium at a single temperature and pressure point
# using both the core and main minimize_gibbs functions.

# Run Gibbs minimization using core function (returns iteration count)

ln_nk_result = minimize_gibbs(
    temperature,
    ln_normalized_pressure,
    b_element_vector,
    ln_nk,
    ln_ntot,
    formula_matrix,
    hvector_func,
    epsilon_crit=epsilon_crit,
    max_iter=max_iter,
)
nk_result = jnp.exp(ln_nk_result)
print("nk_result", nk_result)

# load yk's results for 10 bar
dat = np.loadtxt("p10.txt", delimiter=",")
print("dat", dat)

mask = dat > 1.e-14
mask_nk_result = nk_result[mask]
mask_dat = dat[mask]

res = mask_nk_result/mask_dat - 1.0
print(res,"diff for n>1.e-14")
assert np.max(np.abs(res)) < 0.051
# 8/9/2025
#[-0.00163185 -0.00163185  0.02571018 -0.00203837 -0.05069541 -0.00163185
# -0.00481986 -0.00420364 -0.00161074 -0.00163182 -0.00163185 -0.00163183
# -0.00163184 -0.00163178 -0.00163185 -0.00163184]

import matplotlib.pyplot as plt
plt.plot(nk_result, "+", label="ExoGibbs")
plt.plot(dat, ".", alpha=0.5, label="yk B4 code")
plt.xlabel("Species Index")
plt.ylabel("Number (log scale)")
plt.yscale("log")
plt.legend()
plt.grid()
plt.show()


