import pytest
from unittest.mock import patch, Mock
import numpy as np
from pathlib import Path

from shapely.geometry import Polygon, box, mapping
import geopandas as gpd
from shapely import wkt as shapely_wkt

import sys
sys.path.append('/Users/zmhoppinen/Documents/s1_lia/')
# Assuming functions are imported like:
from s1_lia.search import validate_aoi, check_results, check_relative_orbits, find_static_opera_files

# 1. validate_aoi tests
def test_validate_aoi_wkt():
    wkt = 'POLYGON((-107.5 37.6,-107.5 38.0,-108.0 38.0,-108.0 37.6,-107.5 37.6))'
    result = validate_aoi(wkt)
    assert result.startswith('POLYGON')

def test_validate_aoi_bbox_list():
    bbox = [-108.0, 37.6, -107.5, 38.0]
    result = validate_aoi(bbox)
    assert result.startswith('POLYGON')

def test_validate_aoi_coord_list():
    coords = [(-107.5, 37.6), (-107.5, 38.0), (-108.0, 38.0), (-108.0, 37.6), (-107.5, 37.6)]
    result = validate_aoi(coords)
    assert result.startswith('POLYGON')

def test_validate_aoi_shapely_geometry():
    geom = box(-108.0, 37.6, -107.5, 38.0)
    result = validate_aoi(geom)
    assert result.startswith('POLYGON')

def test_validate_aoi_invalid_type():
    with pytest.raises(TypeError):
        validate_aoi(123)

def test_validate_aoi_invalid_polygon():
    # Self-intersecting polygon
    bad_coords = [(0,0), (1,1), (1,0), (0,1), (0,0)]
    with pytest.raises(ValueError):
        validate_aoi(bad_coords)

def test_validate_aoi_wkt_string():
    wkt_str = "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))"
    result = validate_aoi(wkt_str)
    assert result == shapely_wkt.loads(wkt_str).wkt

def test_validate_aoi_invalid_wkt_string():
    with pytest.raises(ValueError):
        validate_aoi("NOT_A_WKT")

def test_validate_aoi_geodataframe():
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    gdf = gpd.GeoDataFrame(geometry=[poly])
    result = validate_aoi(gdf)
    assert result == poly.wkt

def test_validate_aoi_empty_geodataframe():
    gdf = gpd.GeoDataFrame(geometry=[])
    with pytest.raises(ValueError):
        validate_aoi(gdf)

def test_validate_aoi_shapely_geometry():
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert validate_aoi(poly) == poly.wkt

def test_validate_aoi_bbox_list():
    bbox = [0, 0, 1, 1]
    result = validate_aoi(bbox)
    assert result == box(*bbox).wkt

def test_validate_aoi_coord_list():
    coords = [(0, 0), (1, 0), (1, 1), (0, 1)]
    result = validate_aoi(coords)
    assert result == Polygon(coords).wkt

def test_validate_aoi_bad_list_format():
    with pytest.raises(ValueError):
        validate_aoi([1, 2, "bad", 4])

def test_validate_aoi_wrong_type():
    with pytest.raises(TypeError):
        validate_aoi(1234)

def test_validate_aoi_non_polygon_geometry():
    from shapely.geometry import Point
    with pytest.raises(ValueError):
        validate_aoi(Point(0, 0))

# 2. check_results tests
class DummyProduct:
    def __init__(self, geom_dict):
        self.geometry = geom_dict

def test_check_results_filtering():
    aoi = 'POLYGON((-107.0 37.5, -107.0 38.5, -108.0 38.5, -108.0 37.5, -107.0 37.5))'
    
    inside_geom = {
        'type': 'Polygon',
        'coordinates': [[[-107.5, 38.0], [-107.5, 38.1], [-107.6, 38.1], [-107.6, 38.0], [-107.5, 38.0]]]
    }
    outside_geom = {
        'type': 'Polygon',
        'coordinates': [[[-110, 40], [-110, 41], [-111, 41], [-111, 40], [-110, 40]]]
    }

    results = [DummyProduct(inside_geom), DummyProduct(outside_geom)]
    filtered = check_results(results, aoi)
    assert len(filtered) == 1
    assert filtered[0].geometry == inside_geom

def test_check_results_some_match():
    aoi = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    product1 = DummyProduct(Polygon([(1, 1), (2, 1), (2, 2), (1, 2)]))  # intersects
    product2 = DummyProduct(Polygon([(10, 10), (11, 10), (11, 11), (10, 11)]))  # no intersection
    results = [product1, product2]
    matches = check_results(results, aoi)
    assert matches == [product1]

def test_check_results_invalid_product_geometry():
    bad_result = DummyProduct(Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]))
    bad_result.geometry = {"invalid": "geom"}
    with pytest.raises(ValueError):
        check_results([bad_result], Polygon([(0, 0), (2, 0), (2, 2), (0, 2)]))


# 3. normalize_relative_orbit tests
def test_normalize_none():
    assert check_relative_orbits(None) is None

def test_normalize_single_int():
    assert check_relative_orbits(5) == [5]

def test_normalize_single_float():
    assert check_relative_orbits(10.0) == [10]

def test_normalize_single_str():
    assert check_relative_orbits("15") == [15]

def test_normalize_list_of_ints():
    assert check_relative_orbits([1, 2, 3]) == [1, 2, 3]

def test_normalize_numpy_array():
    arr = np.array([5, 10])
    assert check_relative_orbits(arr) == [5, 10]

def test_invalid_value_type():
    with pytest.raises(TypeError):
        check_relative_orbits({'a':1})

def test_unconvertible_value():
    with pytest.raises(ValueError):
        check_relative_orbits(['a'])

def test_value_out_of_range():
    with pytest.raises(ValueError):
        check_relative_orbits([0, 176])

def test_check_relative_orbits_none():
    assert check_relative_orbits(None) is None

def test_check_relative_orbits_single_int():
    assert check_relative_orbits(42) == [42]

def test_check_relative_orbits_numpy_array():
    arr = np.array([1, 2])
    assert check_relative_orbits(arr) == [1, 2]

def test_check_relative_orbits_string_convertible():
    assert check_relative_orbits("5") == [5]

def test_check_relative_orbits_invalid_type():
    with pytest.raises(TypeError):
        check_relative_orbits({1, 2})

def test_check_relative_orbits_unconvertible_value():
    with pytest.raises(ValueError):
        check_relative_orbits(["abc"])

def test_check_relative_orbits_out_of_range():
    with pytest.raises(ValueError):
        check_relative_orbits([200])