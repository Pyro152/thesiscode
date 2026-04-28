import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------
# Input files
# ---------------------------------------
file1 = "/home/bryan/Negishi_Downloads_March/OutputDir/prod_baseline/2036/GEOSChem.SpeciesConc.20360601_0000z.nc4"
file2 = "/home/bryan/Negishi_Downloads_March/OutputDir/prod_newconst/2036/GEOSChem.SpeciesConc.20360601_0000z.nc4"
file3='/home/bryan/tutorial2/myemit_prod/Restarts/GEOSChem.Restart.20210601_0000z.nc4'

# Species name
species_name = "SpeciesConcVV_ALUMINA"   # or any other species

# ---------------------------------------
# Function to load and process one file
# ---------------------------------------
def load_strat_zm(ncfile, species_name):
    ds = xr.open_dataset(ncfile)

    # Species field (take first time)
    var = ds[species_name].isel(time=0)

    # Hybrid coefficients
    A = ds["lev"]     # A coefficients (Pa/P0)
    B = ds["hybm"]    # B coefficients (unitless)
    P0 = ds["P0"]     # reference pressure (Pa)

    # Pressure (Pa → hPa)
    p_full = (A * P0)

    # Keep only stratosphere (p < 100 hPa)
    strat_mask = p_full < 1000.0

    p_strat = p_full[strat_mask]
    var_strat = var.isel(lev=strat_mask)

    # Zonal mean
    zm = var_strat.mean(dim="lon")

    return zm, p_strat, ds["lat"]

# ---------------------------------------
# Load both files
# ---------------------------------------
zm1, p1, lat1 = load_strat_zm(file1, species_name)
zm2, p2, lat2 = load_strat_zm(file2, species_name)

#find tropopause
ts=xr.open_dataset(file3)
trop_lev = ts["Met_TropLev"].isel(time=0).astype(int)   # dims: lat, lon

# Compute full pressure (Pa → hPa)
p_full = (ts["lev"] * ts["P0"])    # dims: lev

# Convert tropopause level index → pressure
# trop_lev is 2D (lat, lon), so we index p_full for each grid cell
tropopause_p = p_full.isel(lev=trop_lev)

# Zonal mean tropopause pressure (hPa)
tropopause_zm = tropopause_p.mean(dim="lon")


# ---------------------------------------
# Plotting
# ---------------------------------------

plt.rcParams.update({
    "font.size": 24,          # doubles typical default (~12)
    "axes.titlesize": 28,     # title slightly larger
    "axes.labelsize": 24,     # axis labels
    "xtick.labelsize": 20,    # tick labels
    "ytick.labelsize": 20
})

fig, axes = plt.subplots(1, 2, figsize=(14, 6),constrained_layout=True, sharey=True)




# Shared color scale
vmin = min(zm1.min(), zm2.min())
vmax = max(zm1.max(), zm2.max())

# Panel 1
cf1 = axes[0].contourf(
    lat1, p1, zm1,
    levels=30, cmap="BuGn",
    vmin=vmin, vmax=vmax
)
axes[0].set_title("New Input")
axes[0].set_xlabel("Latitude")

# Panel 2
cf2 = axes[1].contourf(
    lat2, p2, zm2,
    levels=30, cmap="BuGn",
    vmin=vmin, vmax=vmax
)
axes[1].set_title("Barker Input")
axes[1].set_xlabel("Latitude (degrees)")

# Pressure axis
axes[0].set_yscale("log")
axes[0].invert_yaxis()
axes[0].set_ylabel("Pressure (hPa)")

# Stratopause annotation (~1 hPa)
for ax in axes:
    ax.axhline(1.0, color="red", lw=2, ls="--")
    ax.plot(lat1, tropopause_zm, color="red", lw=2, ls="--")



# Colorbar
plt.subplots_adjust(right=0.9)
cbar = fig.colorbar(cf1, ax=axes.ravel().tolist(),location='right', label="Alumina (pptv)")

#plt.suptitle("Stratospheric Zonal Mean Ozone (Two GEOS-Chem Files)")
#plt.tight_layout()
plt.show()





##############Difference plot#############

# Absolute difference
diff = zm2 - zm1

# Symmetric percent difference
percent_diff = diff #100 * diff / (0.5 * zm2)


# Symmetric color limits around zero
absmax = np.nanmax(np.abs(percent_diff))

fig, ax = plt.subplots(figsize=(7,6))

cf = ax.contourf(
    lat1,
    p1,
    percent_diff,
    levels=30,
    cmap="bwr",
    vmin=-absmax,
    vmax=absmax
)

ax.set_yscale("log")
ax.invert_yaxis()
ax.set_ylabel("Pressure (hPa)")
ax.set_xlabel("Latitude (degrees)")

plt.colorbar(cf, label="Difference (file2 − file1)")

# Add stratopause and tropopause lines if desired
ax.axhline(1.0, color="red", lw=2, ls="--")
ax.plot(lat1, tropopause_zm, color="black", lw=2, ls="--")

plt.title("Zonal Mean Difference (File2 − File1)")
plt.tight_layout()
plt.show()





################big plot##########################


