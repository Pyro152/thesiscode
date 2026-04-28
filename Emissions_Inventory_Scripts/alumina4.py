import xarray as xr
import numpy as np
from datetime import datetime as dt


# COORDINATES
time=[]
time.append(0)
bnds=[0,1]
lat=np.arange(-90, 90.5, 0.5).tolist()
lon=np.arange(-180,180,0.625).tolist()
lev=np.arange(1,37).tolist()


# DATA
time_bnds=[0,720]
time_bnds=np.array(time_bnds)
time_bnds=time_bnds[np.newaxis, ...]

alumina=np.zeros((len(time),len(lev),len(lat),len(lon)))
alumina[0,35,60,250]=5e-14
#ttt=np.random.randint(20,30,size=(576,361,36))


#initialize dataset
xrds=xr.Dataset(
    coords={
        'time': time,
#        'bnds': bnds,
        'lon': lon,
        'lat': lat,
        'lev': lev
    },
    
    data_vars={
		'time_bnds': (['time','bnds'], time_bnds),
        'alumina': (['time','lev','lat','lon'], alumina)
    }
    
)

#print(xrds)




# METADATA

#globals
xrds.attrs={
    'Conventions': 'CF-1.6',
    'Title': 'alumina emissions generated file',
    'Contact': 'Bryan Enstam Hartigan (bryan.hartigan.1@us.af.mil)',
    'GeneratedBy': 'same (same)',
	'Start_Date': '2021-07-01',
	'End_Date': '2021-07-02',
	'Start_Time': '00:00:00.0',
	'End_Time': '23:59:59.9',
	'frequency': 'mon'
}

dtnow=dt.utcnow().strftime('%Y-%m-%d %H:%M:%S')
xrds.attrs['GenerationDate']=dtnow
xrds.attrs['history']=f'File created at {dtnow} using xarray in Python by Bryan Hartigan'

#variable attributes
xrds['time'].attrs={
    'standard_name': 'time',
    'long_name': 'time',
    'bounds': 'time_bnds',
    'units': 'hours since 2021-07-01 00:00:00',
    'calendar': 'standard',
    'axis': 'T'
}

xrds['lat'].attrs={
    'standard_name': 'latitude',
    'long_name': 'latitude',
    'units': 'degrees_north',
    'axis': 'Y'
#    '_ChunkSizes': '361U'
}

xrds['lon'].attrs={
    'standard_name': 'longitude',
    'long_name': 'longitude',
    'units': 'degrees_east',
    'axis': 'X'
#    '_ChunkSizes': '361U'
}

xrds['lev'].attrs={
    'standard_name': 'level',
    'long_name': 'level',
    'units': 'level',
    'positive': 'up',
    'axis': 'Z'
#    '_ChunkSizes': '361U'
}

xrds['alumina'].attrs={
    'standard_name': 'alumina aerosol injection, kg/m2/s',
    'long_name': 'alumina aerosol injection, kg/m2/s',
    'units': 'kg/m2/s',
    'missing_value': -100000.0,
    'cell_methods': 'time: mean'
}


#encoding
myencoding={
    'time': {
        'dtype': 'int32',
        'chunksizes': (1,)
    },
    
    'time_bnds': {
        'dtype': 'float64',
        '_FillValue': None,
        'chunksizes': (1,2)
    },        

    'lon': {
        'dtype': 'float64',
        '_FillValue': None,
        'chunksizes': (576,)
	},

    'lat': {
        'dtype': 'float64',
        '_FillValue': None,
        'chunksizes': (361,)
    },

    'lev': {
        'dtype': 'int32',
        '_FillValue': None,
        'chunksizes': (36,)
    },
    
    'alumina': {
        'dtype': 'float64',
        '_FillValue': -100000.0,
        'chunksizes': (1,1,361,576)
    }
    
}


xrds.to_netcdf('second_alumina_file.nc',unlimited_dims=['time'],encoding=myencoding)
