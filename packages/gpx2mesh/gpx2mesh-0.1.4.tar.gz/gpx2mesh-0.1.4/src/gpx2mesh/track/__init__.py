from collections import namedtuple
from typing import Tuple
import xml.etree.ElementTree as ET
import numpy as np


TrackBounds = namedtuple("TrackBounds", ["lat_min", "lat_max", "lon_min", "lon_max"])


class InvalidTrackFile(Exception):
    pass


def load_track(track_file: str) -> Tuple[np.ndarray, TrackBounds]:
    tree = ET.parse(track_file)
    root = tree.getroot()
    track = root.find("{*}trk")
    if track is None:
        print("No <trk> element in .gpx file")
        raise InvalidTrackFile

    segments = track.find("{*}trkseg")
    if segments is None:
        print("No <trkseg> element in .gpx file")
        raise InvalidTrackFile

    if len(segments) == 0:
        print("<trkseg> element is empty")
        raise InvalidTrackFile

    lat_min = float(segments[0].attrib["lat"])
    lat_max = float(segments[0].attrib["lat"])
    lon_min = float(segments[0].attrib["lon"])
    lon_max = float(segments[0].attrib["lon"])
    track = []

    for seg in segments:
        lat = float(seg.attrib["lat"])
        lon = float(seg.attrib["lon"])

        track.append((lon, lat))

        if lat < lat_min:
            lat_min = float(lat)
        if lat > lat_max:
            lat_max = float(lat)

        if lon < lon_min:
            lon_min = float(lon)
        if lon > lon_max:
            lon_max = float(lon)

    return np.array(track), TrackBounds(
        lat_min=lat_min, lat_max=lat_max, lon_min=lon_min, lon_max=lon_max
    )
