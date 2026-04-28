-----------------------------------------------------------

Directions for GCC changes to add alumina tracer & chemistry

This readme is a step-by-step changelog that accompanies Chapter 5 of
  thesis. Complementary is the geoschem documentation, https://geos-chem.readthedocs.io
  
Commits in this section of the repo should reflect the clean file download followed
  by changes below to follow along. Line names reference final file line numbers.
  
This changelog does not express changes like output directory location or step time. It
  also assumes your environment is already set up.
  
-----------------------------------------------------------

SECTION 1: CREATE RUN DIRECTORY

>> pull GCClassic git: 
```
    git clone --recurse-submodules https://github.com/geoschem/GCClassic.git
```
    
>> build run directory
```
    cd GCClassic/run
    ./createRunDir.sh
```
    --you answer a bunch of questions here, put settings. chemistry 
      requires full chemistry setup
      
>> compile
```
    cd ~/Run_Directory_Name/build
    cmake ../CodeDir -DRUNDIR=..
    make -j
    make install
```

>> change geoschem_config.yml simulation time, HISTORY.rc outputs/frequency, 
     any other simulation settings; check geoschem documentation for more advice.
     recommend for troubleshooting set a short sim time, a few hours to a day. This
     will require changing HISTORY.rc to not output monthly or whatever
     
>> dryrun and download data and run (for debugging
```
    cd ..
    ./gcclassic --dryrun | tee log.dryrun
    ./download_data.py log.dryrun geoschem+http
    ./gcclassic | tee test1.log
```
    --you may need to change the download_data.yml to the WUSTL server not AWS here
>> debug any errors here
    
    
    
    
----------------------------------------------------------

SECTION 2: ADD ALUMINA

>> add alumina tracer in geoschem_config.yml, line 132
>> add alumina species in species_database.yml, lines 4 - 23
>> set case 6 in aerosol_mod.F90, line 2506 - 2510
     --path from run directory CodeDir/src/GEOS-Chem/GeosCore/aerosol_mod.F90
     --this is linked symbolically to your GCClassic directory, making the path
       from this README.md to aerosol_mod.F90 ./GCClassic/src/GEOS-Chem/GeosCore/aerosol_mod.F90
     --also, this section assumes your still working in the run directory
>> add alumina as a species in the first Restart file 
     --alumina3.py does this
>> re-compile and run to verify functionality


-----------------------------------------------------------

SECTION 3: ADD EMISSIONS

>> generate emissions file (most of the Emissions_Inventory_Scripts do this)
>> add header in HEMCO_Config.rc, lines 111 - 112
>> add switch in HEMCO_Config.rc, lines 2829 - 2836
     --you must point these switches to input files in your ExtData/HEMCO folder;
       this is where you should put the generated emissions file.
>> re-run to verify (you can check alumina concentration change in output restart/speciesconc files)

------------------------------------------------------------

SECTION 4: CHEMISTRY

>> turn off emissions, remove any alumina from restart file
>> add debug block to fullchem_mod.F90 lines 956 - 966 after Update_RCONST()
     --path from run directory CodeDir/src/GEOS-Chem/GeosCore/fullchem_mod.F90
     --this is linked symbolically to your GCClassic directory, making the path
       from this README.md to aerosol_mod.F90 ./GCClassic/src/GEOS-Chem/GeosCore/fullchem_mod.F90
>> add 'id_ALUM' for recognition, lines 41 and 2817, after SALA 
>> recompile and re-run to check zero-alumina reactivity
     --log file should show 0 alumina concentration and low reactivity. for
       the bin I choose the reactivity is:
         8.0784296875956768E-026 ClNO3 + HCl --> LOx + Cl2 + HNO3
    
