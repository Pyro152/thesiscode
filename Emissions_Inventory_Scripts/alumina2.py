import xarray as xr
import numpy as np
from datetime import datetime as dt


#open restart file
ds = xr.open_dataset("GEOSChem.Restart.20190701_0000z.nc4")


# NEW_SPECIES_DATA
alumina=np.zeros((len(ds.lev),len(ds.lat),len(ds.lon)))
alumina=alumina[np.newaxis,...]
alumina = np.array(alumina)
#alumina[0,50,23,36]=1


#initialize dataset
xrds=xr.DataArray(
    alumina,
    
    coords={
        'time': ds.time,
        'lon': ds.lon,
        'lat': ds.lat,
        'lev': ds.lev
    },
    
    dims=['time','lev','lat','lon'],
    name='SpeciesRst_ALUMINA',
    
    attrs={
    'long_name': 'Dry mixing ratio of species ALUMINA',
    'units': 'mol mol-1 dry',
    'averaging_method': 'instantaneous'
    }
    
)


#add to history
old_history = ds.attrs.get("history", "")
dtnow=dt.utcnow().strftime('%Y-%m-%d %H:%M:%S')

new_line = f"ALUMINA tracer added at {dtnow} using xarray in Python by Bryan Hartigan"




encoding = {
    "SpeciesRst_ALUMINA": {
        "dtype": "float32",
        "_FillValue": np.nan,
        "chunksizes": (1, 1, 46, 72)   # just integers, no U suffix
    }
}



ds['SpeciesRst_ALUMINA']=xrds


if old_history:
    ds.attrs["history"] = old_history + "\n" + new_line
else:
    ds.attrs["history"] = new_line


ds.to_netcdf('restart_file_new.nc',encoding=encoding)


