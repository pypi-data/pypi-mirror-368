# multisat/resampler.py

import rasterio
from rasterio.enums import Resampling
import numpy as np
from rasterio.io import MemoryFile

def _get_resampling_method(method):
    methods = {
        "nearest": Resampling.nearest,
        "bilinear": Resampling.bilinear,
        "cubic": Resampling.cubic
    }
    return methods.get(method.lower(), Resampling.bilinear)

def match_resolution(
    input_path: str,
    output_path: str,
    target_resolution: float,
    method: str = "bilinear"
):
    """
    Resample a satellite image to the target spatial resolution.

    Parameters:
        input_path (str): Path to the input raster image.
        output_path (str): Path to save the resampled output image.
        target_resolution (float): Desired resolution in map units (e.g., meters).
        method (str): Resampling method: 'nearest', 'bilinear', or 'cubic'.
    """
    resampling_method = _get_resampling_method(method)

    with rasterio.open(input_path) as src:
        scale_x = src.res[0] / target_resolution
        scale_y = src.res[1] / target_resolution

        new_width = int(src.width * scale_x)
        new_height = int(src.height * scale_y)

        transform = src.transform * src.transform.scale(
            (src.width / new_width),
            (src.height / new_height)
        )

        kwargs = src.meta.copy()
        kwargs.update({
            "height": new_height,
            "width": new_width,
            "transform": transform
        })

        with rasterio.open(output_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                data = src.read(
                    i,
                    out_shape=(new_height, new_width),
                    resampling=resampling_method
                )
                dst.write(data, i)

def resample_to_match(source_path: str, reference_path: str, output_path: str, method: str = "bilinear"):
    """
    Resample source image to match the resolution and shape of the reference image.

    Parameters:
        source_path (str): Path to source image to be resampled.
        reference_path (str): Path to reference image to match.
        output_path (str): Path to save resampled image.
        method (str): Resampling method.
    """
    resampling_method = _get_resampling_method(method)

    with rasterio.open(reference_path) as ref:
        ref_res = ref.res
        ref_width = ref.width
        ref_height = ref.height
        ref_transform = ref.transform
        ref_crs = ref.crs

    with rasterio.open(source_path) as src:
        kwargs = src.meta.copy()
        kwargs.update({
            "height": ref_height,
            "width": ref_width,
            "transform": ref_transform,
            "crs": ref_crs
        })

        with rasterio.open(output_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                data = src.read(
                    i,
                    out_shape=(ref_height, ref_width),
                    resampling=resampling_method
                )
                dst.write(data, i)
