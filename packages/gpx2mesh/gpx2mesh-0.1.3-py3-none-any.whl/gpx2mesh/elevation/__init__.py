from itertools import product
from math import ceil, floor
from typing import List
import numpy as np
from scipy import ndimage
from scipy.ndimage import gaussian_filter

from gpx2mesh.track import TrackBounds
from gpx2mesh.elevation.sources import IGetElevationFiles

ELEVATION_NAN_VALUE = -32768


def get_filenames(bounds: TrackBounds) -> List[str]:
    return [
        _map_filename(lat, lon)
        for lat, lon in product(
            range(floor(bounds.lat_min), floor(bounds.lat_max + 1)),
            range(floor(bounds.lon_min), floor(bounds.lon_max + 1)),
        )
    ]


def _map_filename(lat: int, lon: int) -> str:
    _lat = f"{'n' if lat >= 0 else 's'}{abs(floor(lat)):>02}"
    _lon = f"{'e' if lon >= 0 else 'w'}{abs(floor(lon)):>03}"

    return _lat + _lon + ".hgts"


def load_elevation_map(
    track_bounds: TrackBounds, files_provider: IGetElevationFiles
) -> np.ndarray:
    """
    Load elevation values from file, interpolate missing values, and apply a gaussian filter.
    """
    files = get_filenames(track_bounds)
    paths = files_provider.get_paths(files)

    print(f"loading elevation from file {paths[0]}")
    size = 3601

    elev = np.fromfile(paths[0], dtype=">f4")
    elev = np.where(elev == ELEVATION_NAN_VALUE, np.nan, elev)
    elev = elev.reshape((size, size))

    nan_mask = np.isnan(elev)
    _, indices = ndimage.distance_transform_edt(nan_mask, return_indices=True)
    elev[nan_mask] = elev[tuple(indices[:, nan_mask])]

    elev = gaussian_filter(elev, sigma=3, radius=4)

    return elev


def crop_elevation_map(elevation: np.ndarray, track_bounds: TrackBounds):
    """
    Crop an elevation map to fit the track bounds. Returns the crop map together with
    the coordinate shift vector.
    """
    rows, cols = elevation.shape
    assert rows == cols
    size = rows

    width_c = (
        max(
            track_bounds.lon_max - track_bounds.lon_min,
            track_bounds.lat_max - track_bounds.lat_min,
        )
        * 1.2
    )

    mid_lat = (track_bounds.lat_max + track_bounds.lat_min) / 2
    cropped_lat_min = mid_lat - width_c / 2
    cropped_lat_max = mid_lat + width_c / 2
    row_min = floor((1 - (cropped_lat_max % 1)) * size)
    row_max = ceil((1 - (cropped_lat_min % 1)) * size)

    mid_lon = (track_bounds.lon_max + track_bounds.lon_min) / 2
    cropped_lon_min = mid_lon - width_c / 2
    cropped_lon_max = mid_lon + width_c / 2
    col_min = floor((cropped_lon_min % 1) * size)
    col_max = ceil((cropped_lon_max % 1) * size)

    print(row_min, row_max, col_min, col_max)

    cropped_elevation = elevation[
        row_min:row_max,
        col_min:col_max,
    ]
    shift_vector = [cropped_lon_min, cropped_lat_min]
    print(f"shift vector: {shift_vector}")
    return (cropped_elevation, shift_vector, width_c)
