from tempfile import NamedTemporaryFile

import pytest

from gpx2mesh.track import InvalidTrackFile, TrackBounds, load_track


def test_load_track():
    with NamedTemporaryFile("w", delete_on_close=False) as fp:
        fp.write("""<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.1" creator="local test" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
  <metadata>
    <name>Test track</name>
    <desc>Test track</desc>
    <time>2025-06-17T19:08:32+00:00</time>
  </metadata>
  <trk>
    <name>Test track</name>
    <src>Local</src>
    <trkseg>
      <trkpt lat="45.76154" lon="4.82598">
        <ele>172</ele>
        <time>2025-06-17T19:08:32+00:00</time>
      </trkpt>
      <trkpt lat="45.76154" lon="4.82598">
        <ele>172</ele>
        <time>2025-06-17T19:08:35+00:00</time>
      </trkpt>
      <trkpt lat="45.76181" lon="4.82615">
        <ele>174</ele>
        <time>2025-06-17T19:08:38+00:00</time>
      </trkpt>
      <trkpt lat="45.76195" lon="4.82611">
        <ele>174</ele>
        <time>2025-06-17T19:08:41+00:00</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>""")

        fp.close()

        (track, track_bounds) = load_track(fp.name)

        assert track_bounds == TrackBounds(
            lat_min=45.76154, lat_max=45.76195, lon_min=4.82598, lon_max=4.82615
        )

        assert len(track) == 4


def test_load_track_empty_trackseg():
    with NamedTemporaryFile("w", delete_on_close=False) as fp:
        fp.write("""<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.1" creator="local test" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
  <metadata>
    <name>Test track</name>
    <desc>Test track</desc>
    <time>2025-06-17T19:08:32+00:00</time>
  </metadata>
  <trk>
    <name>Test track</name>
    <src>Local</src>
    <trkseg>
    </trkseg>
  </trk>
</gpx>""")
        fp.close()

        with pytest.raises(InvalidTrackFile):
            load_track(fp.name)
