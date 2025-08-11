import abc
import io
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from typing import List
import zipfile

import requests


class ElevationFileNotFoundError(Exception):
    def __init__(self, missing_files: List[str]):
        self.missing_files = missing_files


class IGetElevationFiles(metaclass=abc.ABCMeta):
    """Provide host-dependant path of elevation files."""

    @abc.abstractmethod
    def get_paths(self, files: List[str]) -> List[Path]:
        """May raise ElevationFileNotFound if a file cannot be found."""
        pass


class AssetsFolderProvider(IGetElevationFiles):
    """Provide elevation file location from a given assets folder."""

    def __init__(self, assets: Path):
        os.makedirs(assets, exist_ok=True)
        self.assets = assets

    def get_paths(self, files) -> List[Path]:
        """Raise ElevationFileNotFoundError if some files cannot be found."""

        paths = []
        missing_files = []

        for file in files:
            if os.path.exists(self.assets / file):
                paths.append(self.assets / file)
            else:
                missing_files.append(file)

        if len(missing_files) > 0:
            raise ElevationFileNotFoundError(missing_files)

        return paths


class NasaConnectionError(Exception):
    def __init__(self, error_code):
        self.error_code = error_code


class NasaConnection:
    def __init__(
        self,
        user: str,
        pwd: str,
        url: str,
    ):
        self.auth = (user, pwd)
        self.url = url
        self.session = requests.Session()
        self.session.auth = self.auth

    def __del__(self):
        self.session.close()

    def fetch(self, filename):
        """Snippet adapted from https://urs.earthdata.nasa.gov/documentation/for_users/data_access/python"""
        url = f"{self.url}/NASADEM_SHHP_{filename}/NASADEM_SHHP_{filename}.zip"
        r1 = self.session.request("get", url)
        r = self.session.get(r1.url, auth=self.session.auth)

        if not r.ok:
            raise NasaConnectionError(r.status_code)

        return r.content


class NasaProvider(IGetElevationFiles):
    """Look for elevation files in a folder and try to download missing files from
    NASA EarthData."""

    def __init__(self, assets: Path, connection: NasaConnection):
        os.makedirs(assets, exist_ok=True)
        self.assets = assets
        self.connection = connection

    def get_paths(self, files: List[str]) -> List[Path]:
        paths = []
        missing_files = []

        for file in files:
            if os.path.exists(self.assets / file):
                paths.append(self.assets / file)
            else:
                missing_files.append(file)

        files_in_error = []
        for file in missing_files:
            filename = file.removesuffix(".hgts")

            try:
                content = self.connection.fetch(filename)
                z = zipfile.ZipFile(io.BytesIO(content))
                with TemporaryDirectory() as tmpdir:
                    z.extractall(tmpdir)
                    shutil.move(Path(tmpdir) / file, self.assets / file)
                    paths.append(self.assets / file)
                    print(f"Downloaded elevation file {file}")
            except NasaConnectionError as exc:
                files_in_error.append(filename)
                print(
                    f"Error when trying to download {file}: response has {exc.error_code}"
                )

        if len(files_in_error) > 0:
            raise ElevationFileNotFoundError(files_in_error)

        return paths
