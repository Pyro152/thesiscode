import xarray as xr
import numpy as np

MW_air = 28.97e-3
MW_alumina = 101.96e-3
g = 9.80665

def burden_from_file(fname):
    ds = xr.open_dataset(fname)

    vmr = ds["SpeciesConcVV_O3"].isel(time=0)  # (lev, lat, lon)

    # Midpoint hybrid coefficients (47)
    A_mid = ds["hyam"]   # hPa
    B_mid = ds["hybm"]   # unitless

    # Interface hybrid coefficients (48)
    A_int = ds["hyai"]   # hPa
    B_int = ds["hybi"]   # unitless

    # Reference pressure (hPa)
    P0 = ds["P0"].item()

    # -------------------------------
    # 1. Stratospheric mask (midpoints)
    # -------------------------------
    strat_mask = B_mid < 1e-3   # length 47

    # -------------------------------
    # 2. Compute pressure at interfaces (Pa)
    #    p_i = A_i * 100  (because B_i ≈ 0 in stratosphere)
    # -------------------------------
    p_int = A_int.values * 100.0   # Pa

    # Pressure thickness Δp for 47 layers
    dp_full = p_int[:-1] - p_int[1:]   # length 47

    # Apply midpoint mask to Δp
    dp = dp_full[strat_mask.values]    # length Nstrat

    # -------------------------------
    # 3. Expand dp to 3D
    # -------------------------------
    area = ds["AREA"].values  # (lat, lon)
    dp_3d = dp[:, None, None] * np.ones_like(area)[None, :, :]

    # -------------------------------
    # 4. Air mass (kg)
    # -------------------------------
    air_mass = (dp_3d / g) * area

    # -------------------------------
    # 5. Species mass (kg)
    # -------------------------------
    vmr_strat = vmr.sel(lev=strat_mask).values
    species_mass = air_mass * vmr_strat * (MW_alumina / MW_air)

    return species_mass.sum().item()



# ------------------------------------------------------
# Loop over 12 months: 2020-07 → 2021-06
# ------------------------------------------------------
files = []
for year, month in [(2026, m) for m in range(7,13)] + \
                   [(y,m) for y in range(2027,2036) for m in range(1,13)] + \
                   [(2036,m) for m in range(1,7)]:#+[(2036,6)]:

    yyyymm = f"{year}{month:02d}"
    fname = f"/home/bryan/Negishi_Downloads_March/OutputDir/prod_baseline/{year}/GEOSChem.SpeciesConc.{yyyymm}01_0000z.nc4"
    files.append(fname)

monthly_burdens = []
for f in files:
    print("Processing:", f)
    monthly_burdens.append(burden_from_file(f))

cumulative_burden = sum(monthly_burdens)

print("\nMonthly burdens (kg):")
for f, b in zip(files, monthly_burdens):
    print(f"{f}: {b:.3e} kg")

print("\nCumulative burden (kg) July 2020 → June 2021:")
print(f"{cumulative_burden:.3e} kg")

from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import datetime

# ----------------------------------------------------
# Build time axis in months since start
# ----------------------------------------------------
dates = []#[datetime.datetime(2020, 7, 1)]
for year, month in [(2026,m) for m in range(7,13)] + \
                   [(y,m) for y in range(2027,2036) for m in range(1,13)] + \
                   [(2036,m) for m in range(1,7)]:#+[(2036,6)]:
    dates.append(datetime.datetime(year, month, 15))

t_months = np.arange(len(dates))  # 0,1,2,...,11

burdens = np.array(monthly_burdens)

# ----------------------------------------------------
# Exponential approach-to-equilibrium model
# ----------------------------------------------------
def exp_model(t, B_inf, tau):
    return B_inf * (1 - np.exp(-t / tau))

# Initial guesses
p0 = [burdens.max(), 6.0]  # guess equilibrium ~ max, tau ~ 6 months

# Fit
params, cov = curve_fit(exp_model, t_months, burdens, p0=p0)
B_inf_fit, tau_fit = params

print(f"Fitted equilibrium burden B_inf = {B_inf_fit:.3e} kg")
print(f"Fitted lifetime tau = {tau_fit:.2f} months")
print(f"95% equilibrium time ≈ {3*tau_fit:.1f} months")

# ----------------------------------------------------
# Plot fit vs data
# ----------------------------------------------------
t_fine = np.linspace(0, len(t_months)-1, 200)
fit_curve = exp_model(t_fine, B_inf_fit, tau_fit)

plt.figure(figsize=(10,5))
plt.plot(dates, burdens, 'o', label='Monthly burden')
#plt.plot([dates[0] + datetime.timedelta(days=30*x) for x in t_fine],
#         fit_curve, '-', label='Exponential fit')

plt.title("Stratospheric Ozone Burden and Exponential Fit")
plt.ylabel("Burden (kg)")
plt.xlabel("Date")
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.show()
