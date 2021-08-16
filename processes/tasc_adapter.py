from typing import Dict, Any

from gdalos.viewshed.viewshed_params import atmospheric_refraction_coeff, rf_refraction_coeff

from shapely.geometry import Polygon, mapping

# workaround ValueError: GEOSGeom_createLineString_r returned a NULL pointer
# https://stackoverflow.com/questions/62075847/using-qgis-and-shaply-error-geosgeom-createlinearring-r-returned-a-null-pointer
from shapely import speedups
speedups.disable()


def aoi_to_shapely(in_poly: list) -> Polygon:
    if in_poly[0] != in_poly[len(in_poly) - 1]:
        in_poly.append(in_poly[0])
    poly = Polygon([[p['lon'], p['lat']] for p in in_poly])
    return poly


def aoi_to_geojson(inputs: Dict[str, Any], name: str = 'aoi'):
    aoi = inputs.get(name, None)
    if not aoi:
        return None
    poly = aoi_to_shapely(aoi)
    return {"type": "complex", "mimeType": 'application/geo+json', "data": mapping(poly)}


def get_tasc_refraction(inputs: Dict[str, Any], name: str = 'isuserefraction'):
    is_refraction = inputs.get(name, False)
    return atmospheric_refraction_coeff if not is_refraction else rf_refraction_coeff

