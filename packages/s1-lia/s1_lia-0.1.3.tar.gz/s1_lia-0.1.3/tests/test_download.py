import sys
sys.path.append('/Users/zmhoppinen/Documents/s1_lia/')
# Assuming functions are imported like:
from s1_lia.download import (
    check_directory, 
    generate_name_stem, 
    find_unique_relative_orbits, 
    download_results, 
    merge_lia_by_relative_orbit)

import pytest
from unittest.mock import patch, Mock, MagicMock

import numpy as np
from pathlib import Path

# check_directory tests

def test_check_directory_creates(tmp_path):
    new_dir = tmp_path / "new_folder"
    result = check_directory(str(new_dir))
    assert isinstance(result, Path)
    assert result.exists()
    assert result.is_dir()

def test_check_directory_existing(tmp_path):
    existing_dir = tmp_path
    result = check_directory(existing_dir)
    assert isinstance(result, Path)
    assert result.exists()
    assert result.is_dir()

def test_check_directory_not_a_dir(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello")
    with pytest.raises(NotADirectoryError):
        check_directory(file_path)

# 5. generate_name_stem tests

def test_generate_name_stem_centroid_only():
    wkt = 'POLYGON((-107.5 37.6,-107.5 38.0,-108.0 38.0,-108.0 37.6,-107.5 37.6))'
    stem = generate_name_stem(wkt, use_place_name=False)
    assert stem.startswith("AOI_")
    assert "_" in stem

def test_generate_name_stem_invalid_aoi():
    with pytest.raises(ValueError):
        generate_name_stem("INVALID_WKT", use_place_name=False)

# Mock the requests.get call for reverse geocoding
@patch("requests.get")
def test_generate_name_stem_with_place_name(mock_get):
    # Mock successful reverse geocode response
    mock_resp = Mock()
    mock_resp.ok = True
    mock_resp.json.return_value = {
        "address": {
            "town": "TestTown"
        }
    }
    mock_get.return_value = mock_resp

    wkt = 'POLYGON((-107.5 37.6,-107.5 38.0,-108.0 38.0,-108.0 37.6,-107.5 37.6))'
    stem = generate_name_stem(wkt, use_place_name=True)
    assert stem.startswith("TestTown_")

    # -------------------------
# check_directory tests
# -------------------------
def test_check_directory_creates(tmp_path):
    test_dir = tmp_path / "newdir"
    result = check_directory(test_dir)
    assert result.exists()
    assert result.is_dir()

def test_check_directory_existing_dir(tmp_path):
    result = check_directory(tmp_path)
    assert result == tmp_path

def test_check_directory_path_exists_but_not_dir(tmp_path):
    file_path = tmp_path / "afile"
    file_path.write_text("test")
    with pytest.raises(NotADirectoryError):
        check_directory(file_path)


# -------------------------
# download_results tests
# -------------------------
def test_download_results_calls_asf_search(tmp_path):
    mock_result = MagicMock()
    mock_result.get_urls.return_value = ["https://example.com/file_incidence_angle.tif"]

    with patch("s1_lia.download.asf_search.download_url") as mock_dl, \
         patch("s1_lia.download.check_directory", return_value=tmp_path):
        download_results([mock_result], tmp_path)
        mock_dl.assert_called_once_with(
            "https://example.com/file_local_incidence_angle.tif", tmp_path
        )


# -------------------------
# find_unique_relative_orbits tests
# -------------------------
def test_find_unique_relative_orbits(tmp_path):
    # Create mock files
    (tmp_path / "OPERA_L2_RTC-S1-STATIC_T123_xyz_local_incidence_angle.tif").touch()
    (tmp_path / "OPERA_L2_RTC-S1-STATIC_T045_xyz_local_incidence_angle.tif").touch()

    result = find_unique_relative_orbits(tmp_path)
    assert np.all(np.isin([45, 123], result))


# -------------------------
# generate_name_stem tests
# -------------------------
@patch("s1_lia.download.validate_aoi", return_value="POLYGON((0 0,1 0,1 1,0 1,0 0))")
@patch("s1_lia.download.requests.get")
def test_generate_name_stem_with_place_name(mock_get, mock_validate):
    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_resp.json.return_value = {"address": {"town": "TestTown"}}
    mock_get.return_value = mock_resp

    name = generate_name_stem("dummy")
    assert name.startswith("TestTown_")

@patch("s1_lia.download.validate_aoi", return_value="POLYGON((0 0,1 0,1 1,0 1,0 0))")
@patch("s1_lia.download.requests.get", side_effect=Exception("API error"))
def test_generate_name_stem_fallback(mock_get, mock_validate):
    name = generate_name_stem("dummy", use_place_name=True)
    assert name.startswith("AOI_")


# -------------------------
# merge_lia_by_relative_orbit tests
# -------------------------
@patch("s1_lia.download.find_unique_relative_orbits", return_value=[42])
@patch("s1_lia.download.merge_arrays", return_value=MagicMock(attrs={"_FillValue": 0}))
@patch("s1_lia.download.xr.open_dataarray")
def test_merge_lia_by_relative_orbit(mock_open_da, mock_merge, mock_find_unique, tmp_path):
    # Prepare mocks
    mock_da = MagicMock()
    mock_da.squeeze.return_value = mock_da
    mock_open_da.return_value = mock_da

    output_dir = tmp_path / "out"
    output_dir.mkdir()

    # Create dummy matching file path
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "file_T042_xyz_local_incidence_angle.tif").touch()

    merged_mock = MagicMock(attrs={"_FillValue": 0})
    merged_mock.rio.to_raster = MagicMock()
    mock_merge.return_value = merged_mock

    merge_lia_by_relative_orbit(data_dir, output_dir, "stem")

    mock_merge.assert_called_once()
    assert "_FillValue" not in merged_mock.attrs
    merged_mock.rio.to_raster.assert_called_once()
