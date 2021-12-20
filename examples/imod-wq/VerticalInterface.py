"""
Vertical Interface
==================

This 2D examples demonstrates the rotation of an initially vertical interface
between fresh and salt water.

For a detailed description of this benchmark, see:

Bakker, M., Oude Essink, G. H. P., & Langevin, C. D. (2004).
The rotating movement of three immiscible fluids - A benchmark problem.
`Journal of Hydrology, 287` (1-4), 270-278.
https://doi.org/10.1016/j.jhydrol.2003.10.007
"""

# %%
# We'll start with the usual imports

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

import imod

# sphinx_gallery_thumbnail_number = -1

# %%
# Discretization
# --------------
#
# We'll start off by creating a model discretization, since
# this is a simple conceptual model.
# The model is a 2D cross-section, hence ``nrow = 1``.

nrow = 1
ncol = 80
nlay = 40

dz = 1.0  # 0.0125
dx = 1.0  # 0.0125
dy = -dx

# Defining tops and bottoms
top1D = xr.DataArray(
    np.arange(nlay * dz, 0.0, -dz), {"layer": np.arange(1, nlay + 1)}, ("layer")
)

bot = top1D - dz
top = nlay * dz

# %%
# Set up ibound, which sets where active cells are `(ibound = 1.0)`
bnd = xr.DataArray(
    data=np.full((nlay, nrow, ncol), 1.0),
    coords={
        "y": [0.5],
        "x": np.arange(0.5 * dx, dx * ncol, dx),
        "layer": np.arange(1, 1 + nlay),
        "dx": dx,
        "dy": dy,
    },
    dims=("layer", "y", "x"),
)

fig, ax = plt.subplots()
bnd.plot(y="layer", yincrease=False, ax=ax)

#%%
# Define the icbund, which sets which cells
# in the solute transport model are active, inactive or constant.
#
# We just go for active cells everywhere here
icbund = xr.full_like(bnd, 1)

# %%
# Boundary Conditions
# -------------------
#
# Set the constant heads by specifying a negative value in iboud,
# that is: ``bnd[index] = -1```

bnd[31, :, 0] = -1

fig, ax = plt.subplots()
bnd.plot(y="layer", yincrease=False, ax=ax)


# %%
# Define WEL data
weldata = pd.DataFrame()
weldata["x"] = np.full(1, 0.5 * dx)
weldata["y"] = np.full(1, 0.5)
weldata["q"] = 0.28512  # positive, so it's an injection well

# %%
# Initial Conditions
# ------------------
#
# Define the starting concentration

sconc = xr.DataArray(
    data=np.full((nlay, nrow, ncol), 0.0),
    coords={
        "y": [0.5],
        "x": np.arange(0.5 * dx, dx * ncol, dx),
        "layer": np.arange(1, nlay + 1),
    },
    dims=("layer", "y", "x"),
)

sconc[:, :, 41:80] = 35.0

# %%
# Build
# -----
#
# Finally, we build the model.

fig, ax = plt.subplots()
sconc.plot(y="layer", yincrease=False, ax=ax)

# Finally, we build the model
m = imod.wq.SeawatModel("VerticalInterface")
m["bas"] = imod.wq.BasicFlow(ibound=bnd, top=top, bottom=bot, starting_head=0.0)
m["lpf"] = imod.wq.LayerPropertyFlow(
    k_horizontal=86.4, k_vertical=86.4, specific_storage=0.0
)
m["btn"] = imod.wq.BasicTransport(
    icbund=icbund, starting_concentration=sconc, porosity=0.1
)
m["adv"] = imod.wq.AdvectionTVD(courant=1.0)
m["dsp"] = imod.wq.Dispersion(longitudinal=0.0, diffusion_coefficient=0.0)
m["vdf"] = imod.wq.VariableDensityFlow(density_concentration_slope=0.71)
m["wel"] = imod.wq.Well(
    id_name="wel", x=weldata["x"], y=weldata["y"], rate=weldata["q"]
)
m["pcg"] = imod.wq.PreconditionedConjugateGradientSolver(
    max_iter=150, inner_iter=30, hclose=0.0001, rclose=0.1, relax=0.98, damp=1.0
)
m["gcg"] = imod.wq.GeneralizedConjugateGradientSolver(
    max_iter=150,
    inner_iter=30,
    cclose=1.0e-6,
    preconditioner="mic",
    lump_dispersion=True,
)
m["oc"] = imod.wq.OutputControl(save_head_idf=True, save_concentration_idf=True)
m.time_discretization(times=["2000-01-01", "2000-01-02"])

# %%
# Now we write the model, including runfile:
modeldir = imod.util.temporary_directory()
m.write(modeldir, resultdir_is_workdir=True)

# %%
# Run
# ---
#
# You can run the model using the comand prompt and the iMOD-WQ executable.
# This is part of the iMOD v5 release, which can be downloaded here:
# https://oss.deltares.nl/web/imod/download-imod5 .
# This only works on Windows.

# %%
# Visualise results
# -----------------
#
# After succesfully running the model, you can
# plot results as follows:
#
# .. code:: python
#
#    head = imod.idf.open(modeldir / "results/head/*.idf")
#
#    fig, ax = plt.subplots()
#    head.plot(yincrease=False, ax=ax)
#
#    conc = imod.idf.open(modeldir / "results/conc/*.idf")
#
#    fig, ax = plt.subplots()
#    conc.plot(levels=range(0, 35, 5), yincrease=False, ax=ax)
#


# %%
