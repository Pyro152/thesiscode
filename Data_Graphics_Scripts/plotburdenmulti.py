import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import datetime
from scipy.optimize import curve_fit

MW_air = 28.97e-3
MW_alumina = 101.96e-3
g = 9.80665

# ------------------------------------------------------
# Function to compute burden from a single file
# ------------------------------------------------------
def burden_from_file(fname):
    ds = xr.open_dataset(fname)

    vmr = ds["SpeciesConcVV_ALUMINA"].isel(time=0)

    A_mid = ds["hyam"]
    B_mid = ds["hybm"]
    A_int = ds["hyai"]
    B_int = ds["hybi"]
    P0 = ds["P0"].item()

    strat_mask = B_mid < 1e-3

    p_int = A_int.values * 100.0
    dp_full = p_int[:-1] - p_int[1:]
    dp = dp_full[strat_mask.values]

    area = ds["AREA"].values
    dp_3d = dp[:, None, None] * np.ones_like(area)[None, :, :]

    air_mass = (dp_3d / g) * area

    vmr_strat = vmr.sel(lev=strat_mask).values
    species_mass = air_mass * vmr_strat * (MW_alumina / MW_air)

    return species_mass.sum().item()


# ------------------------------------------------------
# Build list of dates (same for all simulations)
# ------------------------------------------------------
dates = []
for year, month in [(2026,m) for m in range(7,13)] + \
                   [(y,m) for y in range(2027,2036) for m in range(1,13)] + \
                   [(2036,m) for m in range(1,7)]:
    dates.append(datetime.datetime(year, month, 15))

t_months = np.arange(len(dates))






# ------------------------------------------------------
# Helper: compute burdens for a given simulation directory
# ------------------------------------------------------
def compute_burdens(sim_dir):
    files = []
    for year, month in [(2026,m) for m in range(7,13)] + \
                       [(y,m) for y in range(2027,2036) for m in range(1,13)] + \
                       [(2036,m) for m in range(1,7)]:

        yyyymm = f"{year}{month:02d}"
        fname = f"{sim_dir}/{year}/GEOSChem.SpeciesConc.{yyyymm}01_0000z.nc4"
        files.append(fname)

    burdens = []
    for f in files:
        print("Processing:", f)
        burdens.append(burden_from_file(f))

    return np.array(burdens)


# ------------------------------------------------------
# Define your three simulation directories
# ------------------------------------------------------
sim1 = "/home/bryan/Negishi_Downloads_March/OutputDir/prod_baseline"
sim2 = "/home/bryan/Negishi_Downloads_March/OutputDir/prod_hi_base"
sim3 = "/home/bryan/Negishi_Downloads_March/OutputDir/prod_newconst"

burden1 = compute_burdens(sim1)
burden2 = compute_burdens(sim2)
burden3 = compute_burdens(sim3)



# ------------------------------------------------------
# Fit exponential model to simulation 1 (optional)
# ------------------------------------------------------
def exp_model(t, B_inf, tau):
    return B_inf * (1 - np.exp(-t / tau))

p0 = [burden1.max(), 6.0]
params, cov = curve_fit(exp_model, t_months, burden1, p0=p0)
B_inf_fit, tau_fit = params

print(f"Fit for sim1: B_inf = {B_inf_fit:.3e} kg, tau = {tau_fit:.2f} months")


# ------------------------------------------------------
# Plot all three simulations
# ------------------------------------------------------
plt.figure(figsize=(12,6))

plt.rcParams.update({
        "font.size": 24,          # doubles typical default (~12)
        "axes.titlesize": 28,     # title slightly larger
        "axes.labelsize": 24,     # axis labels
        "xtick.labelsize": 20,    # tick labels
        "ytick.labelsize": 20
    })

plt.plot(dates, burden1, 'o-', label="Scenario 1")
plt.plot(dates, burden2, 's-', label="Scenario 2")
plt.plot(dates, burden3, '^-', label="Scenario 3")

#plt.title("Stratospheric Alumina Burden Comparison Across Simulations")
plt.ylabel("Burden (kg)")
plt.xlabel("Date")
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.show()


# ------------------------------------------------------
# Compute percent differences relative to simulation 1
# ------------------------------------------------------
pct2 = 100 * (burden2 - burden1) / burden1
pct3 = 100 * (burden3 - burden1) / burden1

# ------------------------------------------------------
# Two-panel figure: burdens + percent differences
# ------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12,10), sharex=True)

plt.rcParams.update({
        "font.size": 24,          # doubles typical default (~12)
        "axes.titlesize": 28,     # title slightly larger
        "axes.labelsize": 24,     # axis labels
        "xtick.labelsize": 20,    # tick labels
        "ytick.labelsize": 20
    })

# --- Top panel: burdens (semilog optional) ---
ax1.plot(dates, burden1, 'o-', label="Simulation 1 (baseline)")
ax1.plot(dates, burden2, 's-', label="Simulation 2")
ax1.plot(dates, burden3, '^-', label="Simulation 3")

ax1.set_ylabel("Burden (kg)")
ax1.set_title("Stratospheric Ozone Burden Across Simulations")
ax1.grid(True, linestyle='--', alpha=0.5)
ax1.legend()

# Uncomment for semilog-y:
# ax1.set_yscale('log')

# --- Bottom panel: percent differences ---
ax2.plot(dates, pct2, 's-', label="Sim2 vs Sim1")
ax2.plot(dates, pct3, '^-', label="Sim3 vs Sim1")

ax2.axhline(0, color='k', linewidth=1)
ax2.set_ylabel("Percent Difference (%)")
ax2.set_xlabel("Date")
ax2.set_title("Percent Difference Relative to Baseline")
ax2.grid(True, linestyle='--', alpha=0.5)
ax2.legend()

plt.tight_layout()
plt.show()

