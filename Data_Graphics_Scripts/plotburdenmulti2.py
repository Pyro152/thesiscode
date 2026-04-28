import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import datetime

def plot_two_species_pptv(sim1, sim2, sim3, speciesA, speciesB):
    """
    Reads three GEOS-Chem simulations and plots two chemicals (pptv)
    in a two-panel figure: speciesA on top, speciesB on bottom.
    """

    # ------------------------------------------------------
    # Build date list (same as your original)
    # ------------------------------------------------------
    dates = []
    for year, month in [(2026,m) for m in range(7,13)] + \
                       [(y,m) for y in range(2027,2036) for m in range(1,13)] + \
                       [(2036,m) for m in range(1,7)]:
        dates.append(datetime.datetime(year, month, 15))

    # ------------------------------------------------------
    # Helper: compute global-mean stratospheric pptv
    # ------------------------------------------------------
    def concentration_from_file(fname, species_name):
        ds = xr.open_dataset(fname)

        vmr = ds[f"SpeciesConcVV_{species_name}"].isel(time=0)
        B_mid = ds["hybm"]
        strat_mask = B_mid < 1e-3

        vmr_strat = vmr.sel(lev=strat_mask).values
        conc_pptv = vmr_strat * 1e12  # convert to pptv

        area = ds["AREA"].values
        weights = area / area.sum()

        # weighted mean over lat/lon, then mean over levels
        conc_mean = np.sum(conc_pptv * weights, axis=(1,2)).mean()
        return conc_mean

    # ------------------------------------------------------
    # Helper: compute time series for one species & one sim
    # ------------------------------------------------------
    def compute_concentration_series(sim_dir, species_name):
        values = []
        for year, month in [(2026,m) for m in range(7,13)] + \
                           [(y,m) for y in range(2027,2036) for m in range(1,13)] + \
                           [(2036,m) for m in range(1,7)]:

            yyyymm = f"{year}{month:02d}"
            fname = f"{sim_dir}/{year}/GEOSChem.SpeciesConc.{yyyymm}01_0000z.nc4"
            print("Processing:", fname)
            values.append(concentration_from_file(fname, species_name))

        return np.array(values)

    # ------------------------------------------------------
    # Compute all six time series
    # ------------------------------------------------------
    concA_1 = compute_concentration_series(sim1, speciesA)
    concA_2 = compute_concentration_series(sim2, speciesA)
    concA_3 = compute_concentration_series(sim3, speciesA)

    concB_1 = compute_concentration_series(sim1, speciesB)
    concB_2 = compute_concentration_series(sim2, speciesB)
    concB_3 = compute_concentration_series(sim3, speciesB)
    
    pct2 = 100 * (concB_2 - concB_1) / concB_1
    pct3 = 100 * (concB_3 - concB_1) / concB_1

    # ------------------------------------------------------
    # Plotting
    # ------------------------------------------------------
    plt.rcParams.update({
        "font.size": 24,
        "axes.titlesize": 28,
        "axes.labelsize": 24,
        "xtick.labelsize": 20,
        "ytick.labelsize": 20
    })

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14,12), sharex=True)

    # Top panel: species A
    ax1.plot(dates, concA_1, '+-', markersize=12, label='Simulation 1') #f"{speciesA} – Scenario 1")
    ax1.plot(dates, concA_2, 's-', label='Simulation 2') #f"{speciesA} – Scenario 2")
    ax1.plot(dates, concA_3, '^-', label='Simulation 3') #f"{speciesA} – Scenario 3")
    ax1.set_ylabel(f"{speciesA} (pptv)")
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc="center left", bbox_to_anchor=(1.15, 0.5))

    # Bottom panel: species B
    ax2.plot(dates, concB_1, '+-',markersize=12) #, label=f"{speciesB} – Scenario 1")
    ax2.plot(dates, concB_2, 's-') #, label=f"{speciesB} – Scenario 2")
    ax2.plot(dates, concB_3, '^-') #, label=f"{speciesB} – Scenario 3")
    ax2.set_ylabel(f"{speciesB} (pptv)")

    ax2.grid(True, linestyle='--', alpha=0.5)
    #ax2.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
    
    # Bottom panel: species B
    ax3.plot(dates, pct2, 's-', label="Sim 2 vs Sim 1")
    ax3.plot(dates, pct3, '^-', label="Sim 3 vs Sim 1")
    ax3.set_xlabel("Date")
    ax3.axhline(0, color='k', linewidth=1)
    ax3.set_ylabel("Percent Difference (%)")
    ax3.grid(True, linestyle='--', alpha=0.5)
    ax3.legend(loc="center left", bbox_to_anchor=(1.15, 0.5))
    
    ax1.text(0, 1.05, "(a)", transform=ax1.transAxes,
         fontsize=28, fontweight="bold", va="top", ha="right")

    ax2.text(0, 1.05, "(b)", transform=ax2.transAxes,
         fontsize=28, fontweight="bold", va="top", ha="right")

    ax3.text(0, 1.05, "(c)", transform=ax3.transAxes,
         fontsize=28, fontweight="bold", va="top", ha="right")
         

    # Right axis: percent difference from initial value
    ax2b = ax2.twinx()

    pctB_1 = 100 * (concB_1 - concB_1[0]) / concB_1[0]
    pctB_2 = 100 * (concB_2 - concB_2[0]) / concB_2[0]
    pctB_3 = 100 * (concB_3 - concB_3[0]) / concB_3[0]

    # Plot ONLY the percent-difference curves here
    ax2b.plot(dates, pctB_1, color='C0', linestyle='--', alpha=0)
    ax2b.plot(dates, pctB_2, color='C1', linestyle='--', alpha=0)
    ax2b.plot(dates, pctB_3, color='C2', linestyle='--', alpha=0)

    ax2b.set_ylabel("Percent difference from start")



    plt.tight_layout()
    plt.show()


if __name__=='__main__':
    plot_two_species_pptv(
        sim1="/home/bryan/Negishi_Downloads_March/OutputDir/prod_baseline",
        sim2="/home/bryan/Negishi_Downloads_March/OutputDir/prod_hi_base",
        sim3="/home/bryan/Negishi_Downloads_March/OutputDir/prod_newconst",
        speciesA="ALUMINA",
        speciesB="O3"
    )
