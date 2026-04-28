import numpy as np
import matplotlib.pyplot as plt
from sgp4.api import Satrec, jday
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.gridspec as gridspec

# --- 1. Sample ISS TLE (replace with downloaded TLE if you want) ---
line1 = "1 25544U 98067A   26110.52231242  .00009130  00000-0  17452-3 0  9996"
line2 = "2 25544  51.6326 225.5006 0006686 329.7855  30.2747 15.48851306562816"

#line1 = "1 25504U 98060A   26110.03587353  .00000331  00000-0  41412-4 0  9996"
#line2 = "2 25504  24.9954  70.7685 0016589 227.9497 200.2522 14.45502995451909"

sat = Satrec.twoline2rv(line1, line2)

# --- 2. Compute orbital period from mean motion (rev/day) ---
mean_motion = sat.no_kozai * 1440.0 / (2.0 * np.pi)  # rev/day from rad/min
# or directly from TLE if you parse it: n = 15.49 rev/day approx
# but here we recompute from sat.no_kozai
n_rev_per_day = mean_motion
period_minutes = 1440.0 / n_rev_per_day

print(f"Orbital period ≈ {period_minutes:.2f} minutes")

# --- 3. Build time array: every 5 minutes over one period ---
dt_minutes = 1.0
num_steps = int(np.ceil(period_minutes / dt_minutes)) + 1

# Choose a reference epoch close to TLE epoch (use TLE epoch itself)
# sat.jdsatepoch, sat.jdsatepochF are the TLE epoch in Julian days
jd0 = sat.jdsatepoch
jd0_frac = sat.jdsatepochF

times_jd = jd0 + jd0_frac + (np.arange(num_steps) * dt_minutes) / (24.0 * 60.0)
jd_int = np.floor(times_jd).astype(int)
jd_frac = times_jd - jd_int

# --- 4. Propagate with SGP4 to get ECI coordinates ---
xs, ys, zs = [], [], []
for jdi, jdf in zip(jd_int, jd_frac):
    e, r, v = sat.sgp4(jdi, jdf)
    if e != 0:
        xs.append(np.nan)
        ys.append(np.nan)
        zs.append(np.nan)
    else:
        xs.append(r[0] * 1000.0)  # km -> m
        ys.append(r[1] * 1000.0)
        zs.append(r[2] * 1000.0)

xs = np.array(xs)
ys = np.array(ys)
zs = np.array(zs)

# --- 5. Convert ECI (TEME) to ECEF (simplified) ---
# For a quick demo, we’ll approximate TEME->ECEF with a simple Earth rotation
# using GMST. For more precise work, use a library like `skyfield` or `pyorbital`.

def gmst_from_jd(jd):
    # Simple GMST (in radians) from Julian date
    T = (jd - 2451545.0) / 36525.0
    gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) \
           + 0.000387933 * T**2 - (T**3) / 38710000.0
    gmst = np.deg2rad(gmst % 360.0)
    return gmst

gmst = gmst_from_jd(times_jd)

# Rotate around Z by GMST: ECI -> ECEF
x_ecef = xs * np.cos(gmst) + ys * np.sin(gmst)
y_ecef = -xs * np.sin(gmst) + ys * np.cos(gmst)
z_ecef = zs

# --- 6. Convert ECEF to geodetic lat/lon (WGS84) ---
a = 6378137.0          # semi-major axis
f = 1.0 / 298.257223563
b = a * (1 - f)
e2 = 1 - (b**2 / a**2)

def ecef_to_geodetic(x, y, z):
    lon = np.arctan2(y, x)
    r = np.sqrt(x**2 + y**2)
    lat = np.arctan2(z, r * (1 - e2))  # initial guess

    # Iterate once or twice for better accuracy
    for _ in range(6):
        N = a / np.sqrt(1 - e2 * np.sin(lat)**2)
        h = r / np.cos(lat) - N
        lat = np.arctan2(z, r * (1 - e2 * N / (N + h)))

    return lat, lon

lat, lon = ecef_to_geodetic(x_ecef, y_ecef, z_ecef)

# Convert to degrees
lat_deg = np.rad2deg(lat)
lon_deg = np.rad2deg(lon)

# Wrap longitudes to [-180, 180] for nicer plotting
lon_deg = (lon_deg + 180) % 360 - 180

# --- 7. Mercator projection for plotting ---
# Mercator y = ln(tan(pi/4 + lat/2)), but clip near the poles
lat_clip = np.clip(lat_deg, -85, 85)  # avoid infinity
lat_rad = np.deg2rad(lat_clip)
x_merc = lon_deg
y_merc = np.log(np.tan(np.pi / 4.0 + lat_rad / 2.0))

# --- 8. Plot with time-colored dots ---
t_minutes = np.arange(num_steps) * dt_minutes


# Use a real Mercator projection
proj = ccrs.LambertCylindrical()

fig = plt.figure(figsize=(12, 10))
gs = gridspec.GridSpec(1, 2, width_ratios=[40, 1], wspace=0.05)

# Map axis
ax = fig.add_axes([0.05, 0.05, 0.80, 1.20], projection=proj)

# Simple outline
ax.add_feature(cfeature.COASTLINE, linewidth=0.6, zorder=1)
ax.add_feature(cfeature.BORDERS, linewidth=0.3, zorder=1)

# Gridlines
gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='gray', alpha=0.5)
gl.top_labels = False
gl.right_labels = False

# More latitude labels
gl.ylocator = plt.FixedLocator(np.arange(-90, 91, 5))


# Bounds
ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())

plt.rcParams.update({
    "font.size": 24,          # doubles typical default (~12)
    "axes.titlesize": 28,     # title slightly larger
    "axes.labelsize": 24,     # axis labels
    "xtick.labelsize": 20,    # tick labels
    "ytick.labelsize": 20
})

# Scatter points ABOVE map features
sc = ax.scatter(
    lon_deg,
    lat_deg,
    c=t_minutes,
    cmap='turbo',
    s=80,
    alpha=1.0,
    edgecolors='none',
    transform=ccrs.PlateCarree(),
    zorder=10
)



# Colorbar axis (separate column)
# Get the map axis position in figure coordinates
pos = ax.get_position()

# Create a new axis for the colorbar, same height as the map
cax = fig.add_axes([
    pos.x1 + 0.02,   # x-position (just to the right of the map)
    pos.y0-pos.height/2,          # y-position (same bottom as map)
    0.02,            # width of colorbar
    pos.height*2       # height matches map exactly
])

plt.colorbar(sc, cax=cax, label='Minutes since start')


#plt.suptitle('ISS Ground Track (Equal-Area Projection)')
plt.show()


'''
plt.figure(figsize=(10, 5))
sc = plt.scatter(x_merc, y_merc, c=t_minutes, cmap='viridis', s=15)
plt.colorbar(sc, label='Minutes since start')

# Add simple world outline (optional, crude)
plt.xlim(-180, 180)
plt.xticks(np.arange(-180, 181, 60))
plt.xlabel('Longitude (deg, Mercator x)')
plt.ylabel('Mercator y')
plt.title('ISS Ground Track over One Orbit (Mercator projection)')

plt.grid(True, linestyle='--', alpha=0.3)
plt.tight_layout()
plt.show()'''
