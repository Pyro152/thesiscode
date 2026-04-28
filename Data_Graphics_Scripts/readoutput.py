import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------
# Load GEOS-Chem file
# ---------------------------------------
ds = xr.open_dataset("/home/bryan/Desktop/baseline/2027/GEOSChem.SpeciesConc.20270601_0000z.nc4")

# Species field (restart or diagnostic)
var = ds["SpeciesConcVV_ALUMINA"].isel(time=0)  # or SpeciesRst_O3

# ---------------------------------------
# Hybrid coefficients (1D)
# ---------------------------------------
A = ds["lev"]      # mid-level A coefficients (Pa / P0)
B = ds["hybm"]      # mid-level B coefficients (unitless)
P0 = ds["P0"]       # reference pressure (Pa)

# ---------------------------------------
# Compute pressure for stratospheric levels
# For levels where B ~ 0, p ≈ A * P0
# ---------------------------------------
p_full = A*P0   # convert to hPa

# Keep only stratosphere (p < 100 hPa)
strat_mask = p_full < 1000.0

p_strat = p_full[strat_mask]
var_strat = var.isel(lev=strat_mask)

# ---------------------------------------
# Zonal mean
# ---------------------------------------
zm = var_strat.mean(dim="lon")

# ---------------------------------------
# Stratopause annotation (~1 hPa)
# ---------------------------------------
stratopause_p = 1.0  # climatological

# ---------------------------------------
# Plot
# ---------------------------------------
fig, ax = plt.subplots(figsize=(8,6))

cf = ax.contourf(
    zm["lat"],
    p_strat,
    zm,
    levels=30,
    cmap="viridis"
)

ax.set_yscale("log")
ax.invert_yaxis()
ax.set_ylabel("Pressure (hPa)")
ax.set_xlabel("Latitude")
plt.colorbar(cf, label="O3 (mol/mol)")

# Annotate stratopause
ax.axhline(stratopause_p, color="red", lw=2, ls="--", label="Stratopause (~1 hPa)")

ax.legend(loc="upper right")
plt.title("Stratospheric Zonal Mean Ozone (Hybrid Levels → Pressure)")
plt.tight_layout()
plt.show()
