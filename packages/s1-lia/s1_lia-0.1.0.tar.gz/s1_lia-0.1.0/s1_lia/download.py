import logging
import time
import warnings
import urllib.parse
import re
from pathlib import Path

import asf_search
import numpy as np
import requests
import shapely.wkt
import xarray as xr
from rioxarray.merge import merge_arrays
from tqdm import tqdm

from .search import validate_aoi

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def check_directory(directory):
    directory = Path(directory)
    if not directory.exists():
        logger.info(f"Creating directory {directory}")
        directory.mkdir(parents=True, exist_ok=True)
    elif not directory.is_dir():
        raise NotADirectoryError(f"{directory} exists but is not a directory.")
    return directory


def download_results(results, data_directory, max_retries=3, retry_delay=2):
    """
    Download local incidence angle files from ASF search results.

    Returns a list of Paths to the downloaded files (constructed from URL filenames).
    """
    data_directory = check_directory(data_directory)
    downloaded_files = []

    for result in tqdm(results, desc="Downloading files"):
        try:
            url = result.get_urls()[0]
        except Exception as e:
            raise ValueError(f"Result object did not provide a URL: {e}")

        url = url.replace("_incidence_angle.tif", "_local_incidence_angle.tif")
        parsed_url = urllib.parse.urlparse(url)
        filename = Path(parsed_url.path).name
        if not filename:
            raise ValueError(f"Could not determine filename from URL: {url}")

        local_fp = data_directory / filename
        last_exc = None

        for attempt in range(1, max_retries + 1):
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore",
                        message=r"File already exists, skipping download.*",
                        category=UserWarning,
                        module="asf_search.download.download"
                    )
                    asf_search.download_url(url, data_directory)
                logger.info(f"Downloaded {filename} to {data_directory}")
                downloaded_files.append(local_fp)
                break
            except Exception as exc:
                last_exc = exc
                logger.warning(f"Attempt {attempt} failed to download {filename}: {exc}")
                if attempt < max_retries:
                    time.sleep(retry_delay)
        else:
            raise RuntimeError(f"Failed to download {url} after {max_retries} attempts") from last_exc

    return downloaded_files


def find_unique_relative_orbits(data_directory):
    data_directory = Path(data_directory)
    lia_files = list(data_directory.glob('*_local_incidence_angle.tif'))
    tracks = []
    for f in lia_files:
        # Extract orbit assuming pattern ..._T###_...
        match = re.search(r"_T(\d{3})", f.stem)
        if not match:
            raise ValueError(f"Could not extract orbit from filename: {f}")
        tracks.append(int(match.group(1)))
    unique_orbits = np.unique(tracks)
    logger.info(f"Found unique relative orbits: {unique_orbits}")
    return unique_orbits


def generate_name_stem(aoi, use_place_name=True):
    aoi_wkt = validate_aoi(aoi)
    geom = shapely.wkt.loads(aoi_wkt)

    centroid = geom.centroid
    lat = round(centroid.y, 4)
    lon = round(centroid.x, 4)

    if use_place_name:
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
            headers = {"User-Agent": "AOI-Name-Generator"}
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.ok:
                data = resp.json()
                town = (
                    data.get("address", {}).get("town")
                    or data.get("address", {}).get("city")
                    or data.get("address", {}).get("village")
                    or data.get("address", {}).get("county")
                )
                if town:
                    stem = f"{town.replace(' ', '_')}_{lat}_{lon}"
                    logger.info(f"Generated name stem from place: {stem}")
                    return stem
        except Exception as e:
            logger.warning(f"Reverse geocoding failed: {e}")

    stem = f"AOI_{lat}_{lon}"
    logger.info(f"Generated fallback name stem: {stem}")
    return stem


def merge_lia_by_relative_orbit(downloaded_files, output_directory, name_stem):
    """
    Merge local incidence angle files grouped by relative orbit.

    Args:
        downloaded_files (list of Path): Downloaded LIA files.
        output_directory (str or Path): Where merged files will be saved.
        name_stem (str): Prefix for output filenames.

    Returns:
        list of Path: Paths of merged output files.
    """
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    orbit_groups = {}
    for fp in downloaded_files:
        match = re.search(r"_T(\d{3})", fp.stem)
        if not match:
            raise ValueError(f"Could not extract relative orbit from filename: {fp}")
        orbit = int(match.group(1))
        orbit_groups.setdefault(orbit, []).append(fp)

    out_fps = []
    for orbit, files in orbit_groups.items():
        das = [xr.open_dataarray(fp).squeeze("band", drop=True) for fp in files]
        merged = merge_arrays(das)
        merged.attrs.pop("_FillValue", None)

        out_fp = output_directory / f"{name_stem}_{orbit:03d}_inc.tif"
        merged.rio.to_raster(out_fp)
        logger.info(f"Merged {len(files)} files for orbit {orbit} into {out_fp}")
        out_fps.append(out_fp)

    return out_fps
