import numpy as np
import xarray as xr
import pdb 

def haversine(lat1, lon1, lat2, lon2):
    """
    Compute the Haversine distance between two points in latitude and longitude.
    
    Parameters:
    lat1, lon1 - Latitude and Longitude of point 1 in decimal degrees
    lat2, lon2 - Latitude and Longitude of point 2 in decimal degrees
    
    Returns:
    Distance in kilometers between the two points
    """
    R = 6371.0  # Radius of the Earth in kilometers
    
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Haversine formula
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    # Distance in kilometers
    distance = R * c
    return distance

def compute_pixel_area(da, mask=None):
    """
    Compute the pixel area in km^2 for a DataArray in lat/lon coordinates over time dimension
    
    Parameters:
    da - xarray DataArray with latitude and longitude as dimensions
    
    Returns:
    A DataArray of pixel areas in km^2
    """
    # Extract latitude and longitude values
    lat = da['latitude'].values
    lon = da['longitude'].values
    
    # Prepare empty array for pixel areas (size will be one less in both dimensions)
    pixel_areas = np.full((lat.shape[0] , lon.shape[0] ), 0) 

    if mask is None:
        mask = np.ones((da.latitude.shape[0]-1,da.longitude.shape[0]-1))
        idx = np.where(mask.T==1)
    else: 
        idx = np.where(mask.T==1)

    try:
    # Loop over each grid cell and compute the area
        for (i,j) in zip(*idx):
            # North-South distance (distance between adjacent latitudes)
            dist_ns = haversine(lat[j], lon[i], lat[j + 1], lon[i])
            
            # East-West distance (distance between adjacent longitudes)
            dist_ew = haversine(lat[j], lon[i], lat[j], lon[i + 1])
            
            # Compute pixel area (approximate) by multiplying the two distances
            pixel_areas[j, i] = dist_ns * dist_ew * 1.e6
    except: 
        pdb.set_trace()
    
    pixel_areas[-1,:] = pixel_areas[-2,:]
    pixel_areas[:,-1] = pixel_areas[:,-2]
    
    # Return a new DataArray containing pixel areas
    return xr.DataArray( np.repeat(pixel_areas[np.newaxis, :, :], da.time.shape[0], axis=0), dims=da.dims, 
                        coords={"time":da['time'], "latitude": da['latitude'], "longitude": da['longitude']},
                        name="pixel_area_m2")