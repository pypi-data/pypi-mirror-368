from gpx2mesh.elevation import get_filenames
from gpx2mesh.track import TrackBounds


def test_filename_mapping_single_file():
    assert get_filenames(
        TrackBounds(lat_min=45.2, lat_max=45.3, lon_min=4.2, lon_max=4.3)
    ) == ["n45e004.hgts"]

    assert get_filenames(
        TrackBounds(lat_min=-5.8, lat_max=-5.2, lon_min=-164.2, lon_max=-164.1)
    ) == ["s06w165.hgts"]

    assert get_filenames(
        TrackBounds(lat_min=0, lat_max=0.8, lon_min=0, lon_max=0.8)
    ) == ["n00e000.hgts"]


def test_filenames_mapping_multiple_files():
    assert get_filenames(
        TrackBounds(lat_min=45.2, lat_max=46.3, lon_min=4.7, lon_max=4.8)
    ) == [
        "n45e004.hgts",
        "n46e004.hgts",
    ]

    assert get_filenames(
        TrackBounds(lat_min=45.2, lat_max=45.3, lon_min=4.7, lon_max=5.8)
    ) == [
        "n45e004.hgts",
        "n45e005.hgts",
    ]

    assert get_filenames(
        TrackBounds(lat_min=45.2, lat_max=46.3, lon_min=4.7, lon_max=5.8)
    ) == [
        "n45e004.hgts",
        "n45e005.hgts",
        "n46e004.hgts",
        "n46e005.hgts",
    ]
