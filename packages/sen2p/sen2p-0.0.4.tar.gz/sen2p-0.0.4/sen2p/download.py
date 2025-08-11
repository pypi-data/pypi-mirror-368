import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple

from tqdm import tqdm
import xarray as xr
import rioxarray as rxr
import geopandas as gpd
import rasterio
from shapely.geometry import mapping, Point, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from rasterio.enums import Resampling
from pystac_client import Client
import planetary_computer as pc
from shapely.geometry import shape as shapely_shape

# -----------------------------
# Helper Functions
# -----------------------------

def clean_geometry_to_wgs84(gdf: gpd.GeoDataFrame) -> Tuple[BaseGeometry, List[float]]:
    """
    Reproject GeoDataFrame to EPSG:4326, fix invalid geometries, simplify, and union.
    
    Args:
        gdf: Input GeoDataFrame with geometries.
    
    Returns:
        Tuple containing:
        - Unified geometry (BaseGeometry).
        - Bounding box as [minx, miny, maxx, maxy].
    
    Raises:
        ValueError: If GeoDataFrame is empty or lacks a CRS.
    """
    if gdf.empty:
        raise ValueError("Input GeoDataFrame is empty.")
    if gdf.crs is None:
        raise ValueError("Input GeoDataFrame has no CRS defined.")

    # Reproject to WGS84 (EPSG:4326)
    gdf = gdf.to_crs(4326)

    # Buffer non-polygonal geometries (points/lines) to create areas
    geom_types = set(gdf.geom_type.str.lower())
    if geom_types.issubset({"point", "multipoint", "linestring", "multilinestring"}):
        gdf["geometry"] = gdf.geometry.buffer(0.0005)  # ~50m in degrees

    # Fix invalid geometries and simplify
    gdf["geometry"] = gdf.geometry.buffer(0)  # Fix invalid geometries
    gdf["geometry"] = gdf.geometry.simplify(0.0001, preserve_topology=True)

    geometry = unary_union(gdf.geometry)
    if geometry.is_empty:
        raise ValueError("Unified geometry is empty after processing.")

    bbox = list(gdf.total_bounds)  # [minx, miny, maxx, maxy]
    return geometry, bbox

def convert_location_to_geojson(location: Union[List[float], Dict[str, Any], str]) -> Tuple[Dict[str, Any], Optional[List[float]]]:
    """
    Convert location input to a GeoJSON geometry dictionary (EPSG:4326).
    
    Args:
        location: Either [lon, lat], [min_lon, min_lat, max_lon, max_lat], GeoJSON dict, or path to .shp/.geojson/.json file.
    
    Returns:
        Tuple containing:
        - GeoJSON geometry dictionary.
        - Optional bounding box [minx, miny, maxx, maxy] if derived from a file or bounding box input.
    
    Raises:
        ValueError: If location format is invalid or bounding box coordinates are invalid.
    """
    if isinstance(location, list):
        if len(location) == 2:
            lon, lat = location
            return mapping(Point(lon, lat)), None
        elif len(location) == 4:
            min_lon, min_lat, max_lon, max_lat = location
            if not (-180 <= min_lon <= max_lon <= 180 and -90 <= min_lat <= max_lat <= 90):
                raise ValueError("Invalid bounding box coordinates: must be [min_lon, min_lat, max_lon, max_lat] with min_lon <= max_lon and min_lat <= max_lat")
            geometry = box(min_lon, min_lat, max_lon, max_lat)
            return mapping(geometry), [min_lon, min_lat, max_lon, max_lat]
        else:
            raise ValueError("Location list must have 2 elements [lon, lat] or 4 elements [min_lon, min_lat, max_lon, max_lat]")

    if isinstance(location, dict):
        return location, None  # Assume valid GeoJSON in EPSG:4326

    if isinstance(location, str):
        path = Path(location)
        if path.suffix.lower() in {".shp", ".geojson", ".json"}:
            gdf = gpd.read_file(location, engine="fiona")
            geometry, bbox = clean_geometry_to_wgs84(gdf)
            return mapping(geometry), bbox

    raise ValueError("Location must be [lon, lat], [min_lon, min_lat, max_lon, max_lat], GeoJSON dict, or path to .shp/.geojson/.json file")

