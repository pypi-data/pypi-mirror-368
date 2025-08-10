import io
from pathlib import Path
import struct
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock
import zipfile

import pytest


from gpx2mesh.elevation.sources import (
    ElevationFileNotFoundError,
    NasaConnection,
    NasaConnectionError,
    NasaProvider,
)


def zip_content(filename: str):
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr(filename, struct.pack(">f", 123.4))
        z.writestr("toto.err", struct.pack(">f", 567.8))

    return archive.getvalue()


def test_download_missing_files():
    mocked_connection = MagicMock(NasaConnection)
    mocked_connection.fetch.return_value = zip_content("toto.hgts")

    with TemporaryDirectory() as tmp_dir:
        provider = NasaProvider(Path(tmp_dir), mocked_connection)

        paths = provider.get_paths(["toto.hgts"])

        assert paths == [Path(tmp_dir) / "toto.hgts"]

        mocked_connection.fetch.assert_called_once_with("toto")


def test_does_not_download_existing_files():
    mocked_connection = MagicMock(NasaConnection)
    mocked_connection.fetch.return_value = zip_content("toto.hgts")

    with TemporaryDirectory() as tmp_dir:
        assets = Path(tmp_dir)
        provider = NasaProvider(assets, mocked_connection)
        (assets / "tutu.hgts").touch()

        paths = provider.get_paths(["toto.hgts", "tutu.hgts"])

        assert paths == [
            assets / "tutu.hgts",
            assets / "toto.hgts",
        ]

        mocked_connection.fetch.assert_called_once_with("toto")


def test_raises_exception_file_does_not_exists_on_remote():
    mocked_connection = MagicMock(NasaConnection)
    mocked_connection.fetch.side_effect = NasaConnectionError(error_code=404)

    with TemporaryDirectory() as tmp_dir:
        provider = NasaProvider(Path(tmp_dir), mocked_connection)

        with pytest.raises(ElevationFileNotFoundError) as exc_info:
            provider.get_paths(["toto.hgts"])

        assert exc_info.value.missing_files == ["toto"]

        mocked_connection.fetch.assert_called_once_with("toto")
