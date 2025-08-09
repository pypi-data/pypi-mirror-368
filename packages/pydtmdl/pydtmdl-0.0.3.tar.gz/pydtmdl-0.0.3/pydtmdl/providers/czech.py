"""This module contains provider of Czech data."""

from pydtmdl.base.dtm import DTMProvider
from pydtmdl.base.wcs import WCSProvider


class CzechProvider(WCSProvider, DTMProvider):
    """Provider of Czech data."""

    _code = "czech"
    _name = "Czech Republic"
    _region = "CZ"
    _icon = "🇨🇿"
    _resolution = 5.0
    _extents = [
        (51.0576876059846754, 48.4917065572081754, 18.9775933665038821, 12.0428143585602161)
    ]

    _url = "https://ags.cuzk.cz/arcgis2/services/INSPIRE_Nadmorska_vyska/ImageServer/WCSServer"  # pylint: disable=line-too-long
    _wcs_version = "1.0.0"
    _source_crs = "EPSG:4326"
    _tile_size = 0.05

    def get_wcs_parameters(self, tile):
        return {
            "identifier": "MD_LAS",
            "crs": "EPSG:4326",
            "bbox": tile,
            "width": 1000,
            "height": 1000,
            "format": "GeoTIFF",
        }
