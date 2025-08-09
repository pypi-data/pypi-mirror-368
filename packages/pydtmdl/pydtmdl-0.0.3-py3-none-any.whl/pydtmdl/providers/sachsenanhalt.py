"""This module contains provider of Sachsen-Anhalt data."""

from pydtmdl.base.dtm import DTMProvider
from pydtmdl.base.wcs import WCSProvider


class SachsenAnhaltProvider(WCSProvider, DTMProvider):
    """Provider of Sachsen-Anhalt data."""

    _code = "sachsen-anhalt"
    _name = "Sachsen-Anhalt"
    _region = "DE"
    _icon = "🇩🇪"
    _resolution = 1.0
    _extents = [
        (53.0769416826493412, 50.8927195980075453, 13.3232545527125836, 10.5092298520646867)
    ]

    _url = "https://www.geodatenportal.sachsen-anhalt.de/wss/service/ST_LVermGeo_DGM1_WCS_OpenData/guest"  # pylint: disable=line-too-long
    _wcs_version = "1.0.0"
    _source_crs = "EPSG:4326"
    _tile_size = 0.02

    def get_wcs_parameters(self, tile: tuple[float, float, float, float]) -> dict:
        return {
            "identifier": "1",
            "bbox": tile,
            "format": "GeoTIFF",
            "crs": "EPSG:4326",
            "width": 1000,
            "height": 1000,
            "timeout": 600,
        }
