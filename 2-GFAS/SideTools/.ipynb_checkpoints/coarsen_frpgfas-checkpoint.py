import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
#from netCDF4 import Dataset
import sys
import rioxarray
import geopandas as gpd
import scipy
import shapely
import datetime
from scipy.stats import gaussian_kde
from haversine import haversine, Unit
import xarray as xr
import importlib
from rasterio.transform import from_origin
from rasterio.features import geometry_mask

#homebrewed 
sys.path.append('../')
import haversine2Da 

directory    = '/data/IMFSE/FireBehaviourModelling/Emission/GFAS/'

files = ['GFAS-FRP-2022-04_2022-09.nc', 'GFAS-FRP-2022-10_2023-03.nc']

for file_ in files:
    print(file_)
    frpgfas = xr.open_dataset(directory+file_)
    
    frpgfas = frpgfas.rename({'valid_time': 'time'})
    frpgfas['time'] = frpgfas.time - pd.Timedelta(days=1) # to have it back to start of the time period
    
    pixelArea = haversine2Da.compute_pixel_area(frpgfas.frpfire)
    frp_world_sum = (frpgfas.frpfire*pixelArea).coarsen(longitude=5, latitude=5, boundary="trim").sum()
    pixelArea = haversine2Da.compute_pixel_area(frp_world_sum)
    frp_world = frp_world_sum / pixelArea
    frp_world.name='frpfire'
    frp_world.to_dataset().to_netcdf(directory+file_.split('.')[0]+'_05degree_2.nc')
