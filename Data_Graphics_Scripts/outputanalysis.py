import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import datetime

MW_air = 28.97e-3
MW_alumina = 101.96e-3
g = 9.80665

def burden_from_file(fname):
    ds = xr.open_dataset(fname)

    vmr = ds["SpeciesConcVV_ALUMINA"].isel(time=0)  # (lev, lat, lon)

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

    return vmr_strat #species_mass.sum().item()





# ------------------------------------------------------
# Scenario A (your original tutorial2/myemit_prod)
# ------------------------------------------------------
files_A = []
for year, month in [(2020, m) for m in range(7,13)] + \
                   [(2021, m) for m in range(1,7)]:
    yyyymm = f"{year}{month:02d}"
    fname = f"/home/bryan/tutorial2/myemit_prod/OutputDir/GEOSChem.SpeciesConc.{yyyymm}01_0000z.nc4"
    files_A.append(fname)

burdens_A = [burden_from_file(f) for f in files_A]


# ------------------------------------------------------
# Scenario B (your new barkers_prod directory)
# ------------------------------------------------------
files_B = []
for year, month in [(2020, m) for m in range(7,13)] + \
                   [(2021, m) for m in range(1,7)]:
    yyyymm = f"{year}{month:02d}"
    fname = f"/home/bryan/tutorial2/barkers_prod/OutputDir/GEOSChem.SpeciesConc.{yyyymm}01_0000z.nc4"
    files_B.append(fname)

burdens_B = [burden_from_file(f) for f in files_B]


dates = []#[datetime.datetime(2020, 7, 1)]
for year, month in [(2020, m) for m in range(7,13)] + \
                   [(2021, m) for m in range(1,7)]:# + \
                   #[(2028, m) for m in range(1,13)]:
    dates.append(datetime.datetime(year, month, 15))

t_months = np.arange(len(dates))  # 0,1,2,...,11



A = np.array(burdens_A)
B = np.array(burdens_B)

diff = B - A
pct_diff = 100 * diff / A
pct_diff = np.where(A == 0, np.nan, pct_diff)



#both together
plt.figure(figsize=(10,5))
plt.plot(dates, A, 'o-', label='Scenario A (myemit_prod)')
plt.plot(dates, B, 'o-', label='Scenario B (barkers_prod)')

plt.rcParams.update({
    "font.size": 24,          # doubles typical default (~12)
    "axes.titlesize": 28,     # title slightly larger
    "axes.labelsize": 24,     # axis labels
    "xtick.labelsize": 20,    # tick labels
    "ytick.labelsize": 20
})

plt.title("Monthly Stratospheric Alumina Burden")
plt.ylabel("Burden (kg)")
plt.xlabel("Date")
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.show()


#abs diff
plt.figure(figsize=(10,5))
plt.plot(dates, diff, 'o-', color='purple')

plt.title("Absolute Difference in Burden (Scenario B − Scenario A)")
plt.ylabel("Difference (kg)")
plt.xlabel("Date")
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()


#percent diff
plt.figure(figsize=(10,5))
plt.plot(dates, pct_diff, 'o-', color='black')

#plt.title("Percent Difference in Burden (Barker − New")
plt.ylabel("Percent Difference (%)")
plt.xlabel("Date")
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()



#combined diff-percent diff plot
fig, ax1 = plt.subplots(figsize=(10,5))

ax1.plot(dates, diff, 'o-', color='purple')
ax1.set_ylabel("Absolute Difference (kg)", color='purple')
ax1.tick_params(axis='y', labelcolor='purple')

ax2 = ax1.twinx()
ax2.plot(dates, pct_diff, 's--', color='green')
ax2.set_ylabel("Percent Difference (%)", color='green')
ax2.tick_params(axis='y', labelcolor='green')

plt.title("Difference and Percent Difference Between Scenarios")
plt.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.show()

