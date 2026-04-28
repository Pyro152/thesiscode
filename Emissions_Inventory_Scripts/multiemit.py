import numpy as np
from scipy.integrate import dblquad
import pandas as pd

import sys
#sys.path.append('./python_modules/')
from distribute_emis_func import read_gc_box_height, make_grid_LL

import xarray as xr
import datetime
from datetime import datetime as dt

import csv


########### CONTROL PANEL ##################################
#total_mass=637240    #total mass on reentry
resolution='4x5'   # xxtuple (lat,lon)xx wrong its a string 'latxlon' in deg
nlev=47               #levels (options 47 or 72, though 72 doesn't necessarily work)    
#inc_deg=55         #satellite/constellation inclination
timestep=315576000      #timestep--that is, time over which total mass is emitted, seconds. set to 10 years for a baseline turnover of 10% per year

constfile='satconstinfo.csv'  #input constellation info file (csv?)
metfile='GEOSChem.StateMet.20190701_0000z.nc4'  #netcdf file name that surface area is taken from, must match res

outfilename='prod_baseline.nc'   #name of generated file
############################################################
    

#make grid coordinates
time=[0]
lev=np.arange(1,nlev+1).tolist()
grid_info=make_grid_LL(resolution)

#useful intermediaries: surf area, grid attributes
_, area, _, _, _ = read_gc_box_height(metfile,nlev)
kg_to_kgm2s=area*timestep

#read in info of each sat const. [number, total mass, inclination(deg)]
constinfo = []
with open(constfile) as f:
    reader = csv.DictReader(f)
    for row in reader:
        constinfo.append([
            row["number"],            # keep as string
            float(row["mass"]),       # convert to float
            float(row["inc"])         # convert to float
        ])

#important dimensions
torad = np.pi / 180
lengths=(len(time),nlev,len(grid_info['lat']),len(grid_info['lon']),len(constinfo))


# ----------------------------------------------------
# PDF definition (lat, lon, inc all in DEGREES)
# ----------------------------------------------------
def pdf(lat_deg, lon_deg, inc_deg):
    if abs(lat_deg) > inc_deg:
        return 0.0

    lat = lat_deg * torad
    inc = inc_deg * torad

    sin_lat = np.sin(lat)
    cos_lat = np.cos(lat)
    sin_inc = np.sin(inc)

    inside = sin_inc**2 - sin_lat**2
    if inside <= 0:
        return 0.0

    return cos_lat / (360 * 180 * np.sqrt(inside))


# ----------------------------------------------------
# Integrate over a single lat-lon box (bounds in degrees)
# ----------------------------------------------------
def integrate_region(lat1_deg, lat2_deg, lon1_deg, lon2_deg, inc_deg):

    # dblquad integrates f(lon, lat)
    result, err = dblquad(
        lambda lon, lat: pdf(lat, lon, inc_deg),
        lat1_deg, lat2_deg,
        lambda lat: lon1_deg,
        lambda lat: lon2_deg
    )
    return result


# ----------------------------------------------------
# Build the 45×72 probability grid
# ----------------------------------------------------
def compute_probability_grid(inc_deg,grid,lengthlist):
    #input const. inclination, grid info, lat/lon lengths only as a list
    # Latitude edges: -90 to +90 in 4° steps → 46 edges
    #lat_edges = np.arange(-90, 90 + 4, 4)
    lat_edges=grid['lat_b']

    # Longitude edges: -180 to +180 in 5° steps → 73 edges
    #lon_edges = np.arange(-180, 180 + 5, 5)
    lon_edges=grid['lon_b']

    # Create empty 45×72 array
    prob_grid=np.zeros(lengthlist)

    for i in range(lengthlist[0]):        # latitude bins
        for j in range(lengthlist[1]):    # longitude bins
            lat1, lat2 = lat_edges[i], lat_edges[i+1]
            lon1, lon2 = lon_edges[j], lon_edges[j+1]

            prob_grid[i, j] = integrate_region(lat1, lat2, lon1, lon2, inc_deg)

    return prob_grid


# ----------------------------------------------------
# Build 45×72 mass grid as a sum of probability*mass
# ----------------------------------------------------
def compute_mass_grid(constinfolist, grid, lengthlist):

    #loop thru each sat group to create mass map
    prob2dlist=np.zeros(lengthlist)
    almass2dlist=np.zeros(lengthlist)
    almass2dsum=np.zeros(lengthlist[0:2])
    for i in range(lengthlist[2]):
        prob = compute_probability_grid(constinfolist[i][2],grid,lengthlist[0:2])
        masslayer2d = constinfolist[i][1]*prob
        print('satnum:  ', constinfolist[i][0], '  list mass:  ', constinfolist[i][1], '  grid mass:  ', np.sum(masslayer2d))
        
        prob2dlist[:,:,i] = prob
        almass2dlist[:,:,i] = masslayer2d
        almass2dsum += masslayer2d
    
    return almass2dsum, almass2dlist, prob2dlist



############## DATA GENERATION AND CONVERSION TO NETCDF ################

#convert to mass --> concentration
almass2d, al2dmasslist, df=compute_mass_grid(constinfo,grid_info,lengths[2:5])
print('DOUBLE CHECK TOTAL MASS:')
print('list total:  ', sum(row[1] for row in constinfo))
print('grid total:  ', np.sum(almass2d))


