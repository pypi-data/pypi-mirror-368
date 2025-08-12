from concurrent.futures import ThreadPoolExecutor
from itertools import product
from pathlib import Path

import numpy as np
import shapely
from hyp3lib.fetch import download_file
from osgeo import gdal
from shapely.geometry import LinearRing, Polygon, box


gdal.UseExceptions()
URL = 'https://nisar.asf.earthdatacloud.nasa.gov/STATIC/DEM/v1.1/EPSG4326'


def check_antimeridean(poly: Polygon) -> list[Polygon]:
    """Check if the polygon crosses the antimeridian and split the polygon if it does.

    Args:
        poly: Polygon object to check for antimeridian crossing.

    Returns:
        List of Polygon objects, split if necessary.
    """
    x_min, _, x_max, _ = poly.bounds

    # Check anitmeridean crossing
    if (x_max - x_min > 180.0) or (x_min <= 180.0 <= x_max):
        dateline = shapely.wkt.loads('LINESTRING( 180.0 -90.0, 180.0 90.0)')

        # build new polygon with all longitudes between 0 and 360
        x, y = poly.exterior.coords.xy
        new_x = (k + (k <= 0.0) * 360 for k in x)
        new_ring = LinearRing(zip(new_x, y))

        # Split input polygon
        # (https://gis.stackexchange.com/questions/232771/splitting-polygon-by-linestring-in-geodjango_)
        merged_lines = shapely.ops.linemerge([dateline, new_ring])
        border_lines = shapely.ops.unary_union(merged_lines)
        decomp = shapely.ops.polygonize(border_lines)

        polys = list(decomp)

        for polygon_count in range(len(polys)):
            x, y = polys[polygon_count].exterior.coords.xy
            # if there are no longitude values above 180, continue
            if not any([k > 180 for k in x]):
                continue

            # otherwise, wrap longitude values down by 360 degrees
            x_wrapped_minus_360 = np.asarray(x) - 360
            polys[polygon_count] = Polygon(zip(x_wrapped_minus_360, y))

    else:
        # If dateline is not crossed, treat input poly as list
        polys = [poly]

    return polys


def get_dem_granule_url(lat: int, lon: int) -> str:
    """Generate the URL for the OPERA DEM granule based on latitude and longitude.

    Args:
        lat: Latitude in degrees.
        lon: Longitude in degrees.

    Returns:
        URL string for the DEM granule.
    """
    lat_tens = np.floor_divide(lat, 10) * 10
    lat_cardinal = 'S' if lat_tens < 0 else 'N'

    lon_tens = np.floor_divide(lon, 20) * 20
    lon_cardinal = 'W' if lon_tens < 0 else 'E'

    prefix = f'{lat_cardinal}{np.abs(lat_tens):02d}_{lon_cardinal}{np.abs(lon_tens):03d}'
    filename = f'DEM_{lat_cardinal}{np.abs(lat):02d}_00_{lon_cardinal}{np.abs(lon):03d}_00.tif'
    file_url = f'{URL}/{prefix}/{filename}'
    return file_url


def get_latlon_pairs(polygon: Polygon) -> list[tuple[float, float]]:
    """Get latitude and longitude pairs for the bounding box of a polygon.

    Args:
        polygon: Polygon object representing the area of interest.

    Returns:
        List of tuples containing latitude and longitude pairs for each point of the bounding box.
    """
    minx, miny, maxx, maxy = polygon.bounds
    lats = np.arange(np.floor(miny), np.floor(maxy) + 1).astype(int)
    lons = np.arange(np.floor(minx), np.floor(maxx) + 1).astype(int)
    return list(product(lats, lons))


def download_opera_dem_for_footprint(output_path: Path, footprint: Polygon, buffer: float = 0.2) -> None:
    """
    Download the OPERA DEM for a given footprint and save it to the specified output path.

    Args:
        output_path: Path where the DEM will be saved.
        footprint: Polygon representing the area of interest.
        buffer: Buffer distance in degrees to extend the footprint.
    """
    output_dir = output_path.parent
    if output_path.exists():
        return output_path

    footprint = box(*footprint.buffer(buffer).bounds)
    footprints = check_antimeridean(footprint)
    latlon_pairs = []
    for footprint in footprints:
        latlon_pairs += get_latlon_pairs(footprint)
    urls = [get_dem_granule_url(lat, lon) for lat, lon in latlon_pairs]

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(lambda url: download_file(url, str(output_dir)), urls)

    vrt_filepath = output_dir / 'dem.vrt'
    input_files = [str(output_dir / Path(url).name) for url in urls]
    gdal.BuildVRT(str(output_dir / 'dem.vrt'), input_files)
    ds = gdal.Open(str(vrt_filepath), gdal.GA_ReadOnly)
    gdal.Translate(str(output_path), ds, format='GTiff')

    ds = None
    [Path(f).unlink() for f in input_files + [vrt_filepath]]
