# multisat/harmonizer.py

import rasterio
import numpy as np
from skimage.exposure import match_histograms
import os

def normalize_image(image_path, output_path, mode="0-1"):
    """
    Normalize a GeoTIFF image to [0,1] or [0,255].

    Args:
        image_path (str): Input GeoTIFF path.
        output_path (str): Output normalized GeoTIFF path.
        mode (str): "0-1" or "0-255"
    """
    with rasterio.open(image_path) as src:
        meta = src.meta.copy()
        data = src.read().astype(np.float32)

        norm_data = np.zeros_like(data)
        for i in range(data.shape[0]):
            band = data[i]
            band_min = band.min()
            band_max = band.max()
            if band_max - band_min == 0:
                norm_data[i] = 0
            else:
                norm = (band - band_min) / (band_max - band_min)
                norm_data[i] = norm * (255 if mode == "0-255" else 1)

        norm_data = norm_data.astype(np.uint8 if mode == "0-255" else np.float32)
        meta.update(dtype=norm_data.dtype)

        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(norm_data)

def match_histogram(source_path, reference_path, output_path):
    """
    Match the histogram of source image to that of reference image.

    Args:
        source_path (str): Path to image to adjust.
        reference_path (str): Path to image to match.
        output_path (str): Path to save adjusted image.
    """
    with rasterio.open(source_path) as src, rasterio.open(reference_path) as ref:
        src_data = src.read().astype(np.float32)
        ref_data = ref.read().astype(np.float32)

        matched = match_histograms(src_data, ref_data, channel_axis=0)

        meta = src.meta.copy()
        matched = matched.astype(src.meta['dtype'])

        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(matched)

def harmonize_bands(image_path, satellite_type, output_path):
    """
    Reorder or select bands to match a standard template (e.g., RGB or RGB-NIR).

    Args:
        image_path (str): Input GeoTIFF path (multi-band).
        satellite_type (str): 'sentinel' or 'landsat'.
        output_path (str): Output harmonized image.
    """
    with rasterio.open(image_path) as src:
        data = src.read()
        meta = src.meta.copy()

        if satellite_type.lower() == 'sentinel':
            # Sentinel-2 band order: B02 (Blue), B03 (Green), B04 (Red), B08 (NIR)
            band_indices = [2, 1, 0]  # B04, B03, B02 = RGB
        elif satellite_type.lower() == 'landsat':
            # Landsat 8: B4 (Red), B3 (Green), B2 (Blue)
            band_indices = [0, 1, 2]  # Already RGB in most cases
        else:
            raise ValueError("Unsupported satellite type.")

        harmonized_data = data[band_indices]
        meta.update(count=3)

        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(harmonized_data)

def apply_basic_cloud_mask(image_path, output_path, threshold=200):
    """
    Apply a basic cloud mask (intensity-based) to an RGB image.

    Args:
        image_path (str): Input path to image (RGB assumed).
        output_path (str): Output masked image.
        threshold (int): Brightness threshold to consider as cloud.
    """
    with rasterio.open(image_path) as src:
        data = src.read()
        meta = src.meta.copy()

        rgb = data[:3]
        avg = np.mean(rgb, axis=0)

        mask = avg < threshold
        masked_data = rgb * mask

        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(masked_data.astype(src.meta['dtype']))