def print_aoi_info(geometry_dict: Dict[str, Any], bbox: Optional[List[float]]) -> None:
    """
    Print Area of Interest (AOI) details, including centroid and bounds.
    
    Args:
        geometry_dict: GeoJSON geometry dictionary.
        bbox: Optional bounding box [minx, miny, maxx, maxy].
    
    Raises:
        ValueError: If geometry is invalid.
    """
    geometry = shapely_shape(geometry_dict)
    cx, cy = geometry.centroid.coords[0]
    minx, miny, maxx, maxy = geometry.bounds

    print("📍 Area of Interest (WGS84)")
    print(f"   • Centroid:   lat={cy:.6f}, lon={cx:.6f}")
    print(f"   • Bounds:     [min_lon={minx:.6f}, min_lat={miny:.6f}, max_lon={maxx:.6f}, max_lat={maxy:.6f}]")
    if bbox:
        print(f"   • BBOX (fallback): [min_lon={bbox[0]:.6f}, min_lat={bbox[1]:.6f}, max_lon={bbox[2]:.6f}, max_lat={bbox[3]:.6f}]")

def search_stac_items(catalog: Client, geometry: Dict[str, Any], bbox: Optional[List[float]], 
                     start_date: str, end_date: str, max_items: Optional[int], collection: str) -> List[Any]:
    """
    Search STAC catalog for items matching geometry, date range, and collection.
    
    Args:
        catalog: STAC client instance.
        geometry: GeoJSON geometry dictionary.
        bbox: Optional bounding box for fallback search.
        start_date: Start date (YYYY-MM-DD).
        end_date: End date (YYYY-MM-DD).
        max_items: Maximum number of items to retrieve; if None, fetch all available items.
        collection: STAC collection ID (e.g., "sentinel-2-l2a").
    
    Returns:
        List of STAC items.
    
    Raises:
        ValueError: If no items are found.
    """
    # If max_items is None, perform a preliminary search to count available items
    if max_items is None:
        preliminary_search = catalog.search(
            collections=[collection],
            intersects=geometry,
            datetime=f"{start_date}/{end_date}",
            max_items=1000,  # Large enough to estimate total items
        )
        items = list(preliminary_search.get_items())
        max_items = len(items)
        if not items and bbox:
            preliminary_search = catalog.search(
                collections=[collection],
                bbox=bbox,
                datetime=f"{start_date}/{end_date}",
                max_items=1000,
            )
            items = list(preliminary_search.get_items())
            max_items = len(items)
    else:
        items = []

    # Perform actual search with determined max_items
    try:
        search = catalog.search(
            collections=[collection],
            intersects=geometry,
            datetime=f"{start_date}/{end_date}",
            max_items=max_items,
        )
        items = list(search.get_items())
        if not items and bbox:
            search = catalog.search(
                collections=[collection],
                bbox=bbox,
                datetime=f"{start_date}/{end_date}",
                max_items=max_items,
            )
            items = list(search.get_items())
    except Exception:
        if not bbox:
            raise
        search = catalog.search(
            collections=[collection],
            bbox=bbox,
            datetime=f"{start_date}/{end_date}",
            max_items=max_items,
        )
        items = list(search.get_items())

    if not items:
        raise ValueError("No items found for the given location and date range.")
    
    return items

def process_band(band: str, item: Any, item_output_dir: Optional[str], overwrite: bool, 
                show_progress: bool, tqdm_iter: Any) -> Tuple[Optional[str], Optional[xr.DataArray]]:
    """
    Process a single band, downloading and saving if required.
    
    Args:
        band: Band name (e.g., "B02").
        item: STAC item.
        item_output_dir: Directory to save band file.
        overwrite: Overwrite existing files.
        show_progress: Show progress updates.
        tqdm_iter: tqdm iterator for progress updates.
    
    Returns:
        Tuple containing:
        - File path (if saved) or None.
        - xarray DataArray (if needed for merging) or None.
    """
    href = item.assets[band].href
    file_path = os.path.join(item_output_dir, f"{item.id}_{band}.tif") if item_output_dir else None

    if file_path and os.path.exists(file_path) and not overwrite:
        if show_progress:
            tqdm_iter.write(f"Reusing existing file: {file_path}")
        return file_path, rxr.open_rasterio(file_path) if item_output_dir else None

    if show_progress and hasattr(tqdm_iter, "set_description"):
        tqdm_iter.set_description(f"{item.id}: {band}")

    band_array = rxr.open_rasterio(href)
    if file_path:
        band_array.rio.to_raster(file_path, tags={"CLOUD_COVER": str(item.properties.get("eo:cloud_cover", "N/A"))})
        if show_progress:
            tqdm_iter.write(f"Saved: {file_path}")
    
    return file_path, band_array

