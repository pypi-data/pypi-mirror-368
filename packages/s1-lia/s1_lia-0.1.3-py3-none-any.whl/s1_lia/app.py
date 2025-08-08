import logging
from pathlib import Path

from .search import find_static_opera_files
from .download import download_results, merge_lia_by_relative_orbit, generate_name_stem

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_opera_lia(
    aoi,
    data_dir,
    relative_orbit=None,
    file_stem=None,
    max_download_retries=20,
    download_retry_delay=2,
    max_search_retries=20,
    search_retry_delay=2,
):
    """
    Run full workflow: search, download, merge OPERA local incidence angle files.

    Args:
        aoi (str or geometry): AOI (WKT or other supported format).
        data_dir (str or Path): Directory to save downloads and outputs.
        relative_orbit (optional): Filter for orbit number(s).
        file_stem (optional): Custom stem for output files. If None, derived from AOI.
        max_download_retries, download_retry_delay: Retry config for downloads.
        max_search_retries, search_retry_delay: Retry config for ASF search.

    Returns:
        list[Path]: Paths of merged incidence angle TIFFs.
    """
    logger.info("Starting OPERA LIA workflow")

    results = find_static_opera_files(
        aoi,
        relative_orbit=relative_orbit,
        max_retries=max_search_retries,
        retry_delay=search_retry_delay,
    )

    if not results:
        logger.warning("No matching OPERA static files found for given AOI and orbit.")
        return []

    logger.info(f"Found {len(results)} matching results")

    downloaded_files = download_results(
        results,
        data_directory=data_dir,
        max_retries=max_download_retries,
        retry_delay=download_retry_delay,
    )

    stem = file_stem or generate_name_stem(aoi)
    logger.info(f"Using file stem: {stem}")

    merged_files = merge_lia_by_relative_orbit(downloaded_files, data_dir, stem)

    logger.info(f"Merged files saved: {merged_files}")

    return merged_files


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m s1_lia.app '<AOI WKT>' <data_directory>")
        sys.exit(1)

    aoi_wkt = sys.argv[1]
    data_directory = Path(sys.argv[2])
    get_opera_lia(aoi_wkt, data_directory)
