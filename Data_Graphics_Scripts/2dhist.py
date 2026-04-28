import csv
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker


def parse_coord(coord_text):
    """
    Parse strings like:
        '56E 34S?'
        '112W 45S?'
        '166W 42N'
    Returns (longitude, latitude) as floats.
    """

    coord_text = coord_text.replace("?", "").strip()
    lon_part, lat_part = coord_text.split()

    # Longitude
    lon_deg = float(lon_part[:-1])
    lon_dir = lon_part[-1]
    longitude = lon_deg if lon_dir == "E" else -lon_deg

    # Latitude
    lat_deg = float(lat_part[:-1])
    lat_dir = lat_part[-1]
    latitude = lat_deg if lat_dir == "N" else -lat_deg

    return longitude, latitude


# -----------------------------
# Load data
# -----------------------------
longitudes = []
latitudes = []

with open("reentry.rcat.tsv", "r", newline="") as f:
    reader = csv.reader(f, delimiter="\t")

    next(reader)  # skip header 1
    next(reader)  # skip header 2

    for row in reader:
        location_text = row[22]

        if location_text == "-":
            continue

        # Must contain both longitude and latitude directions
        if not (("E" in location_text or "W" in location_text) and
                ("N" in location_text or "S" in location_text)):
            continue

        try:
            lon, lat = parse_coord(location_text)
            longitudes.append(lon)
            latitudes.append(lat)
        except Exception:
            continue


# Convert to arrays
longitudes = np.array(longitudes)
latitudes = np.array(latitudes)

print(f"Loaded {len(latitudes)} coordinate entries.")


# -----------------------------
# Create 2D histogram
# -----------------------------
bins_lon = np.linspace(-180, 180, 73)   # 5° bins
bins_lat = np.linspace(-90, 90, 37)     # 5° bins

hist, xedges, yedges = np.histogram2d(longitudes, latitudes,
                                      bins=[bins_lon, bins_lat])

'''
# -----------------------------
# Dot-based density map
# -----------------------------
fig = plt.figure(figsize=(12, 6))
ax = plt.axes(projection=ccrs.PlateCarree())

# Map features
ax.add_feature(cfeature.LAND, facecolor="lightgray")
ax.add_feature(cfeature.OCEAN, facecolor="white")
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.3)
ax.set_global()
ax.set_title("Reentry Frequency (Dot Size & Color Represent Density)")

# Compute bin centers
lon_centers = 0.5 * (xedges[:-1] + xedges[1:])
lat_centers = 0.5 * (yedges[:-1] + yedges[1:])

# Flatten histogram and coordinates
H = hist.T.flatten()
lon_flat = np.repeat(lon_centers, len(lat_centers))
lat_flat = np.tile(lat_centers, len(lon_centers))

# Keep only bins with events
mask = H > 0
H = H[mask]
lon_flat = lon_flat[mask]
lat_flat = lat_flat[mask]

# Normalize sizes for plotting
sizes = 20 + 200 * (H / H.max())   # base size + scaled size

# Scatter plot
sc = ax.scatter(
    lon_flat,
    lat_flat,
    s=sizes,
    c=H,
    cmap="hot",
    alpha=0.75,
    transform=ccrs.PlateCarree(),
    edgecolor="black",
    linewidth=0.3
)

# Colorbar
cbar = plt.colorbar(sc, ax=ax, shrink=0.7)
cbar.set_label("Reentry Count")
########

fig = plt.figure(figsize=(12, 6))
ax = plt.axes(projection=ccrs.PlateCarree())

ax.add_feature(cfeature.LAND, facecolor="lightgray")
ax.add_feature(cfeature.OCEAN, facecolor="white")
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.3)

# Force full world view
ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())

mesh = ax.pcolormesh(
    xedges,
    yedges,
    hist.T,
    cmap="hot",
    shading="auto",          # prevents antimeridian clipping
    transform=ccrs.PlateCarree()
)

cbar = plt.colorbar(mesh, ax=ax, shrink=0.7)
cbar.set_label("Reentry Count")

plt.tight_layout()
plt.show()


print(np.sum(hist))
print(len(longitudes))


plt.tight_layout()
plt.show()
'''

plt.rcParams.update({
    "font.size": 24,          # doubles typical default (~12)
    "axes.titlesize": 28,     # title slightly larger
    "axes.labelsize": 24,     # axis labels
    "xtick.labelsize": 20,    # tick labels
    "ytick.labelsize": 20
})


# -----------------------------
# Dot-based 2D histogram (all longitudes preserved)
# -----------------------------
fig = plt.figure(figsize=(12, 6))
ax = plt.axes(projection=ccrs.PlateCarree())

# Map features
ax.add_feature(cfeature.LAND, facecolor="lightgray")
ax.add_feature(cfeature.OCEAN, facecolor="white")
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.3)

# Force full world view
ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
ax.axis('on')

ax.set_xticks(np.arange(-180, 181, 30), crs=ccrs.PlateCarree()) 
ax.set_yticks(np.arange(-90, 91, 30), crs=ccrs.PlateCarree()) 
ax.xaxis.set_major_formatter(cticker.LongitudeFormatter()) 
ax.yaxis.set_major_formatter(cticker.LatitudeFormatter())

# Compute bin centers
lon_centers = 0.5 * (xedges[:-1] + xedges[1:])
lat_centers = 0.5 * (yedges[:-1] + yedges[1:])

# Flatten histogram (lat-major order)
H = hist.T.flatten()

# Correct coordinate flattening:
# longitude varies fastest, latitude varies slowest
lon_flat = np.tile(lon_centers, len(lat_centers))
lat_flat = np.repeat(lat_centers, len(lon_centers))

# Keep only bins with events
mask = H > 0
H = H[mask]
lon_flat = lon_flat[mask]
lat_flat = lat_flat[mask]


# Dot sizes and colors
sizes = 20 + 250 * (H / H.max())   # scale size by density
colors = H                         # color also reflects density

# Scatter plot
sc = ax.scatter(
    lon_flat,
    lat_flat,
    s=sizes,
    c=colors,
    cmap="hot",
    alpha=0.75,
    transform=ccrs.PlateCarree(),
    edgecolor="black",
    linewidth=0.3
)

# Title + axes labels 
#ax.set_title("Histogram of GCAT Reentries")
ax.set_xlabel("Longitude (degrees)")
ax.set_ylabel("Latitude (degrees)")

# Colorbar
cbar = plt.colorbar(sc, ax=ax, shrink=0.7)
cbar.set_label("Reentry Count")

plt.tight_layout()
plt.show()



# -----------------------------
# 1D Histogram of Longitudes
# -----------------------------
fig, ax = plt.subplots(figsize=(10, 4))

# Choose bin width (e.g., 5°)
bins = np.arange(-180, 185, 10)

ax.hist(longitudes, bins=bins, edgecolor="black", color="steelblue")
ax.set_xlabel("Longitude (degrees)")
ax.set_ylabel("Reentry Count")
#ax.set_title("Longitude Distribution of Reentries (5° bins)")
ax.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.show()

# -----------------------------
# 1D Histogram of Latitudes
# -----------------------------
fig, ax = plt.subplots(figsize=(10, 4))

# Choose bin width (e.g., 2° or 5°)
bins = np.arange(-90, 95, 5)

ax.hist(latitudes, bins=bins, edgecolor="black", color="darkgreen")
ax.set_xlabel("Latitude (degrees)")
ax.set_ylabel("Reentry Count")
#ax.set_title("Latitude Distribution of Reentries (5° bins)")
ax.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.show()



