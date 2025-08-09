# multisat/converter.py

import os
import glob
import rasterio
from rasterio.enums import Resampling
from rasterio.shutil import copy as rio_copy
from osgeo import gdal
import numpy as np

def get_format(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.jp2']:
        return "JP2"
    elif ext in ['.tif', '.tiff']:
        return "GeoTIFF"
    elif ext in ['.hdf', '.nc']:
        return "HDF"
    elif ext == '':
        if "SAFE" in file_path:
            return "SAFE"
    return "UNKNOWN"

def convert_jp2_to_geotiff(input_path, output_path):
    """
    Convert JP2 (JPEG2000) to GeoTIFF using GDAL.
    """
    gdal.Translate(output_path, input_path, format='GTiff')

def convert_hdf_to_geotiff(input_path, output_dir):
    """
    Convert HDF or NetCDF files to GeoTIFF bands.
    """
    hdf_dataset = gdal.Open(input_path)
    if hdf_dataset is None:
        raise Exception("Could not open HDF/NetCDF file.")

    subdatasets = hdf_dataset.GetSubDatasets()
    output_files = []

    for i, (subdataset_path, description) in enumerate(subdatasets):
        out_path = os.path.join(output_dir, f"band_{i+1}.tif")
        gdal.Translate(out_path, subdataset_path, format='GTiff')
        output_files.append(out_path)

    return output_files

def extract_safe_bands(safe_dir, output_dir, band_ids=["B02", "B03", "B04", "B08"]):
    """
    Extract specific bands from Sentinel-2 .SAFE folders.

    Args:
        safe_dir (str): Path to .SAFE folder.
        output_dir (str): Where to save extracted GeoTIFF bands.
        band_ids (list): List of band IDs to extract.
    Returns:
        List of saved band paths.
    """
    granule_path = glob.glob(os.path.join(safe_dir, "GRANULE/*/IMG_DATA/*"))[0]
    extracted_bands = []

    for band_id in band_ids:
        jp2_path = glob.glob(os.path.join(granule_path, f"*_{band_id}_*.jp2"))
        if not jp2_path:
            print(f"[WARNING] Band {band_id} not found.")
            continue

        input_jp2 = jp2_path[0]
        output_tif = os.path.join(output_dir, f"{band_id}.tif")
        convert_jp2_to_geotiff(input_jp2, output_tif)
        extracted_bands.append(output_tif)

    return extracted_bands

def convert_any_to_geotiff(input_path, output_dir):
    """
    Master function: Detect format and convert to GeoTIFF.
    """
    fmt = get_format(input_path)
    os.makedirs(output_dir, exist_ok=True)

    if fmt == "JP2":
        output_path = os.path.join(output_dir, os.path.basename(input_path).replace(".jp2", ".tif"))
        convert_jp2_to_geotiff(input_path, output_path)
        return [output_path]

    elif fmt == "HDF":
        return convert_hdf_to_geotiff(input_path, output_dir)

    elif fmt == "SAFE":
        return extract_safe_bands(input_path, output_dir)

    elif fmt == "GeoTIFF":
        print("[INFO] Already in GeoTIFF format.")
        return [input_path]

    else:
        raise ValueError(f"Unsupported format: {fmt}")

def stack_bands(band_paths, output_path):
    """
    Stack multiple single-band GeoTIFFs into one multi-band GeoTIFF.

    Parameters:
        band_paths (list): Paths to individual band GeoTIFFs.
        output_path (str): Path to save stacked output.
    """
    sample = rasterio.open(band_paths[0])
    meta = sample.meta
    meta.update(count=len(band_paths))

    with rasterio.open(output_path, 'w', **meta) as dst:
        for i, band_path in enumerate(band_paths):
            with rasterio.open(band_path) as band:
                dst.write(band.read(1), i + 1)