def merge_bands_into_geotiff(band_data: List[Tuple[str, xr.DataArray]], band_names: List[str], item_id: str, 
                            item_output_dir: str, merged_filename: Optional[str], cell_size: Optional[float], 
                            overwrite: bool, show_progress: bool) -> str:
    """
    Merge multiple bands into a single GeoTIFF.
    
    Args:
        band_data: List of (band_name, DataArray) tuples.
        band_names: List of band names.
        item_id: STAC item ID.
        item_output_dir: Directory to save merged file.
        merged_filename: Optional custom filename for merged file.
        cell_size: Target resolution in meters; inferred if None.
        overwrite: Overwrite existing merged file.
        show_progress: Show progress updates.
    
    Returns:
        Path to the merged GeoTIFF file.
    """
    merged_path = os.path.join(item_output_dir, merged_filename or f"{item_id}_merged.tif")
    if os.path.exists(merged_path) and not overwrite:
        if show_progress:
            print(f"Reusing existing merged file: {merged_path}")
        return merged_path

    # Infer cell size from first band if not provided
    if cell_size is None:
        cell_size = abs(band_data[0][1].rio.transform()[0]) or 10.0  # Default to 10m for Sentinel-2

    # Resample bands to common grid
    resampled_arrays = []
    for _, band_array in band_data:
        current_res = abs(band_array.rio.transform()[0])
        if abs(current_res - cell_size) > 0.01:
            resampling = Resampling.bilinear if current_res < cell_size else Resampling.nearest
            resampled = band_array.rio.reproject(band_array.rio.crs, resolution=(cell_size, cell_size), resampling=resampling)
            resampled_arrays.append(resampled)
        else:
            resampled_arrays.append(band_array)

    # Merge bands
    merged = xr.concat(resampled_arrays, dim="band")
    merged.attrs["description"] = f"Merged bands: {', '.join(band_names)}"
    merged.rio.to_raster(
        merged_path,
        tags={"BAND_NAMES": ",".join(band_names), "CLOUD_COVER": str(band_data[0][1].attrs.get("CLOUD_COVER", "N/A"))},
        descriptions=band_names,
    )
    
    if show_progress:
        print(f"Merged file written: {merged_path}")
    
    return merged_path

def check_all_files_exist(item_id: str, bands_to_download: List[str], item_output_dir: str, 
                          merge_bands: bool, merged_filename: Optional[str]) -> bool:
    """
    Check if all required files (bands and merged GeoTIFF) exist for an item.
    
    Args:
        item_id: STAC item ID.
        bands_to_download: List of band names to check.
        item_output_dir: Directory where files are stored.
        merge_bands: Whether to check for the merged GeoTIFF.
        merged_filename: Custom filename for the merged GeoTIFF, if any.
    
    Returns:
        True if all required files exist, False otherwise.
    """
    # Check individual band files
    for band in bands_to_download:
        band_path = os.path.join(item_output_dir, f"{item_id}_{band}.tif")
        if not os.path.exists(band_path):
            return False
    
    # Check merged file if required
    if merge_bands:
        merged_path = os.path.join(item_output_dir, merged_filename or f"{item_id}_merged.tif")
        if not os.path.exists(merged_path):
            return False
    
    return True

# -----------------------------
# Core Download Function
# -----------------------------

