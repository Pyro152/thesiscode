-----------------------------------------------------------

Directions for GCC changes to add alumina tracer & chemistry

This readme is a step-by-step changelog that accompanies Chapter 5 of
  thesis. Complementary is the geoschem documentation, https://geos-chem.readthedocs.io
  
Commits in this section of the repo should reflect the clean file download followed
  by changes below. Line names reference final file line numbers.
  
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
     recommend for troubleshooting set a short runtime, a few hours to a day.
     
>> dryrun and download data
```
    cd ..
    

    
