'''
import csv
from datetime import datetime

dates = []
locations = []

with open("reentry.rcat.tsv", "r", newline="") as f:
    reader = csv.reader(f, delimiter="\t")
    
    #skip first two lines
    next(reader)
    next(reader)

    for row in reader:
        # Extract raw text from columns 7 and 23 (indices 6 and 22)
        date_text = row[6]
        location_text = row[22]

        # Parse date like: 2024 Nov 5 0000
        date_value = datetime.strptime(date_text, "%Y %b %d %H%M ")

        dates.append(date_value)
        locations.append(location_text)

# Show a few parsed entries
print(dates[:5])
print(locations)
'''
'''
import csv
from datetime import datetime

dates = []
locations = []
latitudes = []
longitudes = []

def parse_coord(coord_text):
    """
    Parse strings like:
        '56E 34S?'
        '112W 45S?'
        '166W 42N'
    Returns (longitude, latitude) as floats.
    """

    # Remove trailing ? if present
    coord_text = coord_text.replace("?", "").strip()

    # Split into two parts: longitude and latitude
    lon_part, lat_part = coord_text.split(' ')

    # --- Parse longitude ---
    # Example: '112W' → degrees=112, direction='W'
    lon_deg = float(lon_part[:-1])
    lon_dir = lon_part[-1]

    if lon_dir == "E":
        longitude = lon_deg
    elif lon_dir == "W":
        longitude = -lon_deg
    else:
        raise ValueError(f"Unknown longitude direction: {lon_dir}")

    # --- Parse latitude ---
    # Example: '45S' → degrees=45, direction='S'
    lat_deg = float(lat_part[:-1])
    lat_dir = lat_part[-1]

    if lat_dir == "N":
        latitude = lat_deg
    elif lat_dir == "S":
        latitude = -lat_deg
    else:
        raise ValueError(f"Unknown latitude direction: {lat_dir}")

    return longitude, latitude


with open("reentry.rcat.tsv", "r", newline="") as f:
    reader = csv.reader(f, delimiter="\t")

    # Skip first two lines
    next(reader)
    next(reader)

    for row in reader:
        # Extract columns 7 and 23 (indices 6 and 22)
        date_text = row[6]
        location_text = row[22]

        # Parse date like: 2024 Nov 5 0000
        date_value = datetime.strptime(date_text, "%Y %b %d %H%M ")

        dates.append(date_value)
        locations.append(location_text)

        # If location is not '-', parse coordinates
        if location_text != "-":
            lon, lat = parse_coord(location_text)
            longitudes.append(lon)
            latitudes.append(lat)

'''
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

dates = []
locations = []
latitudes = []
longitudes = []
coord_dates = []        # dates corresponding ONLY to parsed coordinates

def parse_coord(coord_text):
    """
    Parse strings like:
        '56E 34S?'
        '112W 45S?'
        '166W 42N'
    Returns (longitude, latitude) as floats.
    """

    # Remove trailing ? if present
    coord_text = coord_text.replace("?", "").strip()

    # Split into two parts: longitude and latitude
    lon_part, lat_part = coord_text.split()

    # --- Parse longitude ---
    lon_deg = float(lon_part[:-1])
    lon_dir = lon_part[-1]

    if lon_dir == "E":
        longitude = lon_deg
    elif lon_dir == "W":
        longitude = -lon_deg
    else:
        raise ValueError(f"Unknown longitude direction: {lon_dir}")

    # --- Parse latitude ---
    lat_deg = float(lat_part[:-1])
    lat_dir = lat_part[-1]

    if lat_dir == "N":
        latitude = lat_deg
    elif lat_dir == "S":
        latitude = -lat_deg
    else:
        raise ValueError(f"Unknown latitude direction: {lat_dir}")

    return longitude, latitude


with open("reentry.rcat.tsv", "r", newline="") as f:
    reader = csv.reader(f, delimiter="\t")

    # Skip first two lines
    next(reader)
    next(reader)

    nodir=0
    baddir=0
    gooddir=0
    total=0
    for row in reader:
        total+=1
        
        date_text = row[6]
        location_text = row[22]

        # Parse date like: 2024 Nov 5 0000
        date_value = datetime.strptime(date_text, "%Y %b %d %H%M ")

        dates.append(date_value)
        locations.append(location_text)

        # Skip if location is '-' or not a coordinate
        if location_text == "-":
            nodir+=1
            continue

        # Check if it contains coordinate directions
        if not (("E" in location_text or "W" in location_text) and
                ("N" in location_text or "S" in location_text)):
            baddir+=1
            continue  # skip generic locations like 'Antarctic?'

        # Safe to parse
        try:
            gooddir+=1
            lon, lat = parse_coord(location_text)
            longitudes.append(lon)
            latitudes.append(lat)
            coord_dates.append(date_value)   # keep aligned with latitudes
        except Exception:
            # If parsing fails for any reason, skip it
            continue

# Show a few parsed entries
#print("Dates:", dates[:5])
#print("Locations:", locations[:5])
#print("Longitudes:", longitudes[:5])
#print("Latitudes:", latitudes[:5])

print('Unknown Reentry: ',nodir)
print('Unspecific Reentry: ',baddir)
print('Good Reentry: ',gooddir)
print('Total: ',total)