al_reentry_conc=np.zeros(lengths[0:4])
for i in [0,1]:
    for row in range(lengths[2]):
        for column in range(lengths[3]):
            al_reentry_conc[0,nlev-i-1,row,column]=almass2d[row,column] / kg_to_kgm2s[row,column] /2

#double check yearly input
check_time=31557600   #validate how much material is input in a time period (i chose one year to compare with barker data)
print('Sum of input file mass input over ',check_time/365.25/24/3600,'years:  ', np.sum(area*(al_reentry_conc[0,nlev-1,:,:]+al_reentry_conc[0,nlev-2,:,:])*check_time))


# ----------------------------------------------------
# Populate netcdf dataset
# ----------------------------------------------------
ds=xr.Dataset(
    coords={
        'time': time,
        'lev': lev,
        'lat': grid_info['lat'],
        'lon': grid_info['lon'],
        'satnum': list(row[0] for row in constinfo)
    },
    
    data_vars={
        'AREA': (['lat','lon'], area),
        'constellation_pdf': (['lat','lon','satnum'], df),
        'al_mass_constellation': (['lat','lon','satnum'], al2dmasslist),
        'al_mass_total': (['lat','lon'], almass2d),
        'reentry_al': (['time','lev','lat','lon'], al_reentry_conc)
    }
    
)


# ----------------------------------------------------
# Metadata
# ----------------------------------------------------

#global
ds.attrs={
    'Conventions': 'CF-1.6',
    'Title': 'alumina emissions generated file',
    'Contact': 'Bryan Enstam Hartigan (bryan.hartigan.1@us.af.mil)',
    'GeneratedBy': 'same (same)',
    'Start_Date': '2019-07-01',
    'End_Date': '2019-07-02',
    'Start_Time': '00:00:00.0',
    'End_Time': '23:59:59.9',
    'frequency': 'mon'
}

dtnow=dt.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')
ds.attrs['GenerationDate']=dtnow
ds.attrs['history']=f'File created at {dtnow} using xarray in Python by Bryan Hartigan'

#variable attributes (coordinates first)
ds['time'].attrs={
    'standard_name': 'time',
    'long_name': 'Time',
    'units': 'hours since 2019-07-01 00:00:00',
    'calendar': 'standard',
    'axis': 'T'
}

ds['lev'].attrs={
    'standard_name': 'level',
    'long_name': 'GEOS-Chem level on 47-layer model grid',
    'units': 'level',
    'positive': 'up',
    'axis': 'Z'
}

ds['lat'].attrs={
    'standard_name': 'latitude',
    'long_name': 'Latitude',
    'units': 'degrees_north',
    'axis': 'Y'
}

ds['lon'].attrs={
    'standard_name': 'longitude',
    'long_name': 'Longitude',
    'units': 'degrees_east',
    'axis': 'X'
}

ds['satnum'].attrs={
    'standard_name': 'satellite number',
    'long_name': 'satellite NORAD identifier or constellation name'
}

ds['AREA'].attrs={
    'standard_name': 'surface area',
    'long_name': 'Surface Area',
    'units': 'm2'
}

ds['constellation_pdf'].attrs={
    'standard_name': 'constellation reentry pdf',
    'long_name': 'Probability of reentry as a 2d function of latitude-longitude, indexed by constellation',
    'units': '1'
}

ds['al_mass_constellation'].attrs={
    'standard_name': 'constellation alumina mass',
    'long_name': 'Expectation of total reentering alumina mass ablated, indexed by constellation',
    'units': 'kg'
}

ds['al_mass_total'].attrs={
    'standard_name': 'total alumina mass',
    'long_name': 'Expectation of total reentering alumina mass ablated at any time, combined',
    'units': 'kg'
}

ds['reentry_al'].attrs={
    'standard_name': 'reentry alumina emissions',
    'long_name': 'reentry alumina emissions concentration over time',
    'units': 'kg/m2/s'
}


# ----------------------------------------------------
# Encoding and export to netcdf
# ----------------------------------------------------

#encoding
myencoding={
    'time': {
        'dtype': 'int32',
        'chunksizes': lengths[0:1]
    },
    
    'lev': {
        'dtype': 'int32',
        'chunksizes': lengths[1:2]
    },
    
    'lat': {
        'dtype': 'float64',
        'chunksizes': lengths[2:3]
    },

    'lon': {
        'dtype': 'float64',
        'chunksizes': lengths[3:4]
    },
    
#    'satnum': {
#        'dtype': 'S10',
#        'chunksizes': lengths[4:5]
#    },

    'AREA': {
        'dtype': 'float64',
        'chunksizes': lengths[2:4]
    },
    
    'constellation_pdf': {
        'dtype': 'float64',
        'chunksizes': lengths[2:5]
    },
    
    'al_mass_constellation': {
        'dtype': 'float64',
        'chunksizes': lengths[2:5]
    },
    
    'al_mass_total': {
        'dtype': 'float64',
        'chunksizes': lengths[2:4]
    },
    
    'reentry_al': {
        'dtype': 'float64',
        'chunksizes': lengths[0:4]
    },
    
}

#export ncdf
ds.to_netcdf(outfilename,encoding=myencoding)

