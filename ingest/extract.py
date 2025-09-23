import xarray as xr
import numpy as np
from pathlib import Path

def extract_metadata(file_path, entry_id):
    """
    Extracts only the fields required for the argo_profiles table.
    Returns None if the file cannot be processed.
    """
    try:
        ds = xr.open_dataset(file_path, decode_times=True, decode_timedelta=True)

        # PLATFORM_NUMBER → float_id
        float_id = None
        if 'PLATFORM_NUMBER' in ds:
            val = ds['PLATFORM_NUMBER'].values
            float_id = str(val.item()) if val.ndim == 0 else str(val[0])

        # JULD → profile_time
        profile_time = None
        if 'JULD' in ds:
            val = ds['JULD'].values
            if val.ndim == 0:
                profile_time = str(np.datetime_as_string(val, unit="s"))
            elif val.size > 0:
                profile_time = str(np.datetime_as_string(val[0], unit="s"))

        # LATITUDE & LONGITUDE
        lat = None
        lon = None
        if 'LATITUDE' in ds:
            val = ds['LATITUDE'].values
            lat = float(val) if val.ndim == 0 else float(val[0])
        if 'LONGITUDE' in ds:
            val = ds['LONGITUDE'].values
            lon = float(val) if val.ndim == 0 else float(val[0])

        # Depth range
        depth_range = [None, None]
        if 'PRES' in ds and ds['PRES'].size > 0:
            pres = ds['PRES'].values
            depth_range = [float(pres.min()), float(pres.max())]

        # Variables (fixed for your table)
        variables = ["temperature", "salinity"]

        metadata = {
            "entry_id": entry_id,
            "float_id": float_id,
            "profile_time": profile_time,
            "lat": lat,
            "lon": lon,
            "variables": variables,
            "depth_range": depth_range,
            "source_file": str(file_path)
        }

        ds.close()
        return metadata

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return None
