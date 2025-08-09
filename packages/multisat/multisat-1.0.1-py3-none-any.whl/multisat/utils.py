# multisat/utils.py

import rasterio
import numpy as np
import matplotlib.pyplot as plt
import os

def get_image_metadata(image_path):
    """
    Extract basic metadata from a GeoTIFF image.
    """
    with rasterio.open(image_path) as src:
        metadata = {
            "CRS": str(src.crs),
            "Resolution": src.res,
            "Width": src.width,
            "Height": src.height,
            "Bounds": src.bounds,
            "Band count": src.count,
            "Dtype": src.dtypes,
            "Driver": src.driver
        }
    return metadata

def detect_satellite_type(image_path):
    """
    Try to guess if the image is from Sentinel or Landsat based on resolution/bands.
    """
    with rasterio.open(image_path) as src:
        res = src.res[0]
        bands = src.count

        if res == 10 or res == 20:
            return "Sentinel-2"
        elif res == 30:
            return "Landsat (likely C2 L2)"
        elif res < 10:
            return "High-res (e.g., commercial)"
        else:
            return "Unknown"

def plot_bands(image_path, bands=[1, 2, 3], title="Image", stretch=True):
    """
    Plot selected bands from an image. Defaults to RGB.

    Args:
        image_path (str): GeoTIFF path.
        bands (list): List of 3 band indices (1-based).
        title (str): Plot title.
        stretch (bool): Whether to normalize bands for display.
    """
    with rasterio.open(image_path) as src:
        img = []
        for i in bands:
            band = src.read(i)
            if stretch:
                band = (band - band.min()) / (band.max() - band.min() + 1e-6)
            img.append(band)
        rgb = np.stack(img, axis=-1)
        plt.figure(figsize=(8, 8))
        plt.imshow(rgb)
        plt.title(title)
        plt.axis('off')
        plt.show()

def calculate_ndvi(image_path, red_band=3, nir_band=4, output_path=None):
    """
    Calculate NDVI = (NIR - Red) / (NIR + Red)

    Args:
        image_path (str): GeoTIFF with at least Red & NIR bands.
        red_band (int): Index of red band (1-based).
        nir_band (int): Index of NIR band (1-based).
        output_path (str): Save NDVI to this path if provided.
    Returns:
        NDVI array
    """
    with rasterio.open(image_path) as src:
        red = src.read(red_band).astype(np.float32)
        nir = src.read(nir_band).astype(np.float32)

        ndvi = (nir - red) / (nir + red + 1e-6)
        ndvi = np.clip(ndvi, -1, 1)

        if output_path:
            meta = src.meta.copy()
            meta.update({
                "count": 1,
                "dtype": 'float32'
            })
            with rasterio.open(output_path, 'w', **meta) as dst:
                dst.write(ndvi, 1)

        return ndvi

def print_band_stats(image_path):
    """
    Print min, max, mean, std for each band.
    """
    with rasterio.open(image_path) as src:
        for i in range(1, src.count + 1):
            band = src.read(i)
            print(f"Band {i}: min={band.min():.2f}, max={band.max():.2f}, mean={band.mean():.2f}, std={band.std():.2f}")