# Define the function f(l)
def f(l_deg):
    l_rad = np.radians(l_deg)
    sin_50 = np.sin(np.radians(50))
    denominator = np.sqrt(sin_50**2 - np.sin(l_rad)**2)
    return 2479* np.cos(l_rad) / 180 / denominator

# Generate l values from -49 to 49 degrees
l_values = np.linspace(-49, 49, 1000)
# Compute f(l) values, handling invalid values due to sqrt of negative numbers
f_values = np.full_like(l_values, np.nan)
valid_indices = np.abs(np.sin(np.radians(l_values))) < np.sin(np.radians(50))
f_values[valid_indices] = f(l_values[valid_indices])

'''
# Plot the function
plt.figure(figsize=(10, 6))
plt.plot(l_values, f_values, label=r'$f(\ell) = \frac{\cos(\ell)}{180\sqrt{\sin^2(50^\circ) - \sin^2(\ell)}}$')
plt.xlabel(r'$\ell$ (degrees)')
plt.ylabel(r'$f(\ell)$')
plt.title('Plot of the function $f(\ell)$ from -49° to 49°')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()'''

# Save the plot
output_path = "/mnt/data/plot_function_f_l.png"
#plt.savefig(output_path)

print(f"Plot of the function f(l) saved as {output_path}")


# ---- Histogram of latitudes (bin size = 2 degrees) ----
if latitudes:
    min_lat = int(min(latitudes))
    max_lat = int(max(latitudes))

    # Create bins every 2 degrees
    bins = range(min_lat, max_lat + 3, 2)

    fig,ax = plt.subplots(figsize=(8,5))
    
    ax.hist(latitudes, bins=bins, edgecolor='black')
    ax.plot(l_values, f_values, color='red', linewidth=2, label='f(l)')
    ax.set_xlabel("Latitude (degrees)")
    ax.set_ylabel("Frequency")
    ax.set_title("Histogram of Reentry Latitudes (2° bins)")
    ax.legend()
    
    plt.show()

else:
    print("No valid latitude data to plot.")
    
'''
# ---- Histogram 2: Latitudes from years 2020–2022 ----
latitudes_2020_2022 = [
    lat for lat, dt in zip(latitudes, dates)
    if 2020 <= dt.year <= 2022
]

if latitudes_2020_2022:
    min_lat2 = int(min(latitudes_2020_2022))
    max_lat2 = int(max(latitudes_2020_2022))
    bins2 = range(min_lat2, max_lat2 + 3, 2)

    plt.figure(figsize=(10, 5))
    plt.hist(latitudes_2020_2022, bins=bins2, edgecolor='black')
    plt.xlabel("Latitude (degrees)")
    plt.ylabel("Frequency")
    plt.title("Histogram of Reentry Latitudes (2020–2022, 2° bins)")
    plt.show()
else:
    print("No latitude data found for years 2020–2022.")


import csv
from datetime import datetime
import matplotlib.pyplot as plt

dates = []              # all dates (for reference, if you want)
locations = []
latitudes = []
longitudes = []
coord_dates = []        # dates corresponding ONLY to parsed coordinates

def parse_coord(coord_text):
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


with open("reentry.rcat.tsv", "r", newline="") as f:
    reader = csv.reader(f, delimiter="\t")

    # Skip first two lines
    next(reader)
    next(reader)

    for row in reader:
        date_text = row[6]
        location_text = row[22]

        # Parse date like: 2024 Nov 5 0000
        date_value = datetime.strptime(date_text, "%Y %b %d %H%M ")

        dates.append(date_value)
        locations.append(location_text)

        # Skip non-coordinate locations
        if location_text == "-":
            continue

        if not (("E" in location_text or "W" in location_text) and
                ("N" in location_text or "S" in location_text)):
            continue

        try:
            lon, lat = parse_coord(location_text)
            longitudes.append(lon)
            latitudes.append(lat)
            coord_dates.append(date_value)   # keep aligned with latitudes
        except Exception:
            continue


# ---- Histogram 1: All latitudes (2° bins) ----
if latitudes:
    min_lat = int(min(latitudes))
    max_lat = int(max(latitudes))
    bins = range(min_lat, max_lat + 3, 2)

    plt.figure(figsize=(10, 5))
    plt.hist(latitudes, bins=bins, edgecolor='black')
    plt.xlabel("Latitude (degrees)")
    plt.ylabel("Frequency")
    plt.title("Histogram of All Reentry Latitudes (2° bins)")
    plt.show()
else:
    print("No valid latitude data to plot.")

'''

# ---- Histogram 2: Latitudes from years 2020–2022 ----
latitudes_2020_2022 = [
    lat for lat, dt in zip(latitudes, coord_dates)
    if 2020 <= dt.year <= 2022
]

if latitudes_2020_2022:
    min_lat2 = int(min(latitudes_2020_2022))
    max_lat2 = int(max(latitudes_2020_2022))
    bins2 = range(min_lat2, max_lat2 + 3, 2)

    plt.figure(figsize=(10, 5))
    plt.hist(latitudes_2020_2022, bins=bins2, edgecolor='black')
    plt.xlabel("Latitude (degrees)")
    plt.ylabel("Frequency")
    plt.title("Histogram of Reentry Latitudes (2020–2022, 2° bins)")
    plt.show()
else:
    print("No latitude data found for years 2020–2022.")