def download(
    start_date: str,
    end_date: str,
    location: Union[List[float], Dict[str, Any], str],
    bands: Optional[List[str]] = None,
    output_dir: Optional[str] = None,
    show_progress: bool = True,
    merge_bands: bool = True,
    merged_filename: Optional[str] = None,
    overwrite: bool = False,
    cell_size: Optional[float] = None,
    max_items: Optional[int] = None,
    collection: str = "sentinel-2-l2a",
) -> List[Dict[str, Any]]:
    """
    Download Sentinel-2 imagery from Microsoft Planetary Computer.
    
    Args:
        start_date: Start date in ISO format (YYYY-MM-DD).
        end_date: End date in ISO format (YYYY-MM-DD).
        location: Either [lon, lat], [min_lon, min_lat, max_lon, max_lat], GeoJSON dict, or path to .shp/.geojson/.json file.
        bands: List of band names (e.g., ["B02", "B03"]); if None, downloads all available bands.
        output_dir: Directory to save files; creates subfolders per item ID.
        show_progress: Display progress bars and logs.
        merge_bands: Merge bands into a single GeoTIFF if True (default: True, optional).
        merged_filename: Custom filename for merged GeoTIFF; defaults to "<item_id>_merged.tif".
        overwrite: Overwrite existing files if True.
        cell_size: Target resolution in meters for merged output; inferred if None.
        max_items: Maximum number of STAC items to retrieve; if None, uses total available items.
        collection: STAC collection ID (default: "sentinel-2-l2a").
    
    Returns:
        List of dictionaries containing item metadata and file paths or DataArrays.
    
    Raises:
        ValueError: If no items are found or location is invalid.
    """
    # Initialize STAC client
    catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)

    # Convert location to GeoJSON
    geometry, bbox = convert_location_to_geojson(location)
    print_aoi_info(geometry, bbox)

    # Search for STAC items
    items = search_stac_items(catalog, geometry, bbox, start_date, end_date, max_items, collection)

    # Prepare output directory
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    results = []
    for item in items:
        item_id = item.id
        available_bands = [asset for asset in item.assets.keys() if asset.upper().startswith("B")]
        cloud_cover = item.properties.get("eo:cloud_cover", "N/A")

        # Select bands to download
        bands_to_download = available_bands if bands is None else bands
        missing_bands = [b for b in bands_to_download if b not in available_bands]
        if missing_bands:
            if show_progress:
                print(f"Skipping {item_id}: missing bands {missing_bands}")
            continue

        # Prepare item output directory
        item_output_dir = os.path.join(output_dir, item_id) if output_dir else None
        if item_output_dir:
            os.makedirs(item_output_dir, exist_ok=True)

        # Check if all required files already exist
        if item_output_dir and not overwrite:
            if check_all_files_exist(item_id, bands_to_download, item_output_dir, merge_bands, merged_filename):
                if show_progress:
                    print(f"All files for {item_id} already exist, skipping download.")
                result = {"item_id": item_id, "cloud_cover": cloud_cover}
                for band in bands_to_download:
                    result[band] = os.path.join(item_output_dir, f"{item_id}_{band}.tif")
                if merge_bands:
                    result["merged"] = os.path.join(item_output_dir, merged_filename or f"{item_id}_merged.tif")
                results.append(result)
                continue

        # Process each band
        result = {"item_id": item_id, "cloud_cover": cloud_cover}
        band_data = []
        band_names = []
        iterable = tqdm(bands_to_download, desc=f"Processing {item_id}") if show_progress else bands_to_download

        for band in iterable:
            file_path, band_array = process_band(band, item, item_output_dir, overwrite, show_progress, iterable)
            result[band] = file_path or band_array
            if merge_bands and band_array is not None:
                band_data.append((band, band_array))
                band_names.append(band)

        # Merge bands if requested
        if merge_bands and item_output_dir and band_data:
            result["merged"] = merge_bands_into_geotiff(band_data, band_names, item_id, item_output_dir, 
                                                       merged_filename, cell_size, overwrite, show_progress)

        results.append(result)

    return results

# -----------------------------
# Metadata Utility
# -----------------------------

def show_meta(file_path: str) -> None:
    """
    Display metadata for a raster file.
    
    Args:
        file_path: Path to the raster file.
    """
    da = rxr.open_rasterio(file_path)
    with rasterio.open(file_path) as src:
        tags = src.tags()

    print(f"📄 File: {file_path}")
    if "CLOUD_COVER" in tags:
        print(f"☁️ Cloud cover: {tags['CLOUD_COVER']}%")
    print(f"📐 Dimensions: {da.rio.width} x {da.rio.height}")
    print(f"📊 Number of bands: {da.rio.count}")
    print(f"🗺️ CRS: {da.rio.crs}")
    print(f"📏 Resolution: {da.rio.resolution()}")
    print(f"📌 Bounds: {da.rio.bounds()}")
    print(f"🧾 xarray attrs: {da.attrs}")

# -----------------------------
# Example CLI Usage
# -----------------------------

if __name__ == "__main__":
    results = download(
        start_date="2016-09-01",
        end_date="2016-09-10",
        location=[172.0, -43.6, 172.5, -43.3],  # Darfield, NZ bounding box
        bands=["B02", "B03", "B04", "B08"],
        output_dir="a_hurunui3",
        show_progress=True,
        # merge_bands omitted to use default (True)
        merged_filename=None,
        overwrite=False,
        cell_size=None,
        max_items=None,
        collection="sentinel-2-l2a",
    )

    for result in results:
        print(result)
        if "merged" in result:
            show_meta(result["merged"])