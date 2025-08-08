import time
import logging

import numpy as np
import asf_search
import shapely.geometry
import shapely.wkt
import geopandas as gpd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def validate_aoi(aoi):
    """
    Validate and normalize an AOI into a WKT polygon string.

    Args:
        aoi (str, list, shapely geometry, geopandas.GeoDataFrame/GeoSeries):
            - WKT string
            - List of polygon coordinates [[x1,y1], [x2,y2], ...]
            - List of [minx, miny, maxx, maxy]
            - Shapely geometry
            - GeoDataFrame or GeoSeries

    Returns:
        str: WKT polygon string
    """
    logger.debug(f"Validating AOI of type {type(aoi)}")

    if isinstance(aoi, str):
        try:
            geom = shapely.wkt.loads(aoi)
        except Exception:
            raise ValueError("String input could not be parsed as WKT.")

    elif isinstance(aoi, (gpd.GeoDataFrame, gpd.GeoSeries)):
        if aoi.empty:
            raise ValueError("GeoDataFrame/GeoSeries is empty.")
        geom = aoi.geometry.iloc[0] if isinstance(aoi, gpd.GeoDataFrame) else aoi.iloc[0]

    elif isinstance(aoi, shapely.geometry.base.BaseGeometry):
        geom = aoi

    elif isinstance(aoi, list):
        if len(aoi) == 4 and all(isinstance(v, (int, float)) for v in aoi):
            geom = shapely.geometry.box(*aoi)
        elif all(isinstance(coord, (list, tuple)) and len(coord) == 2 for coord in aoi):
            geom = shapely.geometry.Polygon(aoi)
        else:
            raise ValueError(
                "List input must be bounding box [minx, miny, maxx, maxy] or list of [x,y] coords."
            )
    else:
        raise TypeError(
            "AOI must be WKT string, coordinate list, bounding box list, shapely geometry, or GeoDataFrame/GeoSeries."
        )

    if geom.geom_type != "Polygon":
        raise ValueError(f"AOI must be a Polygon, not {geom.geom_type}.")
    if not geom.is_valid:
        raise ValueError("AOI polygon is not valid.")

    wkt = geom.wkt
    logger.debug(f"AOI validated and converted to WKT: {wkt}")
    return wkt


def check_results(results, aoi):
    """
    Filter ASFSearchResults to only those whose geometry intersects the AOI.

    Args:
        results (list): ASFSearchResult-like objects with `.geometry` dict (GeoJSON).
        aoi: Any AOI format accepted by validate_aoi().

    Returns:
        list: Subset of results whose geometries intersect the AOI polygon.
    """
    aoi_wkt = validate_aoi(aoi)
    aoi_geom = shapely.wkt.loads(aoi_wkt)
    matching = []

    logger.info(f"Filtering {len(results)} results for intersection with AOI polygon")
    for product in results:
        try:
            product_geom = shapely.geometry.shape(product.geometry)
        except Exception as e:
            raise ValueError(f"Could not parse geometry for {product}: {e}")

        if product_geom.intersects(aoi_geom):
            matching.append(product)

    logger.info(f"{len(matching)} results intersect AOI")
    return matching


def check_relative_orbits(relative_orbit):
    """
    Normalize and validate relative_orbit input.

    Args:
        relative_orbit: None, int, float, str, list, or numpy array.

    Returns:
        list[int] or None: List of orbit numbers (0–175) or None.
    """
    if relative_orbit is None:
        logger.debug("No relative_orbit specified, returning None")
        return None

    if isinstance(relative_orbit, np.ndarray):
        relative_orbit = relative_orbit.tolist()

    if isinstance(relative_orbit, (int, float, str)):
        relative_orbit = [relative_orbit]

    if not isinstance(relative_orbit, list):
        raise TypeError("relative_orbit must be None, int, float, str, list, or numpy array.")

    try:
        relative_orbit = [int(v) for v in relative_orbit]
    except Exception:
        raise ValueError("All relative_orbit values must be convertible to int.")

    if not all(0 <= v <= 175 for v in relative_orbit):
        raise ValueError("All relative_orbit values must be between 0 and 175 inclusive.")

    logger.debug(f"Validated relative_orbit values: {relative_orbit}")
    return relative_orbit


def find_static_opera_files(aoi, relative_orbit=None, max_retries=10, retry_delay=5):
    """
    Find static OPERA RTC files that overlap AOI, with retry support.

    Args:
        aoi: AOI in any format supported by validate_aoi().
        relative_orbit: None, int, float, str, list, or numpy array.
        max_retries (int): Maximum number of ASF search attempts.
        retry_delay (int | float): Seconds to wait between retries.

    Returns:
        list: Search results intersecting AOI.
    """
    relative_orbit = check_relative_orbits(relative_orbit)
    validate_aoi(aoi)

    search_kwargs = dict(
        dataset=[asf_search.constants.DATASET.OPERA_S1],
        platform=[asf_search.PLATFORM.SENTINEL1],
        intersectsWith=aoi,
        maxResults=500,
        processingLevel=[asf_search.constants.RTC_STATIC],
    )
    if relative_orbit is not None:
        search_kwargs["relativeOrbit"] = relative_orbit

    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"ASF search attempt {attempt}/{max_retries} for AOI and relative orbit {relative_orbit}")
            results = asf_search.search(**search_kwargs)
            filtered = check_results(results, aoi)
            logger.info(f"Found {len(filtered)} matching results")
            return filtered
        except Exception as e:
            logger.warning(f"ASF search attempt {attempt} failed: {e}")
            last_exception = e
            if attempt < max_retries:
                time.sleep(retry_delay)

    raise RuntimeError(f"ASF search failed after {max_retries} attempts") from last_exception
