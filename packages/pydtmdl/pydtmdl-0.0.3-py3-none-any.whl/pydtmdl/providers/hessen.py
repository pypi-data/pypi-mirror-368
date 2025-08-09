"""This module contains provider of Hessen data."""

from pydtmdl.base.dtm import DTMProvider
from pydtmdl.base.wcs import WCSProvider


class HessenProvider(WCSProvider, DTMProvider):
    """Provider of Hessen data."""

    _code = "hessen"
    _name = "Hessen DGM1"
    _region = "DE"
    _icon = "🇩🇪󠁥"
    _resolution = 1.0
    _extents = [(51.66698, 49.38533, 10.25780, 7.72773)]

    _url = "https://inspire-hessen.de/raster/dgm1/ows"
    _wcs_version = "2.0.1"
    _source_crs = "EPSG:25832"
    _tile_size = 1000

    def get_wcs_parameters(self, tile: tuple[float, float, float, float]) -> dict:
        return {
            "identifier": ["he_dgm1"],
            "subsets": [("N", str(tile[0]), str(tile[2])), ("E", str(tile[1]), str(tile[3]))],
            "format": "image/gtiff",
            "timeout": 600,
        }