file1a = "/home/bryan/tutorial2/myemit_prod/OutputDir/GEOSChem.SpeciesConc.20200901_0000z.nc4"
file1b = "/home/bryan/tutorial2/barkers_prod/OutputDir/GEOSChem.SpeciesConc.20200901_0000z.nc4"
file2a = "/home/bryan/tutorial2/myemit_prod/OutputDir/GEOSChem.SpeciesConc.20201201_0000z.nc4"
file2b = "/home/bryan/tutorial2/barkers_prod/OutputDir/GEOSChem.SpeciesConc.20201201_0000z.nc4"
file3a = "/home/bryan/tutorial2/myemit_prod/OutputDir/GEOSChem.SpeciesConc.20210301_0000z.nc4"
file3b = "/home/bryan/tutorial2/barkers_prod/OutputDir/GEOSChem.SpeciesConc.20210301_0000z.nc4"
file4a = "/home/bryan/tutorial2/myemit_prod/OutputDir/GEOSChem.SpeciesConc.20210601_0000z.nc4"
file4b = "/home/bryan/tutorial2/barkers_prod/OutputDir/GEOSChem.SpeciesConc.20210601_0000z.nc4"


# ---------------------------------------
# List of file pairs to compare
# ---------------------------------------
file_pairs = [
    (file1a, file1b),
    (file2a, file2b),
    (file3a, file3b),
    (file4a, file4b)
]

titles = [
    "September 2020",
    "December 2020",
    "March 2021",
    "June 2021"
]

# ---------------------------------------
# Create 2×2 figure
# ---------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 12),constrained_layout=True, sharey=True)

# ---------------------------------------
# Loop through file pairs
# ---------------------------------------
for idx, ((fa, fb), title) in enumerate(zip(file_pairs, titles)):
    row = idx // 2
    col = idx % 2
    ax = axes[row, col]

    # Load zonal means
    zm1, p, lat = load_strat_zm(fa, species_name)
    zm2, _, _   = load_strat_zm(fb, species_name)

    # Symmetric percent difference
    diff = zm2 - zm1
    percent_diff = diff*1e12#100 * diff / (0.5 * (zm2 + zm1) + 1e-20)

    # Symmetric color limits
    absmax = float(np.nanmax(np.abs(percent_diff)))

    # Plot
    cf = ax.contourf(
        lat,
        p,
        percent_diff,
        levels=30,
        cmap="bwr",
        vmin=-absmax,
        vmax=absmax
    )

    ax.set_yscale("log")
    
    ax.set_title(title)
    ax.set_xlabel("Latitude (degrees)")
    if col == 0:
        ax.set_ylabel("Pressure (hPa)")
        
    # Optional: zero contour
    #ax.contour(lat, p, percent_diff, levels=[0], colors="black", linewidths=1)
    
    # Add stratopause and tropopause lines if desired
    ax.axhline(1.0, color="black", lw=2, ls="--")
    ax.plot(lat1, tropopause_zm, color="black", lw=2, ls="--")

ax.invert_yaxis()
    

# ---------------------------------------
# Shared colorbar
# ---------------------------------------
fig.colorbar(cf, ax=axes.ravel().tolist(), location="right", label="Difference (pptv)")

#plt.suptitle("Zonal Mean Percent Differences (Symmetric)")
#plt.tight_layout()
plt.show()




# ---------------------------------------
# Input files
# ---------------------------------------
nfile1 = "/home/bryan/Negishi_Downloads_March/OutputDir/prod_newconst/2036/GEOSChem.SpeciesConc.20360601_0000z.nc4" #"GEOSChem.SpeciesConc.20200630_0000z.nc4"
#nfile2 = "/home/bryan/tutorial2/barkers_prod/OutputDir/GEOSChem.SpeciesConc.20210601_0000z.nc4"
#file3='/home/bryan/tutorial2/myemit_prod/Restarts/GEOSChem.Restart.20210601_0000z.nc4'

# Species name
species_name1 = "SpeciesConcVV_ClNO3"   # or any other species
species_name2="SpeciesConcVV_HCl"


# ---------------------------------------
# Load both files
# ---------------------------------------
zm1, p1, lat1 = load_strat_zm(nfile1, species_name1)
zm2, p2, lat2 = load_strat_zm(nfile1, species_name2)

zm2=zm2/1000
zm1=zm1/1000 #convert to ppbv

# ---------------------------------------
# Plotting
# ---------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 6),constrained_layout=True, sharey=True)

# Shared color scale
vmin1 = zm1.min()
vmax1 = zm1.max()
vmin2 = zm2.min()
vmax2 = zm2.max()

# Panel 1
cf1 = axes[0].contourf(
    lat1, p1, zm1,
    levels=30, cmap="BuGn",
    vmin=vmin1, vmax=vmax1
)
axes[0].set_title("ClNO3")
axes[0].set_xlabel("Latitude (degrees)")

# Panel 2
cf2 = axes[1].contourf(
    lat2, p2, zm2,
    levels=30, cmap="BuGn",
    vmin=vmin2, vmax=vmax2
)
axes[1].set_title("HCl")
axes[1].set_xlabel("Latitude (degrees)")

# Pressure axis
axes[0].set_yscale("log")
axes[0].invert_yaxis()
axes[0].set_ylabel("Pressure (hPa)")

# Stratopause annotation (~1 hPa)
for ax in axes:
    ax.axhline(1.0, color="red", lw=2, ls="--")
    ax.plot(lat1, tropopause_zm, color="red", lw=2, ls="--")

# Colorbar
plt.subplots_adjust(right=0.9)
cbar = fig.colorbar(cf1, ax=axes.ravel().tolist(),location='right', label="ClNO3 (ppbv)")
cbar = fig.colorbar(cf2, ax=axes.ravel().tolist(),location='right', label="HCl (ppbv)")

#plt.suptitle("Stratospheric Zonal Mean Ozone (Two GEOS-Chem Files)")
#plt.tight_layout()
plt.show()

