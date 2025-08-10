from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from gpx2mesh.elevation.sources import AssetsFolderProvider, ElevationFileNotFoundError


def test_empty_files_list_provided():
    with TemporaryDirectory() as tmp_dir:
        provider = AssetsFolderProvider(Path(tmp_dir))

        paths = provider.get_paths([])

        assert paths == []


def test_get_files_all_exists():
    with TemporaryDirectory() as tmp_dir:
        assets = Path(tmp_dir)
        provider = AssetsFolderProvider(assets)

        (assets / "toto.hgts").touch(exist_ok=True)
        (assets / "tutu.hgts").touch(exist_ok=True)

        paths = provider.get_paths(["toto.hgts", "tutu.hgts"])

        assert paths == [assets / "toto.hgts", assets / "tutu.hgts"]


def test_with_missing_files():
    with TemporaryDirectory() as tmp_dir:
        assets = Path(tmp_dir)
        provider = AssetsFolderProvider(assets)

        (assets / "toto.hgts").touch(exist_ok=True)

        with pytest.raises(ElevationFileNotFoundError) as e:
            provider.get_paths(["toto.hgts", "tutu.hgts"])

        assert e.value.missing_files == ["tutu.hgts"]
