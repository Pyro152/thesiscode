import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


def compute_regional_means(ds, var_name="SpeciesConcVV_HCl", level_index=41):
    """
    Compute mean concentration of a species at a given vertical level
    for three latitude regions.
    """
    da = ds[var_name].isel(lev=level_index)

    region_masks = {
        "South Polar (-90 to -60)": (da.lat >= -90) & (da.lat < -60),
        #"Tropics (-60 to 60)":      (da.lat >= -60) & (da.lat <= 60),
        "North Polar (60 to 90)":   (da.lat > 60) & (da.lat <= 90),
    }

    results = {}
    for region, mask in region_masks.items():
        results[region] = da.where(mask, drop=True).mean().item()*1e12

    return results


def burden_from_file(nc_path):
    """Wrapper to open a file and compute regional means."""
    ds = xr.open_dataset(nc_path)
    results = compute_regional_means(ds)
    ds.close()
    return results


def build_file_list_A():
    """2020-07 through 2021-06."""
    files = []
    for year, month in [(2026, m) for m in range(7,13)] + \
                       [(y,m) for m in range(1,13) for y in range(2027,2036)] + \
                       [(2036,m) for m in range(1,7)]:
        yyyymm = f"{year}{month:02d}"
        fname = f"/home/bryan/Negishi_Downloads_March/OutputDir/prod_newconst/{year}/GEOSChem.SpeciesConc.{yyyymm}01_0000z.nc4"
        files.append(fname)
    return files


def build_file_list_B():
    """Example comparison period: 2019-07 through 2020-06.
       Adjust as needed."""
    files = []
    for year, month in [(2026, m) for m in range(7,13)] + \
                       [(y,m) for m in range(1,13) for y in range(2027,2036)] + \
                       [(2036,m) for m in range(1,7)]:
        yyyymm = f"{year}{month:02d}"
        fname = f"/home/bryan/Negishi_Downloads_March/OutputDir/prod_baseline/{year}/GEOSChem.SpeciesConc.{yyyymm}01_0000z.nc4"
        files.append(fname)
    return files


def process_file_set(files):
    """Return a DataFrame of regional means for a list of files."""
    times = []
    region_series = {
        "South Polar (-90 to -60)": [],
        #"Tropics (-60 to 60)": [],
        "North Polar (60 to 90)": [],
    }

    for f in files:
        print(f"Processing {f} ...")
        results = burden_from_file(f)

        stamp = Path(f).stem.split(".")[2][:6]  # YYYYMM
        times.append(pd.to_datetime(stamp, format="%Y%m"))

        for region in region_series:
            region_series[region].append(results[region])

    df = pd.DataFrame(region_series, index=times).sort_index()
    return df


def main():
    # Build both file sets
    files_A = build_file_list_A()
    files_B = build_file_list_B()

    # Process both
    df_A = process_file_set(files_A)
    df_B = process_file_set(files_B)

    print("\nFirst few rows of Set A:")
    print(df_A.head())
    print("\nFirst few rows of Set B:")
    print(df_B.head())

    # Plot comparison
    plt.figure(figsize=(12, 7))

    plt.rcParams.update({
        "font.size": 24,          # doubles typical default (~12)
        "axes.titlesize": 28,     # title slightly larger
        "axes.labelsize": 24,     # axis labels
        "xtick.labelsize": 20,    # tick labels
        "ytick.labelsize": 20
    })

    colors = {
        "South Polar (-90 to -60)": "blue",
        #"Tropics (-60 to 60)": "green",
        "North Polar (60 to 90)": "red",
    }

    for region in df_A.columns:
        plt.plot(df_A.index, df_A[region],
                 label=f"{region} — New Input",
                 color=colors[region],
                 linewidth=2)

        plt.plot(df_B.index, df_B[region],
                 label=f"{region} — Barker Input",
                 color=colors[region],
                 linestyle="--",
                 linewidth=2)

    #plt.title("Comparison of Mean Alumina Concentration at 6.6hPa")
    plt.xlabel("Time")
    plt.ylabel("Mean Concentration (pptv)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__=='__main__':
	main()
