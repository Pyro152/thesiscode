'''from pprint import pprint
import xarray as xr

ds=xr.open_dataset('/home/bryan/ExtData/HEMCO/prod_singlconst_input.nc')

pprint(ds.variables)'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker
import xarray as xr

ds = xr.open_dataset("/home/bryan/ExtData/HEMCO/Barkers_Rockets/2020/02/byproduct_emis_all_4x5_47L_20200206.nc4")

reentry_top = ds["reentry_al"].isel(time=21, lev=-1)
lats = ds["lat"]
lons = ds["lon"]

# Create a colormap where the lowest value is white
cmap = plt.cm.RdBu_r
colors = cmap(np.linspace(0, 1, 256))
colors[0] = [1, 1, 1, 1]   # RGBA for white
new_cmap = mcolors.ListedColormap(colors)


plt.rcParams.update({
    "font.size": 24,          # doubles typical default (~12)
    "axes.titlesize": 28,     # title slightly larger
    "axes.labelsize": 24,     # axis labels
    "xtick.labelsize": 20,    # tick labels
    "ytick.labelsize": 20
})

plt.figure(figsize=(12, 6))
ax = plt.axes(projection=ccrs.PlateCarree())

# Force full world view
ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
ax.axis('on')

ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS)
ax.add_feature(cfeature.LAND, facecolor="lightgray")
ax.add_feature(cfeature.OCEAN, facecolor="white")

ax.set_xticks(np.arange(-180, 181, 30), crs=ccrs.PlateCarree()) 
ax.set_yticks(np.arange(-90, 91, 30), crs=ccrs.PlateCarree()) 
ax.xaxis.set_major_formatter(cticker.LongitudeFormatter()) 
ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())

heat = ax.pcolormesh(
    lons, lats, reentry_top,
    cmap=new_cmap,
    shading="auto",
    transform=ccrs.PlateCarree()
)

ax.set_xlabel("Longitude (degrees)")
ax.set_ylabel("Latitude (degrees)")

plt.colorbar(heat, label="Reentry Alumina Emissions (kg/m²/s)")
#plt.title("Top-Level Reentry Alumina Emissions")
plt.show()
