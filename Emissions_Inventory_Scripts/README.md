This folder contains the most important contributions from the thesis. Top-level python scripts implement the methodology discussed in Chapter 5. 

myemit.py was the original version of the predictive emissions-inventory-generation methodology. This file created first the Trial 2 (New Input) from Chapter 6, before changes to create the New SMC input for Chapter 7, which
are reflected in the current version. After the imports section there is a highlighted section with toggleable inputs.

myemit_singconst_version.py is a copy saved of myemit.py after creating the Chapter 6 Trial 2 input file.

multiemit.py is a modified version of myemit.py used to parse the entire LEO population of satellites as constituent constellations divided by one-degree inclination bins. The file reads an input csv with constituent constellation 
details and creates a pdf/mass distribution for each before summing them and creating the 3d emissions inventory. This module corresponds to the Baseline trial in Chapter 7.

constlistgenerator.py creates the input csv for multiemit.py. This file breaks down the TLE list for LEO satellites, groups them by inclination, and determines the mass of each. To find the mass of each satellite, the module
accesses the DISCOSweb API and to prompt the mass of each satellite identifier; satellites with no mass or entry in DISCOSweb are discarded. Masses are summed in each inclination band.


Dependencies/ includes a copy of dependencies for these files. This includes Connor Barker's distribute_emis_func.py for surface area calculation.

Restart_File_Modification/ includes python files that open restart netcdf files and modifies them, typically to add alumina as an input.

Satellite_Groups_Data/ contains example intermediate csvs between constlistgenerator.py and multiemit.py.

Test_Emissions_Inventories/ contains practice files that create a netcdf file and assign alumina emissions using Xarray. These were used for verifying GEOS-Chem preparation and understanding of the Xarray process.
