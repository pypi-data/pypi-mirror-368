#!/use/bin/env python
# coding=utf-8
# @Author  : Shuhao Liu
# @Time    : 2025/7/15 10:51 
# @File    : ResampleMask.py

import numpy as np
from scipy.ndimage import map_coordinates


def resample_global_mask(mask, lat, lon, target_resolution):
    """
    Resample global grid data to target resolution with (180, 360) convention

    Parameters:
        mask: 2D numpy array (n_lat, n_lon), 1=inside, 0=outside
        lat: 1D numpy array, in degrees
        lon: 1D numpy array, in degrees
        target_resolution: target resolution in degrees

    Returns:
        new_mask: resampled mask
        new_lat: new latitude grid
        new_lon: new longitude grid
    """
    # Input validation
    assert mask.ndim == 2, "Mask must be 2D array"
    lon2d, lat2d = np.meshgrid(lon, lat)
    assert lat2d.shape == mask.shape, "Latitude grid must match mask shape"
    assert lon2d.shape == mask.shape, "Longitude grid must match mask shape"

    # Calculate current resolution (assuming regular grid)
    current_resolution = np.abs(lat2d[1, 0] - lat2d[0, 0])

    # Calculate new grid dimensions (180×360 convention)
    n_lat = int(180 / target_resolution)
    n_lon = int(360 / target_resolution)

    # Create new regular lat/lon grids (cell-center coordinates)
    lat_edges = np.linspace(-90, 90, n_lat + 1)
    lon_edges = np.linspace(-180, 180, n_lon + 1)
    new_lat = (lat_edges[:-1] + lat_edges[1:]) / 2  # Cell centers
    new_lon = (lon_edges[:-1] + lon_edges[1:]) / 2
    new_lon2d, new_lat2d = np.meshgrid(new_lon, new_lat)

    # Upsampling (higher resolution)
    if target_resolution < current_resolution:
        # Convert geographic coords to array indices
        lat_idx = (lat2d + 90) / 180 * (mask.shape[0] - 1)
        lon_idx = (lon2d + 180) / 360 * (mask.shape[1] - 1)

        # Prepare interpolation coordinates for new grid
        interp_coords = np.array([new_lat2d.ravel(), new_lon2d.ravel()])
        interp_coords[0] = (interp_coords[0] + 90) / 180 * (mask.shape[0] - 1)
        interp_coords[1] = (interp_coords[1] + 180) / 360 * (mask.shape[1] - 1)

        # Perform bilinear interpolation
        new_mask = map_coordinates(mask, interp_coords, order=1, mode='nearest', cval=0)
        new_mask = new_mask.reshape((n_lat, n_lon))

        # Binarize the result
        new_mask = (new_mask > 0.5).astype(mask.dtype)

    # Downsampling (lower resolution)
    else:
        scale_factor = int(round(target_resolution / current_resolution))

        # Calculate new shape after integer scaling
        new_shape = (
            mask.shape[0] // scale_factor,
            mask.shape[1] // scale_factor
        )

        # Crop input to make it divisible by scale factor
        cropped_mask = mask[:new_shape[0] * scale_factor, :new_shape[1] * scale_factor]

        # Reshape into blocks for downsampling
        reshaped = cropped_mask.reshape(
            new_shape[0], scale_factor,
            new_shape[1], scale_factor
        )

        # Apply max pooling (logical OR for binary masks)
        new_mask = np.max(reshaped, axis=(1, 3))

        # Final trim to exact target size
        new_mask = new_mask[:n_lat, :n_lon]

    return new_mask, new_lat, new_lon
