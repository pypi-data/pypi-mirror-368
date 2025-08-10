import argparse
from pathlib import Path
import re

from dotenv import dotenv_values

from gpx2mesh import build_mesh
from gpx2mesh.elevation.sources import NasaConnection, NasaProvider


def main():
    config = dotenv_values(".env")

    parser = argparse.ArgumentParser(
        prog="elevation", description="Generate elevation mesh from a .gpx file"
    )
    parser.add_argument("-f", "--file")
    parser.add_argument("-d", "--debug", default=False)

    args = parser.parse_args()

    nasa_connection = NasaConnection(
        user=config["LOGIN"], pwd=config["PWD"], url=config["URL_PREFIX"]
    )
    nasa_provider = NasaProvider(
        assets=Path(config["ASSETS"]), connection=nasa_connection
    )

    mesh = build_mesh(args.file, nasa_provider, debug=args.debug)

    export_file = re.sub(r"\.gpx$", ".stl", args.file)
    mesh.export(export_file)
    print(f"Mesh exported in {export_file}")


if __name__ == "__main__":
    main()
