#!/use/bin/env python
# coding=utf-8
# @Author  : Shuhao Liu
# @Time    : 2025/7/15 10:50 
# @File    : BufferMask.py

import pathlib

import numpy as np
import cartopy.crs as ccrs
from scipy.ndimage import binary_dilation


def buffer_mask(mask,
                lat,
                lon,
                distance=200,
                operation='expand',
                projection=ccrs.AzimuthalEquidistant
                ):
    """
    Expand or shrink a binary mask by a specified distance (in km) using cartographic projection.

    Parameters:
    -----------
    mask : 2D numpy array
        Binary mask where 1=target area, 0=background.
    lat : 1D numpy array
        Latitude coordinates in degrees.
    lon : 1D numpy array
        Longitude coordinates in degrees.
    distance : float, optional
        Distance to expand/shrink (in kilometers). Default=200.
    operation : str, optional
        Either 'expand' (outward) or 'shrink' (inward). Default='expand'.
    projection : cartopy.crs.Projection, optional
        Projection to use for distance calculations. Default=AzimuthalEquidistant.

    Returns:
    --------
    modified_mask : 2D numpy array
        The expanded or shrunk mask with same shape as input.
    """

    # Validate inputs
    assert operation in ['expand', 'shrink'], "Operation must be 'expand' or 'shrink'"
    assert mask.ndim == 2, "Mask must be 2D array"
    assert len(lat) == mask.shape[0], "Latitude dimension mismatch"
    assert len(lon) == mask.shape[1], "Longitude dimension mismatch"

    # Calculate projection center (mean of coordinates)
    clat, clon = np.mean(lat), np.mean(lon)
    proj = projection(central_latitude=clat, central_longitude=clon)

    # Convert all grid points to projected coordinates (in meters)
    xx, yy = np.meshgrid(lon, lat)
    coords = proj.transform_points(ccrs.PlateCarree(), xx, yy)
    x, y = coords[..., 0], coords[..., 1]  # x and y in projection space

    # Calculate grid resolution (in km)
    dx = np.abs(x[0, 1] - x[0, 0]) / 1000  # Convert m to km
    dy = np.abs(y[1, 0] - y[0, 0]) / 1000
    avg_resolution_km = (dx + dy) / 2  # Average resolution in km

    # Determine number of pixels needed for the operation
    pixel_radius = int(np.ceil(distance / avg_resolution_km))

    # Create circular structuring element
    y_indices, x_indices = np.ogrid[-pixel_radius:pixel_radius + 1,
                           -pixel_radius:pixel_radius + 1]
    structure = (x_indices ** 2 + y_indices ** 2) <= pixel_radius ** 2

    # Apply morphological operation
    if operation == 'expand':
        modified_mask = np.array(binary_dilation(mask, structure=structure))
    else:  # 'shrink'
        modified_mask = np.array(1 - binary_dilation(1 - mask, structure=structure))

    return modified_mask.astype(mask.dtype)
